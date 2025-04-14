from flask import Blueprint, render_template, redirect, url_for, flash, request, current_app
from flask_login import login_required, current_user
from app import db
from datetime import datetime
from app.models.user import User, Role, Permission
from app.utils.decorators import admin_required
import os
from werkzeug.utils import secure_filename
from app.models.unity_cert import UnifiedCertificate
from app.models.student import Student

system_extended = Blueprint('system_extended', __name__)

# 基础信息管理
@system_extended.route('/basic_info')
@login_required
@admin_required
def basic_info():
    """基础信息管理"""
    return render_template('system/basic_info.html')

@system_extended.route('/colleges')
@login_required
@admin_required
def colleges():
    """学院管理"""
    # 这里可以添加学院查询逻辑
    colleges = []
    return render_template('system/colleges.html', colleges=colleges)

@system_extended.route('/students')
@login_required
@admin_required
def students():
    """学生管理"""
    # 这里可以添加学生查询逻辑
    students = []
    return render_template('system/students.html', students=students)

@system_extended.route('/classes')
@login_required
@admin_required
def classes():
    """班级管理"""
    # 这里可以添加班级查询逻辑
    classes = []
    return render_template('system/classes.html', classes=classes)

@system_extended.route('/majors')
@login_required
@admin_required
def majors():
    """专业管理"""
    # 这里可以添加专业查询逻辑
    majors = []
    return render_template('system/majors.html', majors=majors)

# 校内资源管理
@system_extended.route('/campus_resources')
@login_required
@admin_required
def campus_resources():
    """校内资源管理"""
    return render_template('system/campus_resources.html')

@system_extended.route('/books')
@login_required
@admin_required
def books():
    """图书管理"""
    # 这里可以添加图书查询逻辑
    books = []
    return render_template('system/books.html', books=books)

@system_extended.route('/textbooks')
@login_required
@admin_required
def textbooks():
    """教材管理"""
    # 这里可以添加教材查询逻辑
    textbooks = []
    return render_template('system/textbooks.html', textbooks=textbooks)

@system_extended.route('/laboratories')
@login_required
@admin_required
def laboratories():
    """实验室管理"""
    # 这里可以添加实验室查询逻辑
    laboratories = []
    return render_template('system/laboratories.html', laboratories=laboratories)

@system_extended.route('/multimedia_classrooms')
@login_required
@admin_required
def multimedia_classrooms():
    """多媒体教室管理"""
    # 这里可以添加多媒体教室查询逻辑
    classrooms = []
    return render_template('system/multimedia_classrooms.html', classrooms=classrooms)

@system_extended.route('/sports_facilities')
@login_required
@admin_required
def sports_facilities():
    """体育设施管理"""
    # 这里可以添加体育设施查询逻辑
    facilities = []
    return render_template('system/sports_facilities.html', facilities=facilities)

# 活动通知管理
@system_extended.route('/activities')
@login_required
@admin_required
def activities():
    """活动通知管理"""
    # 这里可以添加活动和通知查询逻辑
    announcements = []
    activities = []
    return render_template('system/activities.html', announcements=announcements, activities=activities)

@system_extended.route('/announcements')
@login_required
@admin_required
def announcements():
    """通知公告管理"""
    # 这里可以添加通知公告查询逻辑
    announcements = []
    return render_template('system/announcements.html', announcements=announcements)

@system_extended.route('/create_announcement', methods=['GET', 'POST'])
@login_required
@admin_required
def create_announcement():
    """创建通知公告"""
    # 这里可以添加创建通知公告的逻辑
    return render_template('system/create_announcement.html')

@system_extended.route('/create_activity', methods=['GET', 'POST'])
@login_required
@admin_required
def create_activity():
    """创建活动"""
    # 这里可以添加创建活动的逻辑
    return render_template('system/create_activity.html')

# 设备管理
@system_extended.route('/equipment')
@login_required
@admin_required
def equipment():
    """设备管理"""
    # 查询所有设备
    from app.models.equipment import Equipment
    equipments = Equipment.query.order_by(Equipment.created_at.desc()).all()
    return render_template('system/equipment.html', equipments=equipments)

@system_extended.route('/equipment_register', methods=['GET', 'POST'])
@login_required
@admin_required
def equipment_register():
    """设备登记"""
    from app.forms.equipment import EquipmentForm
    from app.models.equipment import Equipment
    from app.models.user import User
    
    form = EquipmentForm()
    # 获取所有可能的负责人（管理员用户）
    form.manager_id.choices = [(u.id, u.name) for u in User.query.filter_by(is_admin=True).all()]
    
    if form.validate_on_submit():
        equipment = Equipment(
            code=form.code.data,
            name=form.name.data,
            type=form.type.data,
            model=form.model.data,
            brand=form.brand.data,
            location=form.location.data,
            purchase_date=form.purchase_date.data,
            price=form.price.data,
            status=form.status.data,
            description=form.description.data,
            manager_id=form.manager_id.data
        )
        db.session.add(equipment)
        try:
            db.session.commit()
            flash('设备添加成功', 'success')
            return redirect(url_for('system_extended.equipment'))
        except Exception as e:
            db.session.rollback()
            flash(f'设备添加失败: {str(e)}', 'danger')
    
    return render_template('system/equipment_register.html', form=form)

@system_extended.route('/equipment_maintenance', methods=['GET', 'POST'])
@login_required
@admin_required
def equipment_maintenance():
    """设备维护"""
    from app.forms.equipment import EquipmentMaintenanceForm
    from app.models.equipment import Equipment, EquipmentMaintenance
    
    # 查询所有维护记录
    maintenance_records = EquipmentMaintenance.query.order_by(EquipmentMaintenance.created_at.desc()).all()
    
    # 统计数据
    total_maintenance = len(maintenance_records)
    in_progress_count = sum(1 for r in maintenance_records if r.status == 'in_progress')
    completed_count = sum(1 for r in maintenance_records if r.status == 'completed')
    failed_count = sum(1 for r in maintenance_records if r.status == 'failed')
    
    form = EquipmentMaintenanceForm()
    # 获取所有可用设备作为选项
    form.equipment_id.choices = [(e.id, f'{e.code} - {e.name}') for e in Equipment.query.filter(Equipment.status != 'scrapped').all()]
    
    if form.validate_on_submit():
        maintenance = EquipmentMaintenance(
            equipment_id=form.equipment_id.data,
            maintenance_type=form.maintenance_type.data,
            start_time=form.start_time.data,
            end_time=form.end_time.data,
            maintainer=form.maintainer.data,
            cost=form.cost.data,
            description=form.description.data,
            result=form.result.data,
            status=form.status.data
        )
        
        # 如果设备状态为维修中，则更新设备状态
        equipment = Equipment.query.get(form.equipment_id.data)
        if equipment and form.status.data == 'in_progress':
            equipment.status = 'maintenance'
        elif equipment and form.status.data == 'completed':
            equipment.status = 'available'
            
        db.session.add(maintenance)
        try:
            db.session.commit()
            flash('设备维护记录添加成功', 'success')
            return redirect(url_for('system_extended.equipment_maintenance'))
        except Exception as e:
            db.session.rollback()
            flash(f'设备维护记录添加失败: {str(e)}', 'danger')
    
    return render_template('system/equipment_maintenance.html', 
                           form=form, 
                           maintenance_records=maintenance_records,
                           total_maintenance=total_maintenance,
                           in_progress_count=in_progress_count,
                           completed_count=completed_count,
                           failed_count=failed_count)

@system_extended.route('/equipment_borrow', methods=['GET', 'POST'])
@login_required
def equipment_borrow():
    """设备借用"""
    from app.forms.equipment import EquipmentBorrowForm
    from app.models.equipment import Equipment, EquipmentBorrow
    from app.models.user import User
    
    # 查询所有借用记录
    borrow_records = EquipmentBorrow.query.filter_by(borrower_id=current_user.id).order_by(EquipmentBorrow.created_at.desc()).all()
    
    form = EquipmentBorrowForm()
    # 获取所有可用设备作为选项
    form.equipment_id.choices = [(e.id, f'{e.code} - {e.name}') for e in Equipment.query.filter_by(status='available').all()]
    form.borrower_id.data = current_user.id
    
    if form.validate_on_submit():
        # 检查设备是否可用
        equipment = Equipment.query.get(form.equipment_id.data)
        if not equipment or equipment.status != 'available':
            flash('该设备当前不可用', 'danger')
            return redirect(url_for('system_extended.equipment_borrow'))
        
        borrow = EquipmentBorrow(
            equipment_id=form.equipment_id.data,
            borrower_id=current_user.id,
            borrow_time=form.borrow_time.data,
            expected_return_time=form.expected_return_time.data,
            purpose=form.purpose.data,
            remark=form.remark.data,
            status='borrowed'
        )
        
        # 更新设备状态为使用中
        equipment.status = 'in_use'
        
        db.session.add(borrow)
        try:
            db.session.commit()
            flash('设备借用申请提交成功，等待审批', 'success')
            return redirect(url_for('system_extended.equipment_borrow'))
        except Exception as e:
            db.session.rollback()
            flash(f'设备借用申请提交失败: {str(e)}', 'danger')
    
    return render_template('system/equipment_borrow.html', 
                           form=form, 
                           borrow_records=borrow_records)

# 场地预约
@system_extended.route('/venues', methods=['GET', 'POST'])
@login_required
@admin_required
def venues():
    """场地管理"""
    from app.models.venue import Venue
    
    # 查询所有场地
    venues = Venue.query.order_by(Venue.created_at.desc()).all()
    
    # 统计数据
    total_venues = len(venues)
    available_count = sum(1 for v in venues if v.status == 'available')
    booked_count = sum(1 for v in venues if v.status == 'booked')
    maintenance_count = sum(1 for v in venues if v.status == 'maintenance')
    closed_count = sum(1 for v in venues if v.status == 'closed')
    
    return render_template('system/venues.html', 
                           venues=venues,
                           total_venues=total_venues,
                           available_count=available_count,
                           booked_count=booked_count,
                           maintenance_count=maintenance_count,
                           closed_count=closed_count)

@system_extended.route('/venue_booking', methods=['GET', 'POST'])
@login_required
def venue_booking():
    """场地预约"""
    from app.models.venue import Venue, VenueBooking
    from flask_wtf import FlaskForm
    from wtforms import StringField, TextAreaField, SubmitField, SelectField, IntegerField, DateTimeField, HiddenField
    from wtforms.validators import DataRequired, Length, Optional, NumberRange, ValidationError
    
    class VenueBookingForm(FlaskForm):
        venue_id = SelectField('场地', coerce=int, validators=[DataRequired()])
        start_time = DateTimeField('开始时间', format='%Y-%m-%d %H:%M', validators=[DataRequired()])
        end_time = DateTimeField('结束时间', format='%Y-%m-%d %H:%M', validators=[DataRequired()])
        purpose = StringField('用途', validators=[DataRequired(), Length(1, 200)])
        attendees = IntegerField('参与人数', validators=[DataRequired(), NumberRange(min=1)])
        remark = TextAreaField('备注', validators=[Optional(), Length(0, 500)])
        submit = SubmitField('提交')
        
        def validate_end_time(self, field):
            if field.data and self.start_time.data and field.data <= self.start_time.data:
                raise ValidationError('结束时间必须晚于开始时间')
    
    # 查询用户的预约记录
    bookings = VenueBooking.query.filter_by(user_id=current_user.id).order_by(VenueBooking.created_at.desc()).all()
    
    form = VenueBookingForm()
    # 获取所有可用场地作为选项
    form.venue_id.choices = [(v.id, f'{v.code} - {v.name}') for v in Venue.query.filter_by(status='available').all()]
    
    if form.validate_on_submit():
        # 检查场地是否可用
        venue = Venue.query.get(form.venue_id.data)
        if not venue or venue.status != 'available':
            flash('该场地当前不可用', 'danger')
            return redirect(url_for('system_extended.venue_booking'))
        
        # 检查时间段是否已被预约
        conflicting_bookings = VenueBooking.query.filter(
            VenueBooking.venue_id == form.venue_id.data,
            VenueBooking.status == 'approved',
            VenueBooking.start_time < form.end_time.data,
            VenueBooking.end_time > form.start_time.data
        ).all()
        
        if conflicting_bookings:
            flash('该时间段已被预约，请选择其他时间', 'danger')
            return redirect(url_for('system_extended.venue_booking'))
        
        booking = VenueBooking(
            venue_id=form.venue_id.data,
            user_id=current_user.id,
            start_time=form.start_time.data,
            end_time=form.end_time.data,
            purpose=form.purpose.data,
            attendees=form.attendees.data,
            remark=form.remark.data,
            status='pending'
        )
        
        db.session.add(booking)
        try:
            db.session.commit()
            flash('场地预约申请提交成功，等待审批', 'success')
            return redirect(url_for('system_extended.venue_booking'))
        except Exception as e:
            db.session.rollback()
            flash(f'场地预约申请提交失败: {str(e)}', 'danger')
    
    return render_template('system/venue_booking.html', form=form, bookings=bookings)

@system_extended.route('/venue_approval', methods=['GET', 'POST'])
@login_required
@admin_required
def venue_approval():
    """预约审批"""
    from app.models.venue import Venue, VenueBooking
    
    # 查询所有待审批的预约
    pending_bookings = VenueBooking.query.filter_by(status='pending').order_by(VenueBooking.created_at.desc()).all()
    
    # 处理审批操作
    if request.method == 'POST':
        booking_id = request.form.get('booking_id')
        action = request.form.get('action')  # approve 或 reject
        comment = request.form.get('comment', '')
        
        if not booking_id or not action:
            flash('参数错误', 'danger')
            return redirect(url_for('system_extended.venue_approval'))
        
        booking = VenueBooking.query.get(booking_id)
        if not booking or booking.status != 'pending':
            flash('预约记录不存在或已处理', 'danger')
            return redirect(url_for('system_extended.venue_approval'))
        
        if action == 'approve':
            booking.status = 'approved'
            # 更新场地状态
            venue = Venue.query.get(booking.venue_id)
            if venue:
                venue.status = 'booked'
        elif action == 'reject':
            booking.status = 'rejected'
        else:
            flash('操作类型错误', 'danger')
            return redirect(url_for('system_extended.venue_approval'))
        
        booking.approver_id = current_user.id
        booking.approval_time = datetime.now()
        booking.approval_comment = comment
        
        try:
            db.session.commit()
            flash('审批操作成功', 'success')
        except Exception as e:
            db.session.rollback()
            flash(f'审批操作失败: {str(e)}', 'danger')
        
        return redirect(url_for('system_extended.venue_approval'))
    
    return render_template('system/venue_approval.html', pending_bookings=pending_bookings)

@system_extended.route('/check_certificate_image')
def check_certificate_image():
    """检查证书图片是否可以正常访问"""
    from flask import redirect, url_for, current_app
    
    try:
        # 使用正确的导入路径
        from app.models.unity_cert import UnifiedCertificate
        cert = UnifiedCertificate.query.get(1)  # 获取ID为1的证书
        
        if cert and cert.image_url:
            # 返回图片的直接URL
            return f"""
            <!DOCTYPE html>
            <html>
            <head><title>证书图片测试</title></head>
            <body>
                <h1>证书图片测试</h1>
                <p>证书ID: {cert.id}</p>
                <p>证书名称: {cert.name}</p>
                <p>图片路径: {cert.image_url}</p>
                <img src="{url_for('static', filename=cert.image_url)}" style="max-width: 100%;">
                <p><a href="{url_for('system.view_certificate', id=cert.id)}">返回证书详情</a></p>
            </body>
            </html>
            """
        else:
            return "证书未找到或没有图片"
    except Exception as e:
        return f"错误: {str(e)}"

@system_extended.route('/debug/certificate_image/<int:id>')
@login_required
def debug_certificate_image(id):
    """诊断证书图片问题"""
    if not current_user.is_administrator():
        flash('您没有权限访问此页面', 'danger')
        return redirect(url_for('system.literacy_certificates'))
    
    certificate = UnifiedCertificate.query.get_or_404(id)
    student = None
    if certificate.student_id:
        student = Student.query.get(certificate.student_id)
    
    # 构建上下文数据
    context = {
        'certificate': certificate,
        'student': student,
        'image_url_exists': bool(certificate.image_url),
        'file_exists': False,
        'image_path': None,
        'absolute_path': None,
        'static_url': None
    }
    
    # 检查文件是否存在
    if certificate.image_url:
        image_path = certificate.image_url
        absolute_path = os.path.join(current_app.root_path, 'static', image_path)
        context['image_path'] = image_path
        context['absolute_path'] = absolute_path
        context['file_exists'] = os.path.isfile(absolute_path)
        context['static_url'] = url_for('static', filename=image_path)
    
    # 如果是于睿的Java证书但没有图片，添加特殊处理
    is_yu_rui_cert = student and student.name == "于睿" and certificate.name and "Java" in certificate.name
    yu_rui_image_path = "uploads/certificates/cert_java_20240004.png"
    yu_rui_absolute_path = os.path.join(current_app.root_path, 'static', yu_rui_image_path)
    
    context['is_yu_rui_cert'] = is_yu_rui_cert
    context['yu_rui_image_exists'] = os.path.isfile(yu_rui_absolute_path)
    context['yu_rui_image_path'] = yu_rui_image_path
    
    return render_template('system/debug/certificate_image.html', **context)

@system_extended.route('/fix/certificate_image/<int:id>', methods=['POST'])
@login_required
def fix_certificate_image(id):
    """修复证书图片问题"""
    if not current_user.is_administrator():
        flash('您没有权限访问此页面', 'danger')
        return redirect(url_for('system.literacy_certificates'))
    
    certificate = UnifiedCertificate.query.get_or_404(id)
    
    # 获取表单数据
    action = request.form.get('action')
    
    if action == 'update_path':
        # 更新图片路径
        new_path = request.form.get('new_path')
        if new_path:
            # 验证文件存在
            absolute_path = os.path.join(current_app.root_path, 'static', new_path)
            if os.path.isfile(absolute_path):
                certificate.image_url = new_path
                db.session.commit()
                flash(f'证书图片路径已更新为: {new_path}', 'success')
            else:
                flash(f'文件不存在: {absolute_path}', 'danger')
    
    elif action == 'use_yu_rui_cert':
        # 使用于睿的Java证书图片
        yu_rui_image_path = "uploads/certificates/cert_java_20240004.png"
        absolute_path = os.path.join(current_app.root_path, 'static', yu_rui_image_path)
        
        if os.path.isfile(absolute_path):
            certificate.image_url = yu_rui_image_path
            db.session.commit()
            flash(f'已将证书图片设置为于睿的Java证书图片', 'success')
        else:
            flash(f'于睿证书图片文件不存在: {absolute_path}', 'danger')
    
    elif action == 'clear_path':
        # 清除图片路径
        certificate.image_url = None
        db.session.commit()
        flash('已清除证书图片路径', 'success')
    
    elif action == 'upload_image':
        # 处理图片上传
        if 'image_file' not in request.files:
            flash('没有文件被上传', 'danger')
            return redirect(url_for('system_extended.debug_certificate_image', id=id))
        
        file = request.files['image_file']
        if file.filename == '':
            flash('没有选择文件', 'danger')
            return redirect(url_for('system_extended.debug_certificate_image', id=id))
        
        if file:
            # 确保上传目录存在
            upload_folder = os.path.join(current_app.root_path, 'static', 'uploads', 'certificates')
            os.makedirs(upload_folder, exist_ok=True)
            
            # 生成安全的文件名
            filename = secure_filename(file.filename)
            # 添加前缀，确保唯一性
            safe_filename = f"cert_{id}_{filename}"
            file_path = os.path.join(upload_folder, safe_filename)
            
            # 保存文件
            file.save(file_path)
            
            # 更新证书记录
            relative_path = os.path.join('uploads', 'certificates', safe_filename)
            certificate.image_url = relative_path.replace('\\', '/')  # 确保使用正斜杠
            db.session.commit()
            flash(f'证书图片已上传并更新: {safe_filename}', 'success')
    
    return redirect(url_for('system_extended.debug_certificate_image', id=id))