from datetime import datetime
from app import db

class Department(db.Model):
    """部门模型"""
    __tablename__ = 'departments'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True)
    code = db.Column(db.String(20), unique=True)
    # Uncomment the contact field to fix the error
    contact = db.Column(db.String(100), nullable=True)
    description = db.Column(db.Text())
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # 关联
    teachers = db.relationship('Teacher', backref='department', lazy='dynamic')
    majors = db.relationship('Major', back_populates='department', lazy='dynamic')
    
    def __repr__(self):
        return f'<Department {self.name}>'

class Teacher(db.Model):
    """教师模型"""
    __tablename__ = 'teachers'
    id = db.Column(db.Integer, primary_key=True)
    teacher_id = db.Column(db.String(20), unique=True, index=True)  # 教师工号
    name = db.Column(db.String(64))
    gender = db.Column(db.String(10))
    birthday = db.Column(db.Date)
    address = db.Column(db.String(128))
    phone = db.Column(db.String(20))
    email = db.Column(db.String(64))
    title = db.Column(db.String(64))  # 职称
    bio = db.Column(db.Text)  # 教师简介
    department_id = db.Column(db.Integer, db.ForeignKey('departments.id'))
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    status = db.Column(db.String(20), default='active')  # active, leave, retired
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # 关联
    courses = db.relationship('Course', backref='teacher', lazy='dynamic')
    # 定义与 User 的关系，添加 backref，确保关系可以从 Teacher 反向查询到 User
    user = db.relationship('User', backref='teacher_info', foreign_keys=[user_id], uselist=False)
    
    def __repr__(self):
        return f'<Teacher {self.name}>'