from flask import Blueprint, render_template, redirect, url_for, flash, request, current_app
from flask_login import login_required, current_user
from app import db
from app.models.user import User, Permission
from app.models.teacher import Teacher
from app.models.course import Course, Enrollment
from app.utils.decorators import permission_required
from app.forms.teacher import CourseForm, GradeForm

teacher = Blueprint('teacher', __name__)

@teacher.route('/dashboard')
@login_required
@permission_required(Permission.TEACHER)
def dashboard():
    """教师控制面板"""
    # 获取教师信息
    teacher_info = None
    if current_user.teacher:
        teacher_info = current_user.teacher
    
    # 获取教师的课程
    courses = []
    if teacher_info:
        courses = Course.query.filter_by(teacher_id=teacher_info.id).all()
    
    return render_template('teacher/dashboard.html', 
                           teacher=teacher_info, 
                           courses=courses)

@teacher.route('/courses')
@login_required
@permission_required(Permission.TEACHER)
def courses():
    """教师课程列表"""
    page = request.args.get('page', 1, type=int)
    
    # 获取教师信息
    teacher_info = None
    if current_user.teacher:
        teacher_info = current_user.teacher
        pagination = Course.query.filter_by(teacher_id=teacher_info.id).paginate(
            page=page, per_page=current_app.config['ITEMS_PER_PAGE'], error_out=False)
        courses = pagination.items
    else:
        pagination = None
        courses = []
    
    return render_template('teacher/courses.html', 
                           teacher=teacher_info, 
                           courses=courses, 
                           pagination=pagination)

@teacher.route('/courses/create', methods=['GET', 'POST'])
@login_required
@permission_required(Permission.TEACHER)
def create_course():
    """创建课程"""
    if not current_user.teacher:
        flash('您需要先完善教师信息', 'warning')
        return redirect(url_for('teacher.profile'))
    
    form = CourseForm()
    if form.validate_on_submit():
        course = Course(
            code=form.code.data,
            name=form.name.data,
            description=form.description.data,
            credits=form.credits.data,
            hours=form.hours.data,
            semester=form.semester.data,
            teacher_id=current_user.teacher.id,
            max_students=form.max_students.data,
            status=form.status.data
        )
        db.session.add(course)
        db.session.commit()
        flash('课程创建成功', 'success')
        return redirect(url_for('teacher.courses'))
    
    return render_template('teacher/create_course.html', form=form)

@teacher.route('/courses/<int:id>/edit', methods=['GET', 'POST'])
@login_required
@permission_required(Permission.TEACHER)
def edit_course(id):
    """编辑课程"""
    course = Course.query.get_or_404(id)
    
    # 检查是否是课程的教师
    if not current_user.teacher or current_user.teacher.id != course.teacher_id:
        abort(403)
    
    form = CourseForm(obj=course)
    if form.validate_on_submit():
        course.code = form.code.data
        course.name = form.name.data
        course.description = form.description.data
        course.credits = form.credits.data
        course.hours = form.hours.data
        course.semester = form.semester.data
        course.max_students = form.max_students.data
        course.status = form.status.data
        db.session.commit()
        flash('课程更新成功', 'success')
        return redirect(url_for('teacher.courses'))
    
    return render_template('teacher/edit_course.html', form=form, course=course)

@teacher.route('/courses/<int:id>/students')
@login_required
@permission_required(Permission.TEACHER)
def course_students(id):
    """查看课程学生"""
    course = Course.query.get_or_404(id)
    
    # 检查是否是课程的教师
    if not current_user.teacher or current_user.teacher.id != course.teacher_id:
        abort(403)
    
    enrollments = Enrollment.query.filter_by(course_id=id, status='enrolled').all()
    
    return render_template('teacher/course_students.html', 
                           course=course, 
                           enrollments=enrollments)