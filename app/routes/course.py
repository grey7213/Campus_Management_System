from flask import Blueprint, render_template, redirect, url_for, flash, request, current_app
from flask_login import login_required, current_user
from app import db
from app.models.course import Course, Enrollment
from app.models.user import Permission
from app.utils.decorators import permission_required

course = Blueprint('course', __name__)

@course.route('/')
def index():
    """课程列表"""
    page = request.args.get('page', 1, type=int)
    pagination = Course.query.filter_by(status='active').paginate(
        page=page, per_page=current_app.config['ITEMS_PER_PAGE'], error_out=False)
    courses = pagination.items
    return render_template('course/index.html', courses=courses, pagination=pagination)

@course.route('/<int:id>')
def detail(id):
    """课程详情"""
    course = Course.query.get_or_404(id)
    return render_template('course/detail.html', course=course)

@course.route('/<int:id>/enroll', methods=['POST'])
@login_required
@permission_required(Permission.STUDENT)
def enroll(id):
    """选课"""
    course = Course.query.get_or_404(id)
    
    # 检查课程是否还有名额
    enrolled_count = Enrollment.query.filter_by(course_id=id, status='enrolled').count()
    if enrolled_count >= course.max_students:
        flash('该课程已满员', 'warning')
        return redirect(url_for('course.detail', id=id))
    
    # 检查学生是否已经选择了该课程
    if Enrollment.query.filter_by(student_id=current_user.student.id, course_id=id).first():
        flash('您已经选择了该课程', 'warning')
        return redirect(url_for('course.detail', id=id))
    
    # 创建选课记录
    enrollment = Enrollment(
        student_id=current_user.student.id,
        course_id=id,
        status='enrolled'
    )
    db.session.add(enrollment)
    db.session.commit()
    flash('选课成功', 'success')
    return redirect(url_for('student.courses')) 