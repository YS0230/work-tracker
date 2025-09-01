from flask import Flask, request, jsonify, send_from_directory, render_template_string
from flask_cors import CORS
from models import db, Category, Task, WorkLog
from datetime import datetime, date
from functools import wraps
import os
import jwt
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__, static_folder='static', static_url_path='/static')

# 配置
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///work_tracker.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET_KEY', 'your_secret_key_here')
app.config['JWT_ALGORITHM'] = os.getenv('JWT_ALGORITHM', 'HS256')
app.config['ADMIN_ACCOUNT'] = os.getenv('ADMIN_ACCOUNT', 'admin')
app.config['ADMIN_PASSWORD'] = os.getenv('ADMIN_PASSWORD', 'password')

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

# JWT 認證裝飾器
def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        
        # 從 Authorization header 取得 token
        if 'Authorization' in request.headers:
            auth_header = request.headers['Authorization']
            if auth_header.startswith('Bearer '):
                token = auth_header.split(' ')[1]
        
        if not token:
            return jsonify({'error': '缺少認證令牌', 'code': 'NO_TOKEN'}), 401
        
        try:
            # 驗證 token (無過期時間限制)
            data = jwt.decode(token, app.config['JWT_SECRET_KEY'], algorithms=[app.config['JWT_ALGORITHM']])
        except jwt.InvalidTokenError:
            return jsonify({'error': '無效的認證令牌', 'code': 'INVALID_TOKEN'}), 401
        
        return f(*args, **kwargs)
    
    return decorated

# 登入 API
@app.route('/api/auth/login', methods=['POST'])
def login():
    try:
        data = request.json
        username = data.get('username')
        password = data.get('password')
        
        if not username or not password:
            return jsonify({'error': '請提供帳號和密碼'}), 400
        
        # 驗證帳密
        if username == app.config['ADMIN_ACCOUNT'] and password == app.config['ADMIN_PASSWORD']:
            # 生成 token (無過期時間)
            token = jwt.encode(
                {'username': username}, 
                app.config['JWT_SECRET_KEY'], 
                algorithm=app.config['JWT_ALGORITHM']
            )
            
            return jsonify({'token': token, 'message': '登入成功'}), 200
        else:
            return jsonify({'error': '帳號或密碼錯誤'}), 401
    
    except Exception as e:
        return jsonify({'error': '登入失敗'}), 500

# 類別 API
@app.route('/api/categories', methods=['GET'])
def get_categories():
    # 如果有 include_inactive 參數，則返回所有類別，否則只返回啟用的類別
    include_inactive = request.args.get('include_inactive', 'false').lower() == 'true'
    
    if include_inactive:
        categories = Category.query.all()
    else:
        categories = Category.query.filter_by(active=True).all()
    
    return jsonify([cat.to_dict() for cat in categories])

@app.route('/api/categories', methods=['POST'])
@token_required
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
@token_required
def update_category(category_id):
    category = Category.query.get_or_404(category_id)
    data = request.json
    
    category.name = data.get('name', category.name)
    category.active = data.get('active', category.active)
    category.updated_at = datetime.now()
    
    db.session.commit()
    
    return jsonify(category.to_dict())

@app.route('/api/categories/<int:category_id>', methods=['DELETE'])
@token_required
def delete_category(category_id):
    category = Category.query.get_or_404(category_id)
    
    # 檢查是否有任務使用此類別
    existing_tasks = Task.query.filter_by(category_id=category_id).count()
    if existing_tasks > 0:
        return jsonify({'error': f'無法刪除類別，還有 {existing_tasks} 個任務正在使用此類別'}), 400
    
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
        status_param = request.args.get('status')
        if ',' in status_param:
            status_list = [s.strip() for s in status_param.split(',')]
            query = query.filter(Task.status.in_(status_list))
        else:
            query = query.filter(Task.status == status_param)
    
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
@token_required
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
@token_required
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
@token_required
def delete_task(task_id):
    task = Task.query.get_or_404(task_id)
    
    # 檢查是否有工作紀錄使用此任務
    existing_work_logs = WorkLog.query.filter_by(task_id=task_id).count()
    if existing_work_logs > 0:
        return jsonify({'error': f'無法刪除任務，還有 {existing_work_logs} 筆工作紀錄正在使用此任務'}), 400
    
    db.session.delete(task)
    db.session.commit()
    
    return jsonify({'message': 'Task deleted successfully'})

# 工作紀錄 API
@app.route('/api/work-logs', methods=['GET'])
def get_work_logs():
    # 使用 join 預先載入任務和類別資訊，避免 N+1 查詢問題
    query = WorkLog.query.join(Task).join(Category)
    
    # 處理查詢參數
    if request.args.get('work_date'):
        work_date = datetime.strptime(request.args.get('work_date'), '%Y-%m-%d').date()
        query = query.filter(WorkLog.work_date == work_date)
    
    # 處理工作日期範圍
    if request.args.get('start_date'):
        work_date_start = datetime.strptime(request.args.get('start_date'), '%Y-%m-%d').date()
        query = query.filter(WorkLog.work_date >= work_date_start)
    
    if request.args.get('end_date'):
        work_date_end = datetime.strptime(request.args.get('end_date'), '%Y-%m-%d').date()
        query = query.filter(WorkLog.work_date <= work_date_end)
    
    if request.args.get('task_id'):
        query = query.filter(WorkLog.task_id == request.args.get('task_id'))
    
    work_logs = query.order_by(WorkLog.work_date.desc()).all()
    return jsonify([log.to_dict() for log in work_logs])

@app.route('/api/work-logs', methods=['POST'])
@token_required
def create_work_log():
    data = request.json
    now = datetime.now()
    
    # 解析日期
    work_date = datetime.strptime(data['work_date'], '%Y-%m-%d').date()
    
    work_log = WorkLog(
        task_id=data['task_id'],
        work_date=work_date,
        hours=data['hours'],
        description=data.get('description', ''),
        completed=data.get('completed', False),
        created_at=now,
        updated_at=now
    )
    
    db.session.add(work_log)
    
    # 如果標記為完成，更新任務狀態
    if data.get('completed', False):
        task = Task.query.get_or_404(data['task_id'])
        task.status = 'completed'
        task.updated_at = now
    
    db.session.commit()
    
    return jsonify(work_log.to_dict()), 201

@app.route('/api/work-logs/<int:log_id>', methods=['PUT'])
@token_required
def update_work_log(log_id):
    work_log = WorkLog.query.get_or_404(log_id)
    data = request.json
    now = datetime.now()
    
    # 儲存原始完成狀態
    original_completed = work_log.completed
    
    # 更新欄位
    if data.get('work_date'):
        work_log.work_date = datetime.strptime(data['work_date'], '%Y-%m-%d').date()
    
    work_log.hours = data.get('hours', work_log.hours)
    work_log.description = data.get('description', work_log.description)
    work_log.completed = data.get('completed', work_log.completed)
    work_log.updated_at = now
    
    # 如果完成狀態發生變化，更新任務狀態
    if not original_completed and work_log.completed:
        # 從未完成變為完成
        task = Task.query.get_or_404(work_log.task_id)
        task.status = 'completed'
        task.updated_at = now
    elif original_completed and not work_log.completed:
        # 從完成變為未完成，將任務狀態改為進行中
        task = Task.query.get_or_404(work_log.task_id)
        task.status = 'in_progress'
        task.updated_at = now
    
    db.session.commit()
    
    return jsonify(work_log.to_dict())

@app.route('/api/work-logs/<int:log_id>', methods=['DELETE'])
@token_required
def delete_work_log(log_id):
    work_log = WorkLog.query.get_or_404(log_id)
    db.session.delete(work_log)
    db.session.commit()
    
    return jsonify({'message': 'Work log deleted successfully'})

# 取得未完成的任務（用於工作紀錄選擇）
@app.route('/api/tasks/incomplete', methods=['GET'])
def get_incomplete_tasks():
    tasks = Task.query.filter(Task.status.in_(['pending', 'in_progress'])).order_by(Task.created_at.desc()).all()
    return jsonify([task.to_dict() for task in tasks])

# 服務前端靜態檔案
@app.route('/')
def serve_frontend():
    return send_from_directory(app.static_folder, 'index.html')

@app.route('/<path:path>')
def serve_static_files(path):
    try:
        return send_from_directory(app.static_folder, path)
    except:
        # 如果找不到靜態檔案，返回 index.html（用於 Vue Router）
        return send_from_directory(app.static_folder, 'index.html')

if __name__ == '__main__':
    app.run(debug=True)