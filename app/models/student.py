from datetime import datetime
from app import db
from app.models.major import Major  # 导入 Major 类

class Class(db.Model):
    """班级模型"""
    __tablename__ = 'classes'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True)
    code = db.Column(db.String(20), unique=True)  # 班级代码
    grade = db.Column(db.String(10))  # 年级，如2022级
    major_id = db.Column(db.Integer, db.ForeignKey('majors.id'))
    description = db.Column(db.Text())  # 班级描述
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # 关联
    students = db.relationship('Student', backref='class_', lazy='dynamic')
    
    def __repr__(self):
        return f'<Class {self.name}>'

class Student(db.Model):
    """学生模型"""
    __tablename__ = 'students'
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.String(20), unique=True, index=True)  # 学号
    name = db.Column(db.String(64))
    gender = db.Column(db.String(10))
    birthday = db.Column(db.Date)
    address = db.Column(db.String(128))
    phone = db.Column(db.String(20))
    email = db.Column(db.String(64))
    class_id = db.Column(db.Integer, db.ForeignKey('classes.id'))
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    status = db.Column(db.String(20), default='active')  # active, graduated, suspended
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # 关联
    enrollments = db.relationship('Enrollment', backref='student', lazy='dynamic')
    
    def __repr__(self):
        return f'<Student {self.name}>'