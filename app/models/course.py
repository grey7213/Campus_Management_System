from datetime import datetime
from app import db

class Course(db.Model):
    """课程模型"""
    __tablename__ = 'courses'
    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(20), unique=True, index=True)  # 课程代码
    name = db.Column(db.String(64))
    description = db.Column(db.Text())
    credits = db.Column(db.Float)  # 学分
    hours = db.Column(db.Integer)  # 课时
    semester = db.Column(db.String(20))  # 学期，如2023-2024-1
    teacher_id = db.Column(db.Integer, db.ForeignKey('teachers.id'))
    max_students = db.Column(db.Integer, default=100)  # 最大学生数
    status = db.Column(db.String(20), default='active')  # active, inactive
    course_type = db.Column(db.String(20), default='required')  # required, elective, optional
    capacity = db.Column(db.Integer, default=50)  # 容量，用于代替max_students，保持兼容性
    location = db.Column(db.String(100))  # 上课地点
    schedule = db.Column(db.String(200))  # 上课时间
    prerequisites = db.Column(db.String(200))  # 先修课程要求
    allow_selection = db.Column(db.String(10), default='yes')  # 是否允许选课：yes, no
    target_grade = db.Column(db.String(20))  # 目标年级
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # 关联
    enrollments = db.relationship('Enrollment', backref='course', lazy='dynamic')
    
    def __repr__(self):
        return f'<Course {self.name}>'

class Enrollment(db.Model):
    """选课模型"""
    __tablename__ = 'enrollments'
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('students.id'))
    course_id = db.Column(db.Integer, db.ForeignKey('courses.id'))
    status = db.Column(db.String(20), default='enrolled')  # enrolled, dropped, completed
    grade = db.Column(db.Float)  # 成绩
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f'<Enrollment {self.student_id}-{self.course_id}>'