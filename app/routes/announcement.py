from flask import Blueprint, render_template, redirect, url_for, flash, request, current_app
from flask_login import login_required, current_user
from app import db
from app.models.user import User, Role, Permission
from app.utils.decorators import admin_required
from datetime import datetime

announcement = Blueprint('announcement', __name__)

@announcement.route('/dashboard')
@login_required
@admin_required
def dashboard():
    """通知公告管理仪表盘"""
    return render_template('announcement/dashboard.html')

@announcement.route('/list')
@login_required
def list():
    """公告列表"""
    from app.models.announcement import Announcement
    
    page = request.args.get('page', 1, type=int)
    per_page = current_app.config.get('ITEMS_PER_PAGE', 10)
    
    # 根据用户角色筛选公告
    query = Announcement.query
    
    # 如果不是管理员，只显示已发布且在有效期内的公告
    if not current_user.is_admin:
        today = datetime.utcnow().date()
        query = query.filter(Announcement.status == 'published')
        query = query.filter((Announcement.start_date <= today) | (Announcement.start_date == None))
        query = query.filter((Announcement.end_date >= today) | (Announcement.end_date == None))
        
        # 根据目标类型筛选
        if hasattr(current_user, 'role') and current_user.role:
            role_name = current_user.role.name.lower()
            query = query.filter((Announcement.target_type == 'all') | (Announcement.target_type == role_name))
    
    # 按优先级和创建时间排序
    query = query.order_by(Announcement.priority.desc(), Announcement.created_at.desc())
    
    # 分页
    pagination = query.paginate(page=page, per_page=per_page, error_out=False)
    announcements = pagination.items
    
    return render_template('announcement/list.html', 
                          announcements=announcements, 
                          pagination=pagination)

@announcement.route('/create', methods=['GET', 'POST'])
@login_required
@admin_required
def create():
    """创建公告"""
    from app.models.announcement import Announcement
    from flask_wtf import FlaskForm
    from wtforms import StringField, TextAreaField, SelectField, IntegerField, DateField, SubmitField
    from wtforms.validators import DataRequired, Length, Optional, NumberRange
    
    class AnnouncementForm(FlaskForm):
        title = StringField('标题', validators=[DataRequired(), Length(1, 128)])
        content = TextAreaField('内容', validators=[DataRequired()])
        status = SelectField('状态', choices=[
            ('published', '已发布'),
            ('draft', '草稿'),
            ('revoked', '已撤销')
        ], default='published')
        priority = IntegerField('优先级', default=0, validators=[NumberRange(min=0, max=10)])
        start_date = DateField('开始日期', format='%Y-%m-%d', validators=[DataRequired()])
        end_date = DateField('结束日期', format='%Y-%m-%d', validators=[Optional()])
        target_type = SelectField('目标类型', choices=[
            ('all', '所有人'),
            ('student', '学生'),
            ('teacher', '教师'),
            ('admin', '管理员')
        ], default='all')
        submit = SubmitField('提交')
    
    form = AnnouncementForm()
    
    if form.validate_on_submit():
        announcement = Announcement(
            title=form.title.data,
            content=form.content.data,
            author_id=current_user.id,
            status=form.status.data,
            priority=form.priority.data,
            start_date=form.start_date.data,
            end_date=form.end_date.data,
            target_type=form.target_type.data
        )
        
        db.session.add(announcement)
        try:
            db.session.commit()
            flash('公告创建成功', 'success')
            return redirect(url_for('announcement.list'))
        except Exception as e:
            db.session.rollback()
            flash(f'公告创建失败: {str(e)}', 'danger')
    
    return render_template('announcement/create.html', form=form)

@announcement.route('/<int:id>/edit', methods=['GET', 'POST'])
@login_required
@admin_required
def edit(id):
    """编辑公告"""
    from app.models.announcement import Announcement
    from flask_wtf import FlaskForm
    from wtforms import StringField, TextAreaField, SelectField, IntegerField, DateField, SubmitField
    from wtforms.validators import DataRequired, Length, Optional, NumberRange
    
    announcement = Announcement.query.get_or_404(id)
    
    class AnnouncementForm(FlaskForm):
        title = StringField('标题', validators=[DataRequired(), Length(1, 128)])
        content = TextAreaField('内容', validators=[DataRequired()])
        status = SelectField('状态', choices=[
            ('published', '已发布'),
            ('draft', '草稿'),
            ('revoked', '已撤销')
        ])
        priority = IntegerField('优先级', validators=[NumberRange(min=0, max=10)])
        start_date = DateField('开始日期', format='%Y-%m-%d', validators=[DataRequired()])
        end_date = DateField('结束日期', format='%Y-%m-%d', validators=[Optional()])
        target_type = SelectField('目标类型', choices=[
            ('all', '所有人'),
            ('student', '学生'),
            ('teacher', '教师'),
            ('admin', '管理员')
        ])
        submit = SubmitField('提交')
    
    form = AnnouncementForm()
    
    if request.method == 'GET':
        form.title.data = announcement.title
        form.content.data = announcement.content
        form.status.data = announcement.status
        form.priority.data = announcement.priority
        form.start_date.data = announcement.start_date
        form.end_date.data = announcement.end_date
        form.target_type.data = announcement.target_type
    
    if form.validate_on_submit():
        announcement.title = form.title.data
        announcement.content = form.content.data
        announcement.status = form.status.data
        announcement.priority = form.priority.data
        announcement.start_date = form.start_date.data
        announcement.end_date = form.end_date.data
        announcement.target_type = form.target_type.data
        
        try:
            db.session.commit()
            flash('公告更新成功', 'success')
            return redirect(url_for('announcement.list'))
        except Exception as e:
            db.session.rollback()
            flash(f'公告更新失败: {str(e)}', 'danger')
    
    return render_template('announcement/edit.html', form=form, announcement=announcement)

@announcement.route('/<int:id>/delete', methods=['POST'])
@login_required
@admin_required
def delete(id):
    """删除公告"""
    from app.models.announcement import Announcement
    
    announcement = Announcement.query.get_or_404(id)
    
    try:
        db.session.delete(announcement)
        db.session.commit()
        flash('公告已删除', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'删除公告失败: {str(e)}', 'danger')
    
    return redirect(url_for('announcement.list'))