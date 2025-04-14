from flask import Blueprint, render_template, redirect, url_for, flash, request, current_app
from flask_login import login_user, logout_user, login_required, current_user
from app import db
from app.models.user import User
from app.forms.auth import (
    LoginForm, RegisterForm, PasswordResetRequestForm, 
    PasswordResetForm, ProfileUpdateForm, AvatarUploadForm, ChangePasswordForm
)
import os
from werkzeug.utils import secure_filename
import uuid

auth = Blueprint('auth', __name__)

@auth.route('/login', methods=['GET', 'POST'])
def login():
    """用户登录"""
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user is not None and user.verify_password(form.password.data):
            login_user(user, form.remember_me.data)
            next = request.args.get('next')
            if next is None or not next.startswith('/'):
                if user.is_administrator():
                    next = url_for('admin.dashboard')
                elif user.is_teacher():
                    next = url_for('teacher.dashboard')
                else:
                    next = url_for('student.dashboard')
            return redirect(next)
        flash('用户名或密码错误', 'danger')
    return render_template('auth/login.html', form=form)

@auth.route('/logout')
@login_required
def logout():
    """用户登出"""
    logout_user()
    flash('您已成功登出', 'success')
    return redirect(url_for('auth.login'))

@auth.route('/register', methods=['GET', 'POST'])
def register():
    """用户注册"""
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    
    form = RegisterForm()
    if form.validate_on_submit():
        user = User(
            username=form.username.data,
            email=form.email.data,
            name=form.name.data,
            phone=form.phone.data,
            password=form.password.data
        )
        db.session.add(user)
        db.session.commit()
        flash('注册成功，请登录', 'success')
        return redirect(url_for('auth.login'))
    return render_template('auth/register.html', form=form)

@auth.route('/reset', methods=['GET', 'POST'])
def password_reset_request():
    """密码重置请求"""
    if not current_user.is_anonymous:
        return redirect(url_for('main.index'))
    form = PasswordResetRequestForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data.lower()).first()
        if user:
            # 在实际应用中，这里应该发送重置密码的邮件
            # 简化版本，直接跳转到重置密码页面
            flash('重置密码的邮件已发送到您的邮箱', 'info')
            return redirect(url_for('auth.login'))
        else:
            flash('该邮箱未注册', 'warning')
    return render_template('auth/reset_password.html', form=form)

@auth.route('/reset/<token>', methods=['GET', 'POST'])
def password_reset(token):
    """密码重置"""
    if not current_user.is_anonymous:
        return redirect(url_for('main.index'))
    form = PasswordResetForm()
    if form.validate_on_submit():
        # 在实际应用中，这里应该验证token并重置密码
        # 简化版本，直接提示成功
        flash('密码已重置成功', 'success')
        return redirect(url_for('auth.login'))
    return render_template('auth/reset_password.html', form=form)

@auth.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    """显示用户个人资料页面"""
    profile_form = ProfileUpdateForm(current_user)
    avatar_form = AvatarUploadForm()
    password_form = ChangePasswordForm()
    
    if profile_form.validate_on_submit():
        current_user.name = profile_form.name.data
        current_user.email = profile_form.email.data
        current_user.phone = profile_form.phone.data
        db.session.commit()
        flash('个人资料更新成功', 'success')
        return redirect(url_for('auth.profile'))
    
    # 填充表单默认值
    if request.method == 'GET':
        profile_form.name.data = current_user.name
        profile_form.email.data = current_user.email
        profile_form.phone.data = current_user.phone
    
    return render_template('profile.html', 
                          profile_form=profile_form, 
                          avatar_form=avatar_form, 
                          password_form=password_form)

@auth.route('/upload_avatar', methods=['POST'])
@login_required
def upload_avatar():
    """处理用户头像上传"""
    form = AvatarUploadForm()
    
    if form.validate_on_submit():
        if form.avatar.data:
            # 确保文件名安全
            filename = secure_filename(form.avatar.data.filename)
            # 生成唯一文件名
            unique_filename = f"{uuid.uuid4().hex}_{filename}"
            
            # 确保上传目录存在
            avatar_dir = os.path.join(current_app.static_folder, 'uploads', 'avatars')
            os.makedirs(avatar_dir, exist_ok=True)
            
            # 保存文件
            file_path = os.path.join(avatar_dir, unique_filename)
            form.avatar.data.save(file_path)
            
            # 更新用户头像地址
            relative_path = f"static/uploads/avatars/{unique_filename}"
            current_user.avatar_url = relative_path
            db.session.commit()
            
            flash('头像上传成功', 'success')
        else:
            flash('请选择一个文件', 'danger')
    else:
        for field, errors in form.errors.items():
            for error in errors:
                flash(f"{getattr(form, field).label.text}: {error}", 'danger')
    
    return redirect(url_for('auth.profile'))

@auth.route('/update_profile', methods=['POST'])
@login_required
def update_profile():
    """更新用户个人资料"""
    form = ProfileUpdateForm(current_user)
    
    if form.validate_on_submit():
        current_user.name = form.name.data
        current_user.email = form.email.data
        current_user.phone = form.phone.data
        db.session.commit()
        flash('个人资料更新成功', 'success')
    else:
        for field, errors in form.errors.items():
            for error in errors:
                flash(f"{getattr(form, field).label.text}: {error}", 'danger')
    
    return redirect(url_for('auth.profile'))

@auth.route('/change_password', methods=['POST'])
@login_required
def change_password():
    """修改用户密码"""
    form = ChangePasswordForm()
    
    if form.validate_on_submit():
        if current_user.verify_password(form.old_password.data):
            current_user.password = form.new_password.data
            db.session.commit()
            flash('密码修改成功', 'success')
        else:
            flash('当前密码错误', 'danger')
    else:
        for field, errors in form.errors.items():
            for error in errors:
                flash(f"{getattr(form, field).label.text}: {error}", 'danger')
    
    return redirect(url_for('auth.profile'))