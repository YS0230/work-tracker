from flask import Flask, request, jsonify
from flask_cors import CORS
from models import db, Category, Task
from datetime import datetime, date
import os

app = Flask(__name__)

# 配置
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///work_tracker.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# 初始化
db.init_app(app)
CORS(app)

# 建立資料庫表格
with app.app_context():
    db.create_all()
    
    # 建立預設類別
    if Category.query.count() == 0:
        default_categories = [
            '客戶服務',
            '技術支援',
            '系統維修',
            '緊急處理',
            '一般諮詢',
            '主管交辦'
        ]
        
        for cat_name in default_categories:
            now = datetime.now()
            category = Category(
                name=cat_name,
                active=True,
                created_at=now,
                updated_at=now
            )
            db.session.add(category)
        
        db.session.commit()

# 類別 API
@app.route('/api/categories', methods=['GET'])
def get_categories():
    categories = Category.query.filter_by(active=True).all()
    return jsonify([cat.to_dict() for cat in categories])

@app.route('/api/categories', methods=['POST'])
def create_category():
    data = request.json
    now = datetime.now()
    
    category = Category(
        name=data['name'],
        active=True,
        created_at=now,
        updated_at=now
    )
    
    db.session.add(category)
    db.session.commit()
    
    return jsonify(category.to_dict()), 201

@app.route('/api/categories/<int:category_id>', methods=['PUT'])
def update_category(category_id):
    category = Category.query.get_or_404(category_id)
    data = request.json
    
    category.name = data.get('name', category.name)
    category.active = data.get('active', category.active)
    category.updated_at = datetime.now()
    
    db.session.commit()
    
    return jsonify(category.to_dict())

@app.route('/api/categories/<int:category_id>', methods=['DELETE'])
def delete_category(category_id):
    category = Category.query.get_or_404(category_id)
    category.active = False
    category.updated_at = datetime.now()
    
    db.session.commit()
    
    return jsonify({'message': 'Category deleted successfully'})

# 任務 API
@app.route('/api/tasks', methods=['GET'])
def get_tasks():
    query = Task.query
    
    # 處理查詢參數
    if request.args.get('case_number'):
        query = query.filter(Task.case_number.contains(request.args.get('case_number')))
    
    if request.args.get('category_id'):
        query = query.filter(Task.category_id == request.args.get('category_id'))
    
    if request.args.get('form_name'):
        query = query.filter(Task.form_name.contains(request.args.get('form_name')))
    
    if request.args.get('title'):
        query = query.filter(Task.title.contains(request.args.get('title')))
    
    if request.args.get('description'):
        query = query.filter(Task.description.contains(request.args.get('description')))
    
    if request.args.get('requester'):
        query = query.filter(Task.requester.contains(request.args.get('requester')))
    
    if request.args.get('status'):
        query = query.filter(Task.status == request.args.get('status'))
    
    if request.args.get('priority'):
        query = query.filter(Task.priority == request.args.get('priority'))
    
    # 處理截止日期範圍
    if request.args.get('due_date_start'):
        due_date_start = datetime.strptime(request.args.get('due_date_start'), '%Y-%m-%d').date()
        query = query.filter(Task.due_date >= due_date_start)
    
    if request.args.get('due_date_end'):
        due_date_end = datetime.strptime(request.args.get('due_date_end'), '%Y-%m-%d').date()
        query = query.filter(Task.due_date <= due_date_end)
    
    # 處理建立時間範圍
    if request.args.get('created_at_start'):
        created_at_start = datetime.strptime(request.args.get('created_at_start'), '%Y-%m-%d %H:%M:%S')
        query = query.filter(Task.created_at >= created_at_start)
    
    if request.args.get('created_at_end'):
        created_at_end = datetime.strptime(request.args.get('created_at_end'), '%Y-%m-%d %H:%M:%S')
        query = query.filter(Task.created_at <= created_at_end)
    
    # 處理異動時間範圍
    if request.args.get('updated_at_start'):
        updated_at_start = datetime.strptime(request.args.get('updated_at_start'), '%Y-%m-%d %H:%M:%S')
        query = query.filter(Task.updated_at >= updated_at_start)
    
    if request.args.get('updated_at_end'):
        updated_at_end = datetime.strptime(request.args.get('updated_at_end'), '%Y-%m-%d %H:%M:%S')
        query = query.filter(Task.updated_at <= updated_at_end)
    
    tasks = query.order_by(Task.created_at.desc()).all()
    return jsonify([task.to_dict() for task in tasks])

@app.route('/api/tasks', methods=['POST'])
def create_task():
    data = request.json
    now = datetime.now()
    
    # 解析日期
    due_date = None
    if data.get('due_date'):
        due_date = datetime.strptime(data['due_date'], '%Y-%m-%d').date()
    
    task = Task(
        case_number=data['case_number'],
        category_id=data['category_id'],
        form_name=data.get('form_name', ''),
        title=data['title'],
        description=data.get('description', ''),
        requester=data.get('requester', ''),
        due_date=due_date,
        status=data.get('status', 'pending'),
        priority=data.get('priority', 'medium'),
        created_at=now,
        updated_at=now
    )
    
    db.session.add(task)
    db.session.commit()
    
    return jsonify(task.to_dict()), 201

@app.route('/api/tasks/<int:task_id>', methods=['PUT'])
def update_task(task_id):
    task = Task.query.get_or_404(task_id)
    data = request.json
    
    # 更新欄位
    task.case_number = data.get('case_number', task.case_number)
    task.category_id = data.get('category_id', task.category_id)
    task.form_name = data.get('form_name', task.form_name)
    task.title = data.get('title', task.title)
    task.description = data.get('description', task.description)
    task.requester = data.get('requester', task.requester)
    task.status = data.get('status', task.status)
    task.priority = data.get('priority', task.priority)
    task.updated_at = datetime.now()
    
    # 解析日期
    if data.get('due_date'):
        task.due_date = datetime.strptime(data['due_date'], '%Y-%m-%d').date()
    
    db.session.commit()
    
    return jsonify(task.to_dict())

@app.route('/api/tasks/<int:task_id>', methods=['DELETE'])
def delete_task(task_id):
    task = Task.query.get_or_404(task_id)
    db.session.delete(task)
    db.session.commit()
    
    return jsonify({'message': 'Task deleted successfully'})

if __name__ == '__main__':
    app.run(debug=True)