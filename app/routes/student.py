from flask import Blueprint, render_template, redirect, url_for, flash, request, current_app, abort, jsonify, send_file
from flask_login import login_required, current_user
from app import db
from app.models.user import User, Permission
from app.models.student import Student, Class, Major
from app.models.course import Course, Enrollment
from app.utils.decorators import permission_required, student_required
from app.models.literacy import LiteracyCertificate
from app.forms.literacy import CertificateApplicationForm
from app.utils.file_utils import save_uploaded_file
from app.services.blockchain_certificate_service import BlockchainCertificateService
import os
from datetime import datetime

student = Blueprint('student', __name__)

@student.route('/')
@login_required
def index():
    """学生首页"""
    return render_template('student/index.html', active_menu='dashboard')

@student.route('/dashboard')
@login_required
@student_required
def dashboard():
    """学生控制面板"""
    # 获取学生信息
    student_info = None
    if current_user.student:
        student_info = current_user.student
    
    # 获取学生的选课信息
    enrollments = []
    if student_info:
        enrollments = Enrollment.query.filter_by(student_id=student_info.id, status='enrolled').all()
    
    return render_template('student/dashboard.html', 
                           student=student_info, 
                           enrollments=enrollments)

@student.route('/profile', methods=['GET', 'POST'])
@login_required
@student_required
def profile():
    """学生个人信息"""
    student_info = None
    if current_user.student:
        student_info = current_user.student
    
    # 这里应该添加一个表单来编辑学生信息
    # 暂时只显示信息
    return render_template('student/profile.html', student=student_info)

@student.route('/courses')
@login_required
@student_required
def courses():
    """可选课程列表"""
    page = request.args.get('page', 1, type=int)
    pagination = Course.query.filter_by(status='active').paginate(
        page=page, per_page=current_app.config['ITEMS_PER_PAGE'], error_out=False)
    courses = pagination.items
    
    # 获取学生已选课程ID列表，用于前端显示是否已选
    enrolled_course_ids = []
    if current_user.student:
        enrollments = Enrollment.query.filter_by(student_id=current_user.student.id).all()
        enrolled_course_ids = [e.course_id for e in enrollments]
    
    return render_template('student/courses.html', 
                           courses=courses, 
                           pagination=pagination,
                           enrolled_course_ids=enrolled_course_ids)

@student.route('/courses/<int:id>/enroll', methods=['POST'])
@login_required
@student_required
def enroll_course(id):
    """选课"""
    if not current_user.student:
        flash('您需要先完善学生信息', 'warning')
        return redirect(url_for('student.profile'))
    
    course = Course.query.get_or_404(id)
    
    # 检查课程是否可选
    if course.status != 'active':
        flash('该课程不可选', 'danger')
        return redirect(url_for('student.courses'))
    
    # 检查是否已选
    existing = Enrollment.query.filter_by(
        student_id=current_user.student.id,
        course_id=id
    ).first()
    
    if existing:
        flash('您已经选择了该课程', 'warning')
        return redirect(url_for('student.courses'))
    
    # 检查课程人数是否已满
    current_count = Enrollment.query.filter_by(course_id=id, status='enrolled').count()
    if current_count >= course.max_students:
        flash('该课程人数已满', 'danger')
        return redirect(url_for('student.courses'))
    
    # 创建选课记录
    enrollment = Enrollment(
        student_id=current_user.student.id,
        course_id=id,
        status='enrolled'
    )
    db.session.add(enrollment)
    db.session.commit()
    
    flash(f'成功选择课程: {course.name}', 'success')
    return redirect(url_for('student.my_courses'))

@student.route('/my-courses')
@login_required
@student_required
def my_courses():
    """我的课程"""
    if not current_user.student:
        flash('您需要先完善学生信息', 'warning')
        return redirect(url_for('student.profile'))
    
    enrollments = Enrollment.query.filter_by(
        student_id=current_user.student.id,
        status='enrolled'
    ).all()
    
    return render_template('student/my_courses.html', enrollments=enrollments)

@student.route('/courses/<int:id>/drop', methods=['POST'])
@login_required
@student_required
def drop_course(id):
    """退课"""
    if not current_user.student:
        flash('您需要先完善学生信息', 'warning')
        return redirect(url_for('student.profile'))
    
    enrollment = Enrollment.query.filter_by(
        student_id=current_user.student.id,
        course_id=id,
        status='enrolled'
    ).first_or_404()
    
    enrollment.status = 'dropped'
    db.session.commit()
    
    course = Course.query.get(id)
    flash(f'已退选课程: {course.name}', 'success')
    return redirect(url_for('student.my_courses'))

@student.route('/grades')
@login_required
@student_required
def grades():
    """成绩查询"""
    if not current_user.student:
        flash('您需要先完善学生信息', 'warning')
        return redirect(url_for('student.profile'))
    
    # 获取所有有成绩的选课记录
    enrollments = Enrollment.query.filter(
        Enrollment.student_id == current_user.student.id,
        Enrollment.grade.isnot(None)
    ).all()
    
    return render_template('student/grades.html', enrollments=enrollments)

@student.route('/test')
def test():
    """测试endpoint"""
    return "测试成功！系统正常运行！"

@student.route('/literacy_certificates')
@login_required
def literacy_certificates():
    """显示学生的素养证书列表"""
    # 查询当前学生的所有证书
    certificates = []  # 这里应该查询数据库获取证书列表
    return render_template('student/literacy_certificates.html', 
                           certificates=certificates, 
                           active_menu='literacy_certificates')

@student.route('/apply_certificate', methods=['GET', 'POST'])
@login_required
def apply_certificate():
    """申请新证书"""
    form = CertificateApplicationForm()
    
    if form.validate_on_submit():
        # 创建新证书记录
        certificate = LiteracyCertificate(
            name=form.name.data,
            certificate_type=form.certificate_type.data,
            issue_date=form.issue_date.data,
            expiry_date=form.expiry_date.data,
            issuer=form.issuer.data,
            description=form.description.data,
            status='pending',
            user_id=current_user.id
        )
        
        # 处理上传的证明文件
        if form.proof_file.data:
            file_path = save_uploaded_file(
                form.proof_file.data, 
                'proof_files',
                f'certificate_{datetime.now().strftime("%Y%m%d%H%M%S")}'
            )
            certificate.proof_file = file_path
        
        db.session.add(certificate)
        db.session.commit()
        
        flash('证书申请已成功提交，等待审核。', 'success')
        return redirect(url_for('student.literacy_certificates'))
    
    return render_template('student/apply_certificate.html', 
                           form=form,
                           active_menu='literacy_certificates')

@student.route('/view_certificate/<int:id>')
@login_required
def view_certificate(id):
    """查看证书详情"""
    # 查询证书，并确保属于当前用户
    certificate = LiteracyCertificate.query.filter_by(
        id=id,
        user_id=current_user.id
    ).first_or_404()
    
    return render_template('student/view_certificate.html', certificate=certificate)