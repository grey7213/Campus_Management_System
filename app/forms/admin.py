from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SubmitField, SelectField, IntegerField, BooleanField, PasswordField, HiddenField
from wtforms.validators import DataRequired, Length, Optional, Email, ValidationError
from app.models.user import User

class UserForm(FlaskForm):
    """用户表单"""
    id = HiddenField('ID')
    username = StringField('用户名', validators=[
        DataRequired(message='用户名不能为空'),
        Length(1, 64, message='用户名长度必须在1-64个字符之间')
    ])
    email = StringField('邮箱', validators=[
        DataRequired(message='邮箱不能为空'),
        Email(message='请输入有效的邮箱地址'),
        Length(1, 64, message='邮箱长度必须在1-64个字符之间')
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
        Optional(),
        Length(min=6, message='密码长度必须至少为6个字符')
    ])
    password2 = PasswordField('确认密码', validators=[
        Optional(),
        Length(min=6, message='密码长度必须至少为6个字符')
    ])
    role = SelectField('角色', coerce=int, validators=[
        DataRequired(message='请选择角色')
    ])
    is_active = BooleanField('激活状态')
    submit = SubmitField('提交')

    def validate_username(self, field):
        user = User.query.filter_by(username=field.data).first()
        if user and user.id != self.id.data:
            raise ValidationError('该用户名已被使用')

    def validate_email(self, field):
        user = User.query.filter_by(email=field.data).first()
        if user and user.id != self.id.data:
            raise ValidationError('该邮箱已被注册')

    def validate_password2(self, field):
        if self.password.data != field.data:
            raise ValidationError('两次输入的密码不一致')

class DepartmentForm(FlaskForm):
    """部门表单"""
    name = StringField('部门名称', validators=[
        DataRequired(message='部门名称不能为空'),
        Length(1, 64, message='部门名称长度必须在1-64个字符之间')
    ])
    code = StringField('部门代码', validators=[
        DataRequired(message='部门代码不能为空'),
        Length(1, 20, message='部门代码长度必须在1-20个字符之间')
    ])
    contact = StringField('联系方式', validators=[
        Optional(),
        Length(0, 100, message='联系方式长度不能超过100个字符')
    ])
    description = TextAreaField('部门描述')
    submit = SubmitField('提交')

class MajorForm(FlaskForm):
    """专业表单"""
    name = StringField('专业名称', validators=[
        DataRequired(message='专业名称不能为空'),
        Length(1, 64, message='专业名称长度必须在1-64个字符之间')
    ])
    code = StringField('专业代码', validators=[
        DataRequired(message='专业代码不能为空'),
        Length(1, 20, message='专业代码长度必须在1-20个字符之间')
    ])
    department_id = SelectField('所属部门', coerce=int, validators=[
        DataRequired(message='请选择所属部门')
    ])
    level = SelectField('专业级别', choices=[
        ('本科', '本科'),
        ('专科', '专科'),
        ('硕士', '硕士'),
        ('博士', '博士')
    ], validators=[
        DataRequired(message='请选择专业级别')
    ])
    years = IntegerField('学制年限', validators=[
        DataRequired(message='学制年限不能为空')
    ], default=4)
    status = SelectField('状态', choices=[
        ('active', '活跃'),
        ('inactive', '停用')
    ], validators=[
        DataRequired(message='请选择状态')
    ])
    description = TextAreaField('专业描述')
    submit = SubmitField('提交')

class ClassForm(FlaskForm):
    """班级表单"""
    name = StringField('班级名称', validators=[
        DataRequired(message='班级名称不能为空'),
        Length(1, 64, message='班级名称长度必须在1-64个字符之间')
    ])
    code = StringField('班级代码', validators=[
        DataRequired(message='班级代码不能为空'),
        Length(1, 20, message='班级代码长度必须在1-20个字符之间')
    ])
    major_id = SelectField('所属专业', coerce=int, validators=[
        DataRequired(message='请选择所属专业')
    ])
    grade = IntegerField('年级', validators=[
        DataRequired(message='年级不能为空')
    ])
    capacity = IntegerField('班级容量', validators=[
        DataRequired(message='班级容量不能为空')
    ])
    description = TextAreaField('班级描述', validators=[Optional()])
    submit = SubmitField('提交') 