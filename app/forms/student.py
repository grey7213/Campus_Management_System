from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, SelectField, DateField, TextAreaField
from wtforms.validators import DataRequired, Email, Length, Optional, ValidationError
from app.models.student import Student

class StudentForm(FlaskForm):
    """学生表单"""
    student_id = StringField('学号', validators=[
        DataRequired(message='学号不能为空'),
        Length(min=3, max=20, message='学号长度必须在3-20个字符之间')
    ])
    name = StringField('姓名', validators=[
        DataRequired(message='姓名不能为空'),
        Length(max=50, message='姓名长度不能超过50个字符')
    ])
    gender = SelectField('性别', choices=[
        ('male', '男'),
        ('female', '女'),
        ('other', '其他')
    ], validators=[DataRequired(message='请选择性别')])
    birthday = DateField('生日', format='%Y-%m-%d', validators=[Optional()])
    class_id = SelectField('班级', coerce=int, validators=[DataRequired(message='请选择班级')])
    email = StringField('邮箱', validators=[
        DataRequired(message='邮箱不能为空'),
        Email(message='请输入有效的邮箱地址'),
        Length(max=100, message='邮箱长度不能超过100个字符')
    ])
    password = PasswordField('密码', validators=[
        Optional(),
        Length(min=6, message='密码长度不能少于6个字符')
    ])
    phone = StringField('电话', validators=[
        Optional(),
        Length(max=20, message='电话长度不能超过20个字符')
    ])
    status = SelectField('状态', choices=[
        ('active', '在读'),
        ('suspended', '休学'),
        ('graduated', '毕业'),
        ('transferred', '转校')
    ], validators=[DataRequired(message='请选择状态')])
    address = StringField('地址', validators=[Optional(), Length(max=200, message='地址长度不能超过200个字符')])
    bio = TextAreaField('简介', validators=[Optional(), Length(max=500, message='简介长度不能超过500个字符')])
    submit = SubmitField('保存')
    
    def __init__(self, *args, **kwargs):
        super(StudentForm, self).__init__(*args, **kwargs)
        self.original_student_id = None
        self.id = None
        
    def validate_student_id(self, field):
        # 检查学号是否已存在
        if hasattr(self, 'id') and self.id:
            # 编辑模式
            student = Student.query.filter(Student.id != self.id, Student.student_id == field.data).first()
        else:
            # 新增模式
            student = Student.query.filter_by(student_id=field.data).first()
            
        if student:
            raise ValidationError('该学号已被使用')

class EnrollmentForm(FlaskForm):
    """选课表单"""
    course_id = SelectField('课程', coerce=int, validators=[DataRequired(message='请选择课程')])
    status = SelectField('状态', choices=[
        ('enrolled', '已选'),
        ('pending', '待审核'),
        ('completed', '已完成'),
        ('dropped', '已退选')
    ], validators=[DataRequired(message='请选择状态')])
    submit = SubmitField('保存') 