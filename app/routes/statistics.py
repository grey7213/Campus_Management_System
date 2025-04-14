from flask import Blueprint, render_template, redirect, url_for, flash, request, current_app
from flask_login import login_required, current_user
from app import db
from app.models.user import User, Role, Permission
from app.models.student import Student, Class, Major
from app.models.teacher import Teacher, Department
from app.models.course import Course
from app.utils.decorators import admin_required

statistics = Blueprint('statistics', __name__)

@statistics.route('/dashboard')
@login_required
@admin_required
def dashboard():
    """数据统计仪表盘"""
    # 获取基础数据
    student_count = Student.query.count()
    teacher_count = Teacher.query.count()
    course_count = Course.query.count()
    department_count = Department.query.count()
    class_count = Class.query.count()
    major_count = Major.query.count()
    
    return render_template('statistics/dashboard.html',
                          student_count=student_count,
                          teacher_count=teacher_count,
                          course_count=course_count,
                          department_count=department_count,
                          class_count=class_count,
                          major_count=major_count)

@statistics.route('/students')
@login_required
@admin_required
def students():
    """学生数据统计"""
    # 按专业统计学生人数
    students_by_major = db.session.query(Major.name, db.func.count(Student.id)).\
        join(Class, Major.id == Class.major_id).\
        join(Student, Class.id == Student.class_id).\
        group_by(Major.name).all()
    
    # 按性别统计学生人数
    students_by_gender = db.session.query(Student.gender, db.func.count(Student.id)).\
        group_by(Student.gender).all()
    
    return render_template('statistics/students.html',
                          students_by_major=students_by_major,
                          students_by_gender=students_by_gender)

@statistics.route('/teachers')
@login_required
@admin_required
def teachers():
    """教师数据统计"""
    # 按部门统计教师人数
    teachers_by_department = db.session.query(Department.name, db.func.count(Teacher.id)).\
        join(Teacher, Department.id == Teacher.department_id).\
        group_by(Department.name).all()
    
    return render_template('statistics/teachers.html',
                          teachers_by_department=teachers_by_department)

@statistics.route('/courses')
@login_required
@admin_required
def courses():
    """课程数据统计"""
    # 按学期统计课程数量
    courses_by_semester = db.session.query(Course.semester, db.func.count(Course.id)).\
        group_by(Course.semester).all()
    
    return render_template('statistics/courses.html',
                          courses_by_semester=courses_by_semester)

@statistics.route('/reports')
@login_required
@admin_required
def reports():
    """统计报表"""
    return render_template('statistics/reports.html')