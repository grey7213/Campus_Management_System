from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SubmitField, SelectField, IntegerField, FloatField, DateField, PasswordField
from wtforms.validators import DataRequired, Length, Optional, NumberRange, Email
from app.models.teacher import Teacher
from app.models.user import User

class CourseForm(FlaskForm):
    """课程表单"""
    code = StringField('课程代码', validators=[
        DataRequired(message='课程代码不能为空'),
        Length(1, 20, message='课程代码长度必须在1-20个字符之间')
    ])
    name = StringField('课程名称', validators=[
        DataRequired(message='课程名称不能为空'),
        Length(1, 64, message='课程名称长度必须在1-64个字符之间')
    ])
    description = TextAreaField('课程描述')
    credits = FloatField('学分', validators=[
        DataRequired(message='学分不能为空'),
        NumberRange(min=0, message='学分必须大于等于0')
    ])
    hours = IntegerField('课时', validators=[
        DataRequired(message='课时不能为空'),
        NumberRange(min=0, message='课时必须大于等于0')
    ])
    semester = StringField('学期', validators=[
        DataRequired(message='学期不能为空'),
        Length(1, 20, message='学期长度必须在1-20个字符之间')
    ])
    max_students = IntegerField('最大学生数', validators=[
        DataRequired(message='最大学生数不能为空'),
        NumberRange(min=1, message='最大学生数必须大于等于1')
    ])
    status = SelectField('状态', choices=[
        ('active', '活跃'),
        ('inactive', '不活跃')
    ])
    submit = SubmitField('提交')

class TeacherForm(FlaskForm):
    """教师表单"""
    teacher_id = StringField('工号', validators=[DataRequired(), Length(min=3, max=20)])
    name = StringField('姓名', validators=[DataRequired(), Length(max=50)])
    gender = SelectField('性别', choices=[('男', '男'), ('女', '女')])
    title = SelectField('职称', choices=[
        ('讲师', '讲师'),
        ('助教', '助教'),
        ('副教授', '副教授'),
        ('教授', '教授'),
        ('其他', '其他')
    ])
    email = StringField('邮箱', validators=[DataRequired(), Email()])
    password = PasswordField('密码', validators=[Optional(), Length(min=6)])
    phone = StringField('电话', validators=[Optional(), Length(max=20)])
    department_id = SelectField('所属院系', coerce=int, validators=[Optional()])
    status = SelectField('状态', choices=[
        ('active', '在职'),
        ('leave', '休假'),
        ('retired', '退休')
    ], default='active')
    bio = TextAreaField('简介', validators=[Optional(), Length(max=500)])
    
    def validate_teacher_id(self, field):
        """验证工号唯一性"""
        teacher = Teacher.query.filter_by(teacher_id=field.data).first()
        if teacher and teacher.id != getattr(self, 'id', None):
            raise ValueError('该工号已被使用')
    
    def validate_email(self, field):
        """验证邮箱唯一性"""
        user = User.query.filter_by(email=field.data).first()
        teacher = getattr(self, 'teacher', None)
        if user and (not teacher or not teacher.user or teacher.user.id != user.id):
            raise ValueError('该邮箱已被使用')

class GradeForm(FlaskForm):
    """成绩表单"""
    score = FloatField('分数', validators=[
        DataRequired(message='分数不能为空'),
        NumberRange(min=0, max=100, message='分数必须在0-100之间')
    ])
    comments = TextAreaField('评语', validators=[
        Optional(),
        Length(0, 500, message='评语长度不能超过500个字符')
    ])
    submit = SubmitField('提交')