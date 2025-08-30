from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class Category(db.Model):
    __tablename__ = 'categories'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    active = db.Column(db.Boolean, default=True, nullable=False)
    created_at = db.Column(db.DateTime, nullable=False)
    updated_at = db.Column(db.DateTime, nullable=False)
    
    # 關聯到任務
    tasks = db.relationship('Task', backref='category', lazy=True)
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'active': self.active,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

class Task(db.Model):
    __tablename__ = 'tasks'
    
    id = db.Column(db.Integer, primary_key=True)
    case_number = db.Column(db.String(100), nullable=False)
    category_id = db.Column(db.Integer, db.ForeignKey('categories.id'), nullable=False)
    form_name = db.Column(db.String(200))
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    requester = db.Column(db.String(100))
    due_date = db.Column(db.Date)
    status = db.Column(db.String(20), default='pending')  # pending, in_progress, completed
    priority = db.Column(db.String(10), default='medium')  # low, medium, high
    created_at = db.Column(db.DateTime, nullable=False)
    updated_at = db.Column(db.DateTime, nullable=False)
    
    # 關聯到工作紀錄
    work_logs = db.relationship('WorkLog', backref='task', lazy=True)
    
    def to_dict(self):
        return {
            'id': self.id,
            'case_number': self.case_number,
            'category_id': self.category_id,
            'category_name': self.category.name if self.category else None,
            'form_name': self.form_name,
            'title': self.title,
            'description': self.description,
            'requester': self.requester,
            'due_date': self.due_date.isoformat() if self.due_date else None,
            'status': self.status,
            'priority': self.priority,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

class WorkLog(db.Model):
    __tablename__ = 'work_logs'
    
    id = db.Column(db.Integer, primary_key=True)
    task_id = db.Column(db.Integer, db.ForeignKey('tasks.id'), nullable=False)
    work_date = db.Column(db.Date, nullable=False)
    hours = db.Column(db.Float, nullable=False)
    description = db.Column(db.Text)
    completed = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, nullable=False)
    updated_at = db.Column(db.DateTime, nullable=False)
    
    def to_dict(self):
        return {
            'id': self.id,
            'task_id': self.task_id,
            'task': {
                'id': self.task.id if self.task else None,
                'case_number': self.task.case_number if self.task else None,
                'category_name': self.task.category.name if self.task and self.task.category else None,
                'title': self.task.title if self.task else None,
                'description': self.task.description if self.task else None,
                'status': self.task.status if self.task else None,
                'priority': self.task.priority if self.task else None
            } if self.task else None,
            'work_date': self.work_date.isoformat() if self.work_date else None,
            'hours': self.hours,
            'description': self.description,
            'completed': self.completed,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }