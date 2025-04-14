from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import StringField, PasswordField, BooleanField, SubmitField, ValidationError
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError, Optional, Regexp
from app.models.user import User

class LoginForm(FlaskForm):
    """登录表单"""
    username = StringField('用户名', validators=[
        DataRequired(message='用户名不能为空'),
        Length(1, 64, message='用户名长度必须在1-64个字符之间')
    ])
    password = PasswordField('密码', validators=[
        DataRequired(message='密码不能为空')
    ])
    remember_me = BooleanField('记住我')
    submit = SubmitField('登录')

class RegisterForm(FlaskForm):
    """注册表单"""
    email = StringField('邮箱', validators=[
        DataRequired(message='邮箱不能为空'),
        Email(message='请输入有效的邮箱地址'),
        Length(1, 64, message='邮箱长度必须在1-64个字符之间')
    ])
    username = StringField('用户名', validators=[
        DataRequired(message='用户名不能为空'),
        Length(1, 64, message='用户名长度必须在1-64个字符之间')
    ])
    name = StringField('姓名', validators=[
        DataRequired(message='姓名不能为空'),
        Length(1, 64, message='姓名长度必须在1-64个字符之间')
    ])
    phone = StringField('电话', validators=[
        Optional(),
        Length(0, 20, message='电话长度不能超过20个字符')
    ])
    password = PasswordField('密码', validators=[
        DataRequired(message='密码不能为空'),
        Length(min=8, message='密码长度必须至少为8个字符')
    ])
    password2 = PasswordField('确认密码', validators=[
        DataRequired(message='确认密码不能为空'),
        EqualTo('password', message='两次输入的密码必须匹配')
    ])
    submit = SubmitField('注册')

    def validate_email(self, field):
        if User.query.filter_by(email=field.data).first():
            raise ValidationError('该邮箱已被注册')

    def validate_username(self, field):
        if User.query.filter_by(username=field.data).first():
            raise ValidationError('该用户名已被注册')

class PasswordResetRequestForm(FlaskForm):
    """密码重置请求表单"""
    email = StringField('邮箱', validators=[
        DataRequired(message='邮箱不能为空'),
        Email(message='请输入有效的邮箱地址'),
        Length(1, 64, message='邮箱长度必须在1-64个字符之间')
    ])
    submit = SubmitField('重置密码')

class PasswordResetForm(FlaskForm):
    """密码重置表单"""
    password = PasswordField('新密码', validators=[
        DataRequired(message='密码不能为空'),
        Length(min=8, message='密码长度必须至少为8个字符')
    ])
    password2 = PasswordField('确认密码', validators=[
        DataRequired(message='确认密码不能为空'),
        EqualTo('password', message='两次输入的密码必须匹配')
    ])
    submit = SubmitField('重置密码')

class ProfileUpdateForm(FlaskForm):
    """个人资料更新表单"""
    name = StringField('姓名', validators=[Length(0, 64)])
    email = StringField('电子邮箱', validators=[DataRequired(), Length(1, 64), Email()])
    phone = StringField('联系电话', validators=[Length(0, 20)])
    submit = SubmitField('保存修改')

    def __init__(self, user, *args, **kwargs):
        super(ProfileUpdateForm, self).__init__(*args, **kwargs)
        self.user = user

    def validate_email(self, field):
        if field.data != self.user.email and \
                User.query.filter_by(email=field.data).first():
            raise ValidationError('该邮箱已被注册')

class AvatarUploadForm(FlaskForm):
    """头像上传表单"""
    avatar = FileField('头像', validators=[
        FileAllowed(['jpg', 'jpeg', 'png', 'gif'], '只允许上传jpg, jpeg, png, gif格式的图片！')
    ])
    submit = SubmitField('上传头像')

class ChangePasswordForm(FlaskForm):
    """修改密码表单"""
    old_password = PasswordField('当前密码', validators=[DataRequired()])
    new_password = PasswordField('新密码', validators=[
        DataRequired(), Length(8, 30),
        Regexp('^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)',
               message='密码必须包含至少一个小写字母、一个大写字母和一个数字')
    ])
    confirm_password = PasswordField('确认新密码', validators=[
        DataRequired(), EqualTo('new_password', message='两次输入的密码不一致')
    ])
    submit = SubmitField('修改密码') 