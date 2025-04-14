from flask import Blueprint, render_template, redirect, url_for, flash, request, current_app, jsonify, abort, send_file
from flask_login import login_required, current_user
from app import db
from app.models.user import User, Role, Permission
from app.models.student import Student, Class, Major
from app.models.teacher import Teacher, Department
from app.models.course import Course, Enrollment
from app.models.system import SystemSetting, SystemSettingService
from app.utils.decorators import admin_required
from app.forms.admin import UserForm, DepartmentForm, MajorForm, ClassForm
from app.forms.student import StudentForm
from app.forms.course import CourseForm, EnrollmentForm
from datetime import datetime, timedelta
from sqlalchemy import func
import os
from werkzeug.utils import secure_filename
import io

admin = Blueprint('admin', __name__)

@admin.route('/')
@login_required
@admin_required
def index():
    """管理员默认页面，重定向到仪表盘"""
    return redirect(url_for('admin.new_dashboard'))

@admin.route('/dashboard')
@login_required
@admin_required
def dashboard():
    """管理员控制面板"""
    # 统计数据 - 使用更大的假数据
    student_count = 2536  # 假设有2536名学生
    teacher_count = 186   # 假设有186名教师
    course_count = 324    # 假设有324门课程
    class_count = 68      # 假设有68个班级
    
    return render_template('admin/dashboard.html', 
                           student_count=student_count,
                           teacher_count=teacher_count,
                           course_count=course_count,
                           class_count=class_count)

@admin.route('/new_dashboard')
@login_required
@admin_required
def new_dashboard():
    """新版管理员控制面板"""
    # 统计数据 - 使用更大的假数据
    student_count = 2536  # 假设有2536名学生
    teacher_count = 186   # 假设有186名教师
    course_count = 324    # 假设有324门课程
    class_count = 68      # 假设有68个班级
    
    return render_template('admin/new_dashboard.html', 
                           student_count=student_count,
                           teacher_count=teacher_count,
                           course_count=course_count,
                           class_count=class_count)

# 学生管理
@admin.route('/students')
@login_required
@admin_required
def students():
    """学生列表"""
    page = request.args.get('page', 1, type=int)
    query = Student.query
    
    # 搜索和过滤
    search = request.args.get('q', '')
    if search:
        query = query.filter(Student.name.contains(search) | 
                            Student.student_id.contains(search))
    
    class_id = request.args.get('class_id', '')
    if class_id and class_id.isdigit():
        query = query.filter_by(class_id=int(class_id))
    
    status = request.args.get('status', '')
    if status:
        query = query.filter_by(status=status)
    
    # 分页
    pagination = query.order_by(Student.created_at.desc()).paginate(
        page=page, per_page=current_app.config['ITEMS_PER_PAGE'], error_out=False)
    students = pagination.items
    
    # 获取所有班级供过滤使用
    classes = Class.query.all()
    
    return render_template('admin/students.html', 
                           students=students, 
                           pagination=pagination,
                           classes=classes)

@admin.route('/students/new')
@login_required
@admin_required
def students_new():
    """新版学生列表"""
    page = request.args.get('page', 1, type=int)
    query = Student.query
    
    # 搜索和过滤
    search = request.args.get('q', '')
    if search:
        query = query.filter(Student.name.contains(search) | 
                            Student.student_id.contains(search))
    
    class_id = request.args.get('class_id', '')
    if class_id and class_id.isdigit():
        query = query.filter_by(class_id=int(class_id))
    
    status = request.args.get('status', '')
    if status:
        query = query.filter_by(status=status)
    
    # 分页
    pagination = query.order_by(Student.created_at.desc()).paginate(
        page=page, per_page=current_app.config['ITEMS_PER_PAGE'], error_out=False)
    students = pagination.items
    
    # 获取所有班级供过滤使用
    classes = Class.query.all()
    
    # 额外统计数据
    active_count = Student.query.filter_by(status='active').count()
    
    # 今日新增
    today = datetime.now().date()
    new_today = Student.query.filter(
        db.func.date(Student.created_at) == today
    ).count()
    
    return render_template('admin/students_new.html', 
                           students=students, 
                           pagination=pagination,
                           classes=classes,
                           active_count=active_count,
                           new_today=new_today)

@admin.route('/students/create', methods=['GET', 'POST'])
@login_required
@admin_required
def create_student():
    """创建学生"""
    form = StudentForm()
    
    # 获取所有有效的班级
    classes = Class.query.join(Major).filter(Class.major_id == Major.id).all()
    if not classes:
        flash('请先创建班级和专业', 'warning')
        return redirect(url_for('admin.classes'))
        
    form.class_id.choices = [(c.id, f"{c.name} ({c.major.name})") for c in classes]
    
    if form.validate_on_submit():
        try:
            # 先创建用户账号
            user = User(
                username=form.student_id.data,
                email=form.email.data,
                name=form.name.data,
                phone=form.phone.data,
                password=form.password.data,
                role_id=Role.query.filter_by(name='Student').first().id,
                is_active=True
            )
            db.session.add(user)
            db.session.flush()  # 获取用户ID
            
            # 创建学生记录
            student = Student(
                student_id=form.student_id.data,
                name=form.name.data,
                gender=form.gender.data,
                birthday=form.birthday.data,
                address=form.address.data,
                phone=form.phone.data,
                status=form.status.data,
                bio=form.bio.data,
                class_id=form.class_id.data,
                user_id=user.id
            )
            db.session.add(student)
            db.session.commit()
            
            flash('学生创建成功', 'success')
            return redirect(url_for('admin.students_new'))
            
        except Exception as e:
            db.session.rollback()
            flash(f'创建学生失败: {str(e)}', 'error')
            return render_template('admin/create_student.html', form=form)
    
    return render_template('admin/create_student.html', form=form)

@admin.route('/students/<int:id>/edit', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_student(id):
    """编辑学生"""
    student = Student.query.get_or_404(id)
    form = StudentForm(obj=student)
    form.class_id.choices = [(c.id, f"{c.name} ({c.major.name})") for c in Class.query.all()]
    
    if request.method == 'GET':
        # 如果学生已关联用户，填充关联用户的邮箱
        if student.user:
            form.email.data = student.user.email
    
    if form.validate_on_submit():
        # 更新学生记录
        student.student_id = form.student_id.data
        student.name = form.name.data
        student.gender = form.gender.data
        student.birthday = form.birthday.data
        student.address = form.address.data
        student.phone = form.phone.data
        student.status = form.status.data
        student.bio = form.bio.data
        student.class_id = form.class_id.data
        
        # 更新关联的用户
        if student.user:
            student.user.email = form.email.data
            student.user.name = form.name.data
            student.user.phone = form.phone.data
            if form.password.data:
                student.user.password = form.password.data
        
        db.session.commit()
        flash('学生信息更新成功', 'success')
        return redirect(url_for('admin.students'))
    
    return render_template('admin/edit_student.html', form=form, student=student)

@admin.route('/students/<int:id>', methods=['GET'])
@login_required
@admin_required
def view_student(id):
    """查看学生详情"""
    student = Student.query.get_or_404(id)
    enrollments = student.enrollments.all()
    
    # 计算已完成课程和已获学分
    completed_courses = sum(1 for e in enrollments if e.status == 'completed')
    total_credits = sum(e.course.credits for e in enrollments if e.status == 'completed')
    
    return render_template('admin/view_student.html', 
                           student=student, 
                           enrollments=enrollments,
                           completed_courses=completed_courses,
                           total_credits=total_credits)

@admin.route('/students/<int:id>/delete', methods=['POST'])
@login_required
@admin_required
def delete_student(id):
    """删除学生"""
    student = Student.query.get_or_404(id)
    user = student.user
    
    # 删除学生记录
    db.session.delete(student)
    
    # 如果有关联用户，也删除用户
    if user:
        db.session.delete(user)
    
    db.session.commit()
    flash('学生删除成功', 'success')
    return redirect(url_for('admin.students'))

@admin.route('/students/import', methods=['GET', 'POST'])
@login_required
@admin_required
def import_students():
    """导入学生"""
    if request.method == 'POST':
        # 检查是否有文件上传
        if 'file' not in request.files:
            flash('没有选择文件', 'danger')
            return redirect(request.url)
            
        file = request.files['file']
        if file.filename == '':
            flash('没有选择文件', 'danger')
            return redirect(request.url)
            
        if file and allowed_file(file.filename):
            try:
                # 获取处理选项
                skip_header = request.form.get('skip_header', 'off') == 'on'
                duplicate_handling = request.form.get('duplicate_handling', 'update')
                auto_create_class = request.form.get('auto_create_class', 'off') == 'on'
                
                # 保存文件
                filename = secure_filename(file.filename)
                file_path = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
                file.save(file_path)
                
                # 处理Excel文件
                from app.utils.excel import process_student_import
                success_count, error_records = process_student_import(
                    file_path, 
                    skip_header=skip_header,
                    duplicate_handling=duplicate_handling,
                    auto_create_class=auto_create_class
                )
                
                # 删除临时文件
                os.remove(file_path)
                
                if error_records:
                    flash(f'导入完成。成功：{success_count}条，失败：{len(error_records)}条。', 'warning')
                    return render_template('admin/import_result.html',
                                        success_count=success_count,
                                        error_records=error_records)
                else:
                    flash(f'导入成功，共导入{success_count}条记录。', 'success')
                    return redirect(url_for('admin.students'))
                    
            except Exception as e:
                flash(f'导入失败：{str(e)}', 'danger')
                return redirect(request.url)
        else:
            flash('不支持的文件格式', 'danger')
            return redirect(request.url)
            
    return render_template('admin/import_students.html')

@admin.route('/students/download_template')
@login_required
@admin_required
def download_student_template():
    """下载学生导入模板"""
    from app.utils.excel import create_student_import_template
    import io
    
    # 创建模板
    wb = create_student_import_template()
    
    # 将Excel写入内存中的字节流
    excel_file = io.BytesIO()
    wb.save(excel_file)
    excel_file.seek(0)  # 将指针移到开头
    
    # 发送文件
    return send_file(
        excel_file,
        mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        as_attachment=True,
        download_name='student_import_template.xlsx'
    )

def allowed_file(filename):
    """检查文件扩展名是否允许"""
    ALLOWED_EXTENSIONS = {'xlsx', 'xls', 'csv'}
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@admin.route('/students/export', methods=['GET'])
@login_required
@admin_required
def export_students():
    """导出学生"""
    # 简化起见，这里只返回到学生列表页面，实际功能需要额外开发
    flash('学生数据导出功能将在后续版本提供', 'info')
    return redirect(url_for('admin.students'))

# 课程管理
@admin.route('/courses/new')
@login_required
@admin_required
def courses_new():
    """新版课程列表"""
    page = request.args.get('page', 1, type=int)
    query = Course.query
    
    # 搜索和过滤
    search = request.args.get('q', '')
    if search:
        query = query.filter(Course.name.contains(search) | 
                            Course.code.contains(search))
    
    semester = request.args.get('semester', '')
    if semester:
        query = query.filter_by(semester=semester)
    
    status = request.args.get('status', '')
    if status:
        query = query.filter_by(status=status)
    
    # 分页
    pagination = query.order_by(Course.created_at.desc()).paginate(
        page=page, per_page=current_app.config['ITEMS_PER_PAGE'], error_out=False)
    courses = pagination.items
    
    # 额外统计数据
    active_count = Course.query.filter_by(status='active').count()
    
    # 计算总学分
    total_credits = db.session.query(func.sum(Course.credits)).scalar() or 0
    
    # 课程类型分布
    required_count = Course.query.filter_by(course_type='required').count()
    elective_count = Course.query.filter_by(course_type='elective').count()
    optional_count = Course.query.filter_by(course_type='optional').count()
    
    # 获取当前学期（示例）
    current_semester = "2023-2024-2"  # 或者从配置或其他地方获取
    current_semester_count = Course.query.filter_by(semester=current_semester).count()
    
    return render_template('admin/courses_new.html', 
                           courses=courses, 
                           pagination=pagination,
                           active_count=active_count,
                           total_credits=total_credits,
                           required_count=required_count,
                           elective_count=elective_count,
                           optional_count=optional_count,
                           current_semester_count=current_semester_count)

@admin.route('/courses')
@login_required
@admin_required
def courses():
    """课程列表"""
    page = request.args.get('page', 1, type=int)
    query = Course.query
    
    # 搜索和过滤
    search = request.args.get('q', '')
    if search:
        query = query.filter(Course.name.contains(search) | 
                            Course.code.contains(search))
    
    semester = request.args.get('semester', '')
    if semester:
        query = query.filter_by(semester=semester)
    
    status = request.args.get('status', '')
    if status:
        query = query.filter_by(status=status)
    
    # 分页
    pagination = query.order_by(Course.created_at.desc()).paginate(
        page=page, per_page=current_app.config['ITEMS_PER_PAGE'], error_out=False)
    courses = pagination.items
    
    return render_template('admin/courses.html', 
                          courses=courses, 
                          pagination=pagination)

@admin.route('/courses/create', methods=['GET', 'POST'])
@login_required
@admin_required
def create_course():
    """创建课程"""
    form = CourseForm()
    
    # 设置教师选择列表
    teachers = Teacher.query.all()
    form.teacher_id.choices = [(0, '-- 选择教师 --')] + [(t.id, f"{t.name} ({t.department.name if t.department else '未分配'})") for t in teachers]
    
    if form.validate_on_submit():
        # 创建课程记录
        course = Course(
            code=form.code.data,
            name=form.name.data,
            credits=form.credits.data,
            hours=form.hours.data,
            capacity=form.capacity.data,
            semester=form.semester.data,
            teacher_id=form.teacher_id.data if form.teacher_id.data > 0 else None,
            description=form.description.data,
            status=form.status.data,
            location=form.location.data,
            schedule=form.schedule.data,
            course_type=form.course_type.data,
            prerequisites=form.prerequisites.data,
            allow_selection=(form.allow_selection.data == 'yes'),
            target_grade=form.target_grade.data
        )
        db.session.add(course)
        db.session.commit()
        
        flash('课程创建成功', 'success')
        return redirect(url_for('admin.courses'))
    
    return render_template('admin/create_course.html', form=form)

@admin.route('/courses/<int:id>/edit', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_course(id):
    """编辑课程"""
    course = Course.query.get_or_404(id)
    form = CourseForm(obj=course)
    
    # 设置教师选择列表
    teachers = Teacher.query.all()
    form.teacher_id.choices = [(0, '-- 选择教师 --')] + [(t.id, f"{t.name} ({t.department.name if t.department else '未分配'})") for t in teachers]
    
    # 设置表单中的选项值
    if request.method == 'GET':
        form.allow_selection.data = 'yes' if course.allow_selection else 'no'
        
    if form.validate_on_submit():
        # 更新课程记录
        course.code = form.code.data
        course.name = form.name.data
        course.credits = form.credits.data
        course.hours = form.hours.data
        course.capacity = form.capacity.data
        course.semester = form.semester.data
        course.teacher_id = form.teacher_id.data if form.teacher_id.data > 0 else None
        course.description = form.description.data
        course.status = form.status.data
        course.location = form.location.data
        course.schedule = form.schedule.data
        course.course_type = form.course_type.data
        course.prerequisites = form.prerequisites.data
        course.allow_selection = (form.allow_selection.data == 'yes')
        course.target_grade = form.target_grade.data
        
        db.session.commit()
        flash('课程信息更新成功', 'success')
        return redirect(url_for('admin.courses'))
    
    return render_template('admin/edit_course.html', form=form, course=course)

@admin.route('/courses/<int:id>', methods=['GET'])
@login_required
@admin_required
def view_course(id):
    """查看课程详情"""
    course = Course.query.get_or_404(id)
    
    # 获取选课学生
    enrollments = Enrollment.query.filter_by(course_id=course.id).all()
    
    return render_template('admin/view_course.html', 
                          course=course,
                          enrollments=enrollments)

@admin.route('/courses/<int:id>/delete', methods=['POST'])
@login_required
@admin_required
def delete_course(id):
    """删除课程"""
    course = Course.query.get_or_404(id)
    
    # 检查是否有选课记录
    if course.enrollments.count() > 0:
        flash('该课程已有学生选课，不能删除', 'danger')
        return redirect(url_for('admin.courses'))
    
    db.session.delete(course)
    db.session.commit()
    
    flash('课程删除成功', 'success')
    return redirect(url_for('admin.courses'))

@admin.route('/courses/import', methods=['GET', 'POST'])
@login_required
@admin_required
def import_courses():
    """导入课程"""
    # 简化起见，这里只返回到课程列表页面，实际功能需要额外开发
    flash('课程导入功能将在后续版本提供', 'info')
    return redirect(url_for('admin.courses'))

@admin.route('/courses/export', methods=['GET'])
@login_required
@admin_required
def export_courses():
    """导出课程"""
    # 简化起见，这里只返回到课程列表页面，实际功能需要额外开发
    flash('课程导出功能将在后续版本提供', 'info')
    return redirect(url_for('admin.courses'))

# 用户管理
@admin.route('/users')
@login_required
@admin_required
def users():
    """用户列表"""
    page = request.args.get('page', 1, type=int)
    pagination = User.query.order_by(User.created_at.desc()).paginate(
        page=page, per_page=current_app.config['ITEMS_PER_PAGE'], error_out=False)
    users = pagination.items
    return render_template('admin/users.html', users=users, pagination=pagination)

@admin.route('/users/create', methods=['GET', 'POST'])
@login_required
@admin_required
def create_user():
    """创建用户"""
    form = UserForm()
    form.role.choices = [(role.id, role.name) for role in Role.query.all()]
    
    if form.validate_on_submit():
        user = User(
            username=form.username.data,
            email=form.email.data,
            name=form.name.data,
            phone=form.phone.data,
            password=form.password.data,
            role_id=form.role.data,
            is_active=form.is_active.data
        )
        db.session.add(user)
        db.session.commit()
        flash('用户创建成功', 'success')
        return redirect(url_for('admin.users'))
    
    return render_template('admin/create_user.html', form=form)

@admin.route('/users/<int:id>/edit', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_user(id):
    """编辑用户"""
    user = User.query.get_or_404(id)
    form = UserForm(obj=user)
    form.role.choices = [(role.id, role.name) for role in Role.query.all()]
    
    if form.validate_on_submit():
        user.username = form.username.data
        user.email = form.email.data
        user.name = form.name.data
        user.phone = form.phone.data
        if form.password.data:
            user.password = form.password.data
        user.role_id = form.role.data
        user.is_active = form.is_active.data
        db.session.commit()
        flash('用户更新成功', 'success')
        return redirect(url_for('admin.users'))
    
    return render_template('admin/edit_user.html', form=form, user=user)

@admin.route('/users/<int:id>/delete', methods=['POST'])
@login_required
@admin_required
def delete_user(id):
    """删除用户"""
    user = User.query.get_or_404(id)
    
    # 检查是否为当前登录用户，防止删除自己
    if user == current_user:
        flash('不能删除当前登录的用户账号', 'danger')
        return redirect(url_for('admin.users'))
    
    # 检查用户是否有关联数据，如学生或教师信息
    has_student = hasattr(user, 'student') and user.student is not None
    has_teacher = hasattr(user, 'teacher') and user.teacher is not None
    
    if has_student or has_teacher:
        flash('该用户关联了学生或教师数据，无法直接删除', 'warning')
        return redirect(url_for('admin.users'))
    
    username = user.username
    db.session.delete(user)
    db.session.commit()
    flash(f'用户 {username} 已成功删除', 'success')
    return redirect(url_for('admin.users'))

@admin.route('/application_center')
@login_required
@admin_required
def application_center():
    """应用中心页面"""
    return render_template('admin/application_center.html')

# 班级管理
@admin.route('/classes')
@login_required
@admin_required
def classes():
    """班级列表"""
    # 添加一些示例班级数据
    example_classes = [
        {
            'id': 1,
            'name': '计算机科学与技术2023-1班',
            'code': 'CS2023-1',
            'grade': '2023',
            'major': {
                'name': '计算机科学与技术',
                'department': {'name': '计算机科学与技术学院'}
            },
            'students_count': 35,
            'created_at': datetime(2023, 9, 1)
        },
        {
            'id': 2,
            'name': '软件工程2023-1班',
            'code': 'SE2023-1',
            'grade': '2023',
            'major': {
                'name': '软件工程',
                'department': {'name': '计算机科学与技术学院'}
            },
            'students_count': 40,
            'created_at': datetime(2023, 9, 1)
        },
        {
            'id': 3,
            'name': '数学与应用数学2023-1班',
            'code': 'MA2023-1',
            'grade': '2023',
            'major': {
                'name': '数学与应用数学',
                'department': {'name': '数学学院'}
            },
            'students_count': 30,
            'created_at': datetime(2023, 9, 1)
        },
        {
            'id': 4,
            'name': '英语2023-1班',
            'code': 'EN2023-1',
            'grade': '2023',
            'major': {
                'name': '英语',
                'department': {'name': '外国语学院'}
            },
            'students_count': 32,
            'created_at': datetime(2023, 9, 1)
        },
        {
            'id': 5,
            'name': '机械工程2023-1班',
            'code': 'ME2023-1',
            'grade': '2023',
            'major': {
                'name': '机械工程',
                'department': {'name': '机械工程学院'}
            },
            'students_count': 38,
            'created_at': datetime(2023, 9, 1)
        },
        {
            'id': 6,
            'name': '计算机科学与技术2022-1班',
            'code': 'CS2022-1',
            'grade': '2022',
            'major': {
                'name': '计算机科学与技术',
                'department': {'name': '计算机科学与技术学院'}
            },
            'students_count': 36,
            'created_at': datetime(2022, 9, 1)
        },
        {
            'id': 7,
            'name': '软件工程2022-1班',
            'code': 'SE2022-1',
            'grade': '2022',
            'major': {
                'name': '软件工程',
                'department': {'name': '计算机科学与技术学院'}
            },
            'students_count': 42,
            'created_at': datetime(2022, 9, 1)
        },
        {
            'id': 8,
            'name': '物理学2023-1班',
            'code': 'PH2023-1',
            'grade': '2023',
            'major': {
                'name': '物理学',
                'department': {'name': '物理学院'}
            },
            'students_count': 28,
            'created_at': datetime(2023, 9, 1)
        }
    ]
    
    page = request.args.get('page', 1, type=int)
    query = Class.query
    
    # 搜索和过滤
    search = request.args.get('q', '')
    if search:
        query = query.filter(Class.name.contains(search))
    
    major_id = request.args.get('major_id', '')
    if major_id and major_id.isdigit():
        query = query.filter_by(major_id=int(major_id))
    
    # 分页
    pagination = query.order_by(Class.created_at.desc()).paginate(
        page=page, per_page=current_app.config['ITEMS_PER_PAGE'], error_out=False)
    classes = pagination.items
    
    # 如果数据库中没有班级数据，使用示例数据
    if not classes:
        classes = example_classes
        pagination = None
    
    # 获取所有专业供过滤使用
    majors = Major.query.all()
    
    return render_template('admin/classes.html', 
                          classes=classes, 
                          pagination=pagination,
                          majors=majors)

@admin.route('/classes/create', methods=['GET', 'POST'])
@login_required
@admin_required
def create_class():
    """创建班级"""
    form = ClassForm()
    form.major_id.choices = [(m.id, f"{m.name} ({m.department.name if m.department else '未分配'})") for m in Major.query.all()]
    
    if form.validate_on_submit():
        class_obj = Class(
            name=form.name.data,
            code=form.code.data,
            grade=str(form.grade.data),  # 转为字符串，与模型定义匹配
            major_id=form.major_id.data,
            description=form.description.data
        )
        db.session.add(class_obj)
        db.session.commit()
        
        flash('班级创建成功', 'success')
        return redirect(url_for('admin.classes'))
    
    return render_template('admin/create_class.html', form=form)

# 专业管理
@admin.route('/majors')
@login_required
@admin_required
def majors():
    """专业列表"""
    page = request.args.get('page', 1, type=int)
    query = Major.query
    
    # 搜索和过滤
    search = request.args.get('q', '')
    if search:
        query = query.filter(Major.name.contains(search))
    
    department_id = request.args.get('department_id', '')
    if department_id and department_id.isdigit():
        query = query.filter_by(department_id=int(department_id))
    
    # 分页
    pagination = query.order_by(Major.created_at.desc()).paginate(
        page=page, per_page=current_app.config['ITEMS_PER_PAGE'], error_out=False)
    majors = pagination.items
    
    # 获取所有院系供过滤使用
    departments = Department.query.all()
    
    # 计算各类型专业数量，用于图表显示
    total_majors = Major.query.count()
    
    # 计算各专业的学生数量
    student_counts = {}
    for major in majors:
        student_counts[major.id] = major.get_student_count()
    
    # 根据专业的不同字段来区分专业类型
    from sqlalchemy import func
    
    # 假设 Major 模型有 level 字段表示专业级别（本科、专科、硕士、博士）
    try:
        undergrad_count = Major.query.filter_by(level='本科').count()
    except:
        undergrad_count = 0
        
    try:
        associate_count = Major.query.filter_by(level='专科').count()
    except:
        associate_count = 0
        
    try:
        master_count = Major.query.filter_by(level='硕士').count()
    except:
        master_count = 0
        
    try:
        phd_count = Major.query.filter_by(level='博士').count()
    except:
        phd_count = 0
    
    return render_template('admin/majors.html', 
                          majors=majors, 
                          pagination=pagination,
                          departments=departments,
                          total_majors=total_majors or 1,  # 避免除以零错误
                          undergrad_count=undergrad_count,
                          associate_count=associate_count,
                          master_count=master_count,
                          phd_count=phd_count,
                          student_counts=student_counts)

@admin.route('/majors/create', methods=['GET', 'POST'])
@login_required
@admin_required
def create_major():
    """创建专业"""
    form = MajorForm()
    
    # 获取所有院系作为选项
    departments = Department.query.all()
    if not departments:
        flash('请先创建院系', 'warning')
        return redirect(url_for('admin.departments'))
        
    form.department_id.choices = [(d.id, d.name) for d in departments]
    
    if form.validate_on_submit():
        try:
            # 检查专业代码是否已存在
            existing_major = Major.query.filter_by(code=form.code.data).first()
            if existing_major:
                flash('专业代码已存在', 'error')
                return render_template('admin/create_major.html', form=form)
            
            # 创建专业记录
            major = Major(
                name=form.name.data,
                code=form.code.data,
                department_id=form.department_id.data,
                description=form.description.data,
                level=form.level.data,
                years=form.years.data,
                status=form.status.data
            )
            db.session.add(major)
            db.session.commit()
            
            flash('专业创建成功', 'success')
            return redirect(url_for('admin.majors'))
            
        except Exception as e:
            db.session.rollback()
            flash(f'创建专业失败: {str(e)}', 'error')
            return render_template('admin/create_major.html', form=form)
    
    return render_template('admin/create_major.html', form=form)

@admin.route('/majors/<int:id>', methods=['GET'])
@login_required
@admin_required
def view_major(id):
    """查看专业详情"""
    major = Major.query.get_or_404(id)
    
    # 获取相关数据
    class_count = major.classes.count()
    student_count = major.get_student_count()
    course_count = 0  # 这里需要实际查询该专业的课程数量
    
    # 获取该专业的班级
    classes = major.classes.all()
    
    # 获取该专业相关的课程（这里需要根据实际模型关系进行查询）
    major_courses = []
    
    return render_template('admin/view_major.html',
                          major=major,
                          class_count=class_count,
                          student_count=student_count,
                          course_count=course_count,
                          classes=classes,
                          major_courses=major_courses)

@admin.route('/majors/<int:id>/edit', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_major(id):
    """编辑专业"""
    major = Major.query.get_or_404(id)
    form = MajorForm(obj=major)
    form.department_id.choices = [(d.id, d.name) for d in Department.query.all()]
    
    if form.validate_on_submit():
        major.name = form.name.data
        major.code = form.code.data
        major.department_id = form.department_id.data
        major.level = form.level.data
        major.years = form.years.data
        major.description = form.description.data
        major.status = form.status.data
        
        db.session.commit()
        flash('专业信息更新成功', 'success')
        return redirect(url_for('admin.view_major', id=major.id))
    
    return render_template('admin/edit_major.html', form=form, major=major)

# 院系管理
@admin.route('/departments')
@login_required
@admin_required
def departments():
    """院系列表"""
    # 添加一些示例院系数据
    example_departments = [
        {
            'id': 1,
            'name': '计算机科学与技术学院',
            'code': 'CS',
            'description': '培养计算机科学、软件工程等领域的专业人才',
            'status': 'active',
            'created_at': datetime(2020, 9, 1),
            'majors_count': 3,
            'teachers_count': 45,
            'students_count': 650
        },
        {
            'id': 2,
            'name': '数学学院',
            'code': 'MATH',
            'description': '培养数学与应用数学、统计学等领域的专业人才',
            'status': 'active',
            'created_at': datetime(2020, 9, 1),
            'majors_count': 2,
            'teachers_count': 38,
            'students_count': 420
        },
        {
            'id': 3,
            'name': '外国语学院',
            'code': 'FL',
            'description': '培养英语、日语、德语等语言专业人才',
            'status': 'active',
            'created_at': datetime(2020, 9, 1),
            'majors_count': 4,
            'teachers_count': 52,
            'students_count': 580
        },
        {
            'id': 4,
            'name': '物理学院',
            'code': 'PHY',
            'description': '培养物理学、应用物理等领域的专业人才',
            'status': 'active',
            'created_at': datetime(2020, 9, 1),
            'majors_count': 2,
            'teachers_count': 35,
            'students_count': 320
        },
        {
            'id': 5,
            'name': '化学学院',
            'code': 'CHEM',
            'description': '培养化学、应用化学等领域的专业人才',
            'status': 'active',
            'created_at': datetime(2020, 9, 1),
            'majors_count': 2,
            'teachers_count': 40,
            'students_count': 380
        },
        {
            'id': 6,
            'name': '机械工程学院',
            'code': 'ME',
            'description': '培养机械工程、自动化等领域的专业人才',
            'status': 'active',
            'created_at': datetime(2020, 9, 1),
            'majors_count': 3,
            'teachers_count': 48,
            'students_count': 520
        },
        {
            'id': 7,
            'name': '艺术学院',
            'code': 'ART',
            'description': '培养音乐、美术、设计等艺术领域的专业人才',
            'status': 'active',
            'created_at': datetime(2020, 9, 1),
            'majors_count': 4,
            'teachers_count': 42,
            'students_count': 460
        },
        {
            'id': 8,
            'name': '经济管理学院',
            'code': 'EM',
            'description': '培养经济学、工商管理等领域的专业人才',
            'status': 'active',
            'created_at': datetime(2020, 9, 1),
            'majors_count': 5,
            'teachers_count': 56,
            'students_count': 720
        }
    ]
    
    page = request.args.get('page', 1, type=int)
    query = Department.query
    
    # 搜索和过滤
    search = request.args.get('q', '')
    if search:
        query = query.filter(Department.name.contains(search))
    
    # 分页
    pagination = query.order_by(Department.created_at.desc()).paginate(
        page=page, per_page=current_app.config['ITEMS_PER_PAGE'], error_out=False)
    departments = pagination.items
    
    # 如果数据库中没有院系数据，使用示例数据
    if not departments:
        departments = example_departments
        pagination = None
    
    return render_template('admin/departments.html', 
                          departments=departments,
                          pagination=pagination)

@admin.route('/departments/create', methods=['GET', 'POST'])
@login_required
@admin_required
def create_department():
    """创建院系"""
    form = DepartmentForm()
    
    if form.validate_on_submit():
        department = Department(
            name=form.name.data,
            code=form.code.data,
            contact=form.contact.data,
            description=form.description.data
        )
        db.session.add(department)
        db.session.commit()
        
        flash('院系创建成功', 'success')
        return redirect(url_for('admin.departments'))
    
    return render_template('admin/create_department.html', form=form)

@admin.route('/departments/<int:id>', methods=['GET'])
@login_required
@admin_required
def view_department(id):
    """查看院系详情"""
    department = Department.query.get_or_404(id)
    
    # 获取该院系下的专业列表
    majors = Major.query.filter_by(department_id=id).all()
    
    # 统计数据
    teacher_count = Teacher.query.filter_by(department_id=id).count()
    major_count = len(majors)
    
    # 计算学生数量
    student_count = 0
    for major in majors:
        for class_ in major.classes:
            student_count += class_.students.count()
    
    return render_template('admin/view_department.html',
                          department=department,
                          majors=majors,
                          teacher_count=teacher_count,
                          major_count=major_count,
                          student_count=student_count)

@admin.route('/departments/<int:id>/edit', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_department(id):
    """编辑院系"""
    department = Department.query.get_or_404(id)
    form = DepartmentForm(obj=department)
    
    if form.validate_on_submit():
        department.name = form.name.data
        department.code = form.code.data
        department.contact = form.contact.data
        department.description = form.description.data
        
        db.session.commit()
        flash('院系信息更新成功', 'success')
        return redirect(url_for('admin.view_department', id=department.id))
    
    return render_template('admin/edit_department.html', form=form, department=department)

# 公告管理
@admin.route('/announcements')
@login_required
@admin_required
def announcements():
    """公告列表"""
    return render_template('admin/announcements.html')

# 系统设置
@admin.route('/settings', methods=['GET'])
@login_required
@admin_required
def settings():
    """系统设置页面"""
    settings_dict = SystemSettingService.get_dict()
    return render_template('admin/settings.html', settings=settings_dict)

@admin.route('/settings/save', methods=['POST'])
@login_required
@admin_required
def save_settings():
    """保存系统设置"""
    setting_type = request.form.get('setting_type', 'basic')
    
    if setting_type == 'basic':
        # 保存基本设置
        site_name = request.form.get('site_name')
        school_name = request.form.get('school_name')
        contact_email = request.form.get('contact_email')
        current_semester = request.form.get('current_semester')
        items_per_page = request.form.get('items_per_page')
        enable_registration = 'true' if request.form.get('enable_registration') else 'false'
        
        SystemSettingService.set('site_name', site_name, 'string', '站点名称')
        SystemSettingService.set('school_name', school_name, 'string', '学校名称')
        SystemSettingService.set('contact_email', contact_email, 'string', '联系邮箱')
        SystemSettingService.set('current_semester', current_semester, 'string', '当前学期')
        SystemSettingService.set('items_per_page', items_per_page, 'int', '每页项目数')
        SystemSettingService.set('enable_registration', enable_registration, 'boolean', '是否允许注册')
        
        flash('基本设置已保存', 'success')
    
    elif setting_type == 'appearance':
        # 保存外观设置
        theme_color = request.form.get('theme_color')
        layout_style = request.form.get('layout_style')
        
        SystemSettingService.set('theme_color', theme_color, 'string', '主题颜色')
        SystemSettingService.set('layout_style', layout_style, 'string', '布局样式')
        
        # 处理上传的Logo
        if 'logo' in request.files and request.files['logo'].filename:
            logo = request.files['logo']
            filename = secure_filename(logo.filename)
            upload_dir = os.path.join(current_app.static_folder, 'uploads')
            if not os.path.exists(upload_dir):
                os.makedirs(upload_dir)
            
            logo_path = os.path.join(upload_dir, filename)
            logo.save(logo_path)
            logo_url = url_for('static', filename=f'uploads/{filename}')
            SystemSettingService.set('logo', logo_url, 'string', '系统Logo')
        
        # 处理上传的Favicon
        if 'favicon' in request.files and request.files['favicon'].filename:
            favicon = request.files['favicon']
            filename = secure_filename(favicon.filename)
            upload_dir = os.path.join(current_app.static_folder, 'uploads')
            if not os.path.exists(upload_dir):
                os.makedirs(upload_dir)
            
            favicon_path = os.path.join(upload_dir, filename)
            favicon.save(favicon_path)
            favicon_url = url_for('static', filename=f'uploads/{filename}')
            SystemSettingService.set('favicon', favicon_url, 'string', '网站图标')
        
        flash('外观设置已保存', 'success')
        
    elif setting_type == 'home_appearance':
        # 保存首页外观设置
        home_theme_color = request.form.get('home_theme_color')
        home_layout_style = request.form.get('home_layout_style')
        
        SystemSettingService.set('home_theme_color', home_theme_color, 'string', '首页主题颜色')
        SystemSettingService.set('home_layout_style', home_layout_style, 'string', '首页布局样式')
        
        # 处理上传的首页Logo
        if 'home_logo' in request.files and request.files['home_logo'].filename:
            logo = request.files['home_logo']
            filename = secure_filename(logo.filename)
            upload_dir = os.path.join(current_app.static_folder, 'uploads')
            if not os.path.exists(upload_dir):
                os.makedirs(upload_dir)
            
            logo_path = os.path.join(upload_dir, filename)
            logo.save(logo_path)
            logo_url = url_for('static', filename=f'uploads/{filename}')
            SystemSettingService.set('home_logo', logo_url, 'string', '首页Logo')
            
        flash('首页外观设置已保存', 'success')
    
    elif setting_type == 'security':
        # 保存安全设置
        password_min_length = request.form.get('password_min_length')
        password_complexity = 'true' if request.form.get('password_complexity') else 'false'
        session_timeout = request.form.get('session_timeout')
        
        SystemSettingService.set('password_min_length', password_min_length, 'int', '密码最小长度')
        SystemSettingService.set('password_complexity', password_complexity, 'boolean', '密码复杂度要求')
        SystemSettingService.set('session_timeout', session_timeout, 'int', '会话超时时间(秒)')
        
        flash('安全设置已保存', 'success')
    
    elif setting_type == 'backup':
        # 备份功能将在后续版本实现
        flash('备份功能将在后续版本实现', 'warning')
    
    elif setting_type == 'logs':
        # 日志功能将在后续版本实现
        flash('日志功能将在后续版本实现', 'warning')
    
    return redirect(url_for('admin.settings'))

@admin.route('/settings/backup', methods=['POST'])
@login_required
@admin_required
def backup_database():
    """备份数据库"""
    # 备份功能将在后续版本实现
    flash('备份功能将在后续版本实现', 'warning')
    return redirect(url_for('admin.settings'))

@admin.route('/settings/restore', methods=['POST'])
@login_required
@admin_required
def restore_database():
    """恢复数据库"""
    # 恢复功能将在后续版本实现
    flash('恢复功能将在后续版本实现', 'warning')
    return redirect(url_for('admin.settings'))

@admin.route('/settings/export_logs', methods=['POST'])
@login_required
@admin_required
def export_logs():
    """导出日志"""
    # 日志导出功能将在后续版本实现
    flash('日志导出功能将在后续版本实现', 'warning')
    return redirect(url_for('admin.settings'))

@admin.route('/settings/clear_logs', methods=['POST'])
@login_required
@admin_required
def clear_logs():
    """清空日志"""
    # 清空日志功能将在后续版本实现
    flash('清空日志功能将在后续版本实现', 'warning')
    return redirect(url_for('admin.settings'))

# 教师管理
@admin.route('/teachers')
@login_required
@admin_required
def teachers():
    """教师列表"""
    # 添加一些示例教师数据
    example_teachers = [
        {
            'id': 1,
            'teacher_id': 'T20230001',
            'name': '张明',
            'title': '教授',
            'department': '计算机科学与技术学院',
            'status': 'active',
            'courses_count': 3,
            'phone': '13800138001',
            'email': 'zhang.ming@example.com'
        },
        {
            'id': 2,
            'teacher_id': 'T20230002',
            'name': '李华',
            'title': '副教授',
            'department': '数学学院',
            'status': 'active',
            'courses_count': 2,
            'phone': '13800138002',
            'email': 'li.hua@example.com'
        },
        {
            'id': 3,
            'teacher_id': 'T20230003',
            'name': '王芳',
            'title': '讲师',
            'department': '外国语学院',
            'status': 'active',
            'courses_count': 4,
            'phone': '13800138003',
            'email': 'wang.fang@example.com'
        },
        {
            'id': 4,
            'teacher_id': 'T20230004',
            'name': '刘伟',
            'title': '教授',
            'department': '物理学院',
            'status': 'active',
            'courses_count': 2,
            'phone': '13800138004',
            'email': 'liu.wei@example.com'
        },
        {
            'id': 5,
            'teacher_id': 'T20230005',
            'name': '陈静',
            'title': '副教授',
            'department': '化学学院',
            'status': 'active',
            'courses_count': 3,
            'phone': '13800138005',
            'email': 'chen.jing@example.com'
        },
        {
            'id': 6,
            'teacher_id': 'T20230006',
            'name': '赵阳',
            'title': '教授',
            'department': '机械工程学院',
            'status': 'active',
            'courses_count': 2,
            'phone': '13800138006',
            'email': 'zhao.yang@example.com'
        },
        {
            'id': 7,
            'teacher_id': 'T20230007',
            'name': '孙莉',
            'title': '讲师',
            'department': '艺术学院',
            'status': 'active',
            'courses_count': 3,
            'phone': '13800138007',
            'email': 'sun.li@example.com'
        },
        {
            'id': 8,
            'teacher_id': 'T20230008',
            'name': '周强',
            'title': '副教授',
            'department': '经济管理学院',
            'status': 'active',
            'courses_count': 4,
            'phone': '13800138008',
            'email': 'zhou.qiang@example.com'
        }
    ]
    
    page = request.args.get('page', 1, type=int)
    query = Teacher.query
    
    # 搜索和过滤
    search = request.args.get('q', '')
    if search:
        query = query.filter(Teacher.name.contains(search) | 
                            Teacher.teacher_id.contains(search))
    
    department_id = request.args.get('department_id', '')
    if department_id and department_id.isdigit():
        query = query.filter_by(department_id=int(department_id))
    
    status = request.args.get('status', '')
    if status:
        query = query.filter_by(status=status)
    
    # 分页
    pagination = query.order_by(Teacher.created_at.desc()).paginate(
        page=page, per_page=current_app.config['ITEMS_PER_PAGE'], error_out=False)
    teachers = pagination.items
    
    # 如果数据库中没有教师数据，使用示例数据
    if not teachers:
        teachers = example_teachers
        pagination = None
    
    # 获取所有院系供过滤使用
    departments = Department.query.all()
    
    return render_template('admin/teachers.html', 
                          teachers=teachers, 
                          pagination=pagination,
                          departments=departments)

@admin.route('/teachers/create', methods=['GET', 'POST'])
@login_required
@admin_required
def create_teacher():
    """创建教师"""
    from app.forms.teacher import TeacherForm
    
    form = TeacherForm()
    form.department_id.choices = [(d.id, d.name) for d in Department.query.all()]
    
    if form.validate_on_submit():
        # 先创建用户账号
        user = User(
            username=form.teacher_id.data,
            email=form.email.data,
            name=form.name.data,
            phone=form.phone.data,
            password=form.password.data,
            role_id=Role.query.filter_by(name='Teacher').first().id,
            is_active=True
        )
        db.session.add(user)
        db.session.flush()  # 获取用户ID
        
        # 创建教师记录
        teacher = Teacher(
            teacher_id=form.teacher_id.data,
            name=form.name.data,
            gender=form.gender.data,
            title=form.title.data,
            phone=form.phone.data,
            status=form.status.data,
            department_id=form.department_id.data,
            bio=form.bio.data,
            user_id=user.id
        )
        db.session.add(teacher)
        db.session.commit()
        
        flash('教师创建成功', 'success')
        return redirect(url_for('admin.teachers'))
    
    return render_template('admin/create_teacher.html', form=form)

@admin.route('/teachers/<int:id>/edit', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_teacher(id):
    """编辑教师"""
    from app.forms.teacher import TeacherForm
    
    teacher = Teacher.query.get_or_404(id)
    form = TeacherForm(obj=teacher)
    form.department_id.choices = [(d.id, d.name) for d in Department.query.all()]
    
    if request.method == 'GET':
        # 如果教师已关联用户，填充关联用户的邮箱
        if teacher.user:
            form.email.data = teacher.user.email
    
    if form.validate_on_submit():
        teacher.name = form.name.data
        teacher.gender = form.gender.data
        teacher.title = form.title.data
        teacher.phone = form.phone.data
        teacher.status = form.status.data
        teacher.department_id = form.department_id.data
        teacher.bio = form.bio.data
        
        # 更新用户信息
        if teacher.user:
            teacher.user.email = form.email.data
            teacher.user.name = form.name.data
            teacher.user.phone = form.phone.data
            
            # 如果提供了密码，则更新密码
            if form.password.data:
                teacher.user.password = form.password.data
        
        db.session.commit()
        flash('教师信息更新成功', 'success')
        return redirect(url_for('admin.view_teacher', id=teacher.id))
    
    return render_template('admin/edit_teacher.html', form=form, teacher=teacher)

@admin.route('/teachers/<int:id>', methods=['GET'])
@login_required
@admin_required
def view_teacher(id):
    """查看教师详情"""
    teacher = Teacher.query.get_or_404(id)
    
    # 获取教师所教授的课程
    courses = Course.query.filter_by(teacher_id=teacher.id).all()
    
    return render_template('admin/view_teacher.html', 
                          teacher=teacher,
                          courses=courses)

@admin.route('/teachers/<int:id>/delete', methods=['POST'])
@login_required
@admin_required
def delete_teacher(id):
    """删除教师"""
    teacher = Teacher.query.get_or_404(id)
    
    # 检查是否有关联的课程
    courses = Course.query.filter_by(teacher_id=teacher.id).all()
    if courses:
        flash(f'无法删除教师，该教师还有{len(courses)}门关联课程', 'danger')
        return redirect(url_for('admin.teachers'))
    
    # 删除关联的用户账号
    if teacher.user:
        user = teacher.user
        db.session.delete(user)
    
    # 删除教师记录
    db.session.delete(teacher)
    db.session.commit()
    
    flash('教师删除成功', 'success')
    return redirect(url_for('admin.teachers'))

@admin.route('/teachers/import', methods=['GET', 'POST'])
@login_required
@admin_required
def import_teachers():
    """批量导入教师"""
    return render_template('admin/import_teachers.html')

@admin.route('/help')
@login_required
def help():
    """帮助页面"""
    return render_template('admin/help.html')

@admin.route('/quality/dashboard')
@login_required
def quality_dashboard():
    """素养维度大屏"""
    return render_template('admin/quality_dashboard.html')

@admin.route('/system/literacy/certificates')
@login_required
def quality_certificates():
    """素养证书页面"""
    # 创建一些示例证书数据
    certificates = [
        {
            'id': 1,
            'name': '全国计算机等级考试二级证书',
            'certificate_type': 'professional',
            'certificate_no': 'NCRE2024001',
            'issuer': '教育部考试中心',
            'issue_date': datetime(2024, 4, 7),
            'status': 'approved',
            'blockchain_enabled': True,
            'blockchain_certificate_id': '0x0085ff9d03a949478025331c9db87a0a',
            'blockchain_verification_url': 'https://example.com/verify/bc001',
            'student_name': '张三'
        },
        {
            'id': 2,
            'name': '大学英语六级证书',
            'certificate_type': 'language',
            'certificate_no': 'CET6202403001',
            'issuer': '教育部考试中心',
            'issue_date': datetime(2024, 4, 12),
            'status': 'approved',
            'blockchain_enabled': True,
            'blockchain_certificate_id': 'bc002',
            'blockchain_verification_url': 'https://example.com/verify/bc002',
            'student_name': '李四'
        },
        {
            'id': 3,
            'name': '全国大学生数学建模竞赛省级一等奖',
            'certificate_type': 'competition',
            'certificate_no': 'CUMCM2024001',
            'issuer': '中国工业与应用数学学会',
            'issue_date': datetime(2024, 2, 10),
            'status': 'pending',
            'blockchain_enabled': False,
            'blockchain_certificate_id': None,
            'blockchain_verification_url': None,
            'student_name': '王五'
        },
        {
            'id': 4,
            'name': 'Python认证开发工程师',
            'certificate_type': 'skill',
            'certificate_no': 'PCEP2024001',
            'issuer': 'Python Institute',
            'issue_date': datetime(2024, 4, 15),
            'status': 'approved',
            'blockchain_enabled': True,
            'blockchain_certificate_id': 'bc003',
            'blockchain_verification_url': 'https://example.com/verify/bc003',
            'student_name': '赵六'
        },
        {
            'id': 5,
            'name': '人工智能工程师认证',
            'certificate_type': 'professional',
            'certificate_no': 'AI2024001',
            'issuer': '中国人工智能产业发展联盟',
            'issue_date': datetime(2024, 1, 30),
            'status': 'pending',
            'blockchain_enabled': False,
            'blockchain_certificate_id': None,
            'blockchain_verification_url': None,
            'student_name': '孙七'
        },
        {
            'id': 6,
            'name': '软件工程师资格认证',
            'certificate_type': 'professional',
            'certificate_no': 'SE2024001',
            'issuer': '中国软件行业协会',
            'issue_date': datetime(2024, 4, 5),
            'status': 'approved',
            'blockchain_enabled': True,
            'blockchain_certificate_id': 'bc004',
            'blockchain_verification_url': 'https://example.com/verify/bc004',
            'student_name': '周八'
        },
        {
            'id': 7,
            'name': '网络安全工程师认证',
            'certificate_type': 'skill',
            'certificate_no': 'SEC2024001',
            'issuer': '中国信息安全测评中心',
            'issue_date': datetime(2024, 4, 12),
            'status': 'approved',
            'blockchain_enabled': True,
            'blockchain_certificate_id': 'bc005',
            'blockchain_verification_url': 'https://example.com/verify/bc005',
            'student_name': '吴九'
        },
        {
            'id': 8,
            'name': '全国英语演讲比赛校级一等奖',
            'certificate_type': 'competition',
            'certificate_no': 'ESC2024001',
            'issuer': '校英语系',
            'issue_date': datetime(2024, 3, 28),
            'status': 'approved',
            'blockchain_enabled': False,
            'blockchain_certificate_id': None,
            'blockchain_verification_url': None,
            'student_name': '郑十'
        }
    ]

    # 计算统计数据
    context = {
        'total_count': len(certificates),
        'approved_count': sum(1 for cert in certificates if cert['status'] == 'approved'),
        'pending_count': sum(1 for cert in certificates if cert['status'] == 'pending'),
        'rejected_count': sum(1 for cert in certificates if cert['status'] == 'rejected'),
        'certificates': certificates  # 添加证书列表到上下文
    }
    
    return render_template('admin/quality_certificate.html', **context)

@admin.route('/quality/reports')
@login_required
def quality_reports():
    """素养报告页面"""
    # TODO: 从数据库获取报告统计数据
    context = {
        'report_count': 0,
        'comprehensive_count': 0,
        'professional_count': 0,
        'social_count': 0
    }
    return render_template('admin/quality_report.html', **context)

@admin.route('/quality/dimension_dashboard')
@login_required
def quality_dimension_dashboard():
    """素养维度大屏直接访问"""
    # 返回404页面，因为此功能已移除
    abort(404)
    # 原来的代码: return redirect(url_for('admin.quality_reports', tab='dashboard'))