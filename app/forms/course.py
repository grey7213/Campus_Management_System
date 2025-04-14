from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, IntegerField, SelectField, SubmitField, FloatField, BooleanField
from wtforms.validators import DataRequired, Length, Optional, NumberRange, ValidationError
from app.models.course import Course

class CourseForm(FlaskForm):
    """课程表单"""
    code = StringField('课程代码', validators=[
        DataRequired(message='课程代码不能为空'),
        Length(min=2, max=20, message='课程代码长度必须在2-20个字符之间')
    ])
    name = StringField('课程名称', validators=[
        DataRequired(message='课程名称不能为空'),
        Length(max=100, message='课程名称长度不能超过100个字符')
    ])
    credits = FloatField('学分', validators=[
        DataRequired(message='学分不能为空'),
        NumberRange(min=0.5, max=10, message='学分必须在0.5-10之间')
    ])
    hours = IntegerField('课时', validators=[
        DataRequired(message='课时不能为空'),
        NumberRange(min=1, max=200, message='课时必须在1-200之间')
    ])
    capacity = IntegerField('容量', validators=[
        DataRequired(message='容量不能为空'),
        NumberRange(min=1, max=500, message='容量必须在1-500之间')
    ])
    semester = SelectField('学期', choices=[
        ('', '请选择学期'),
        ('2023-2024-1', '2023-2024学年第一学期'),
        ('2023-2024-2', '2023-2024学年第二学期'),
        ('2024-2025-1', '2024-2025学年第一学期'),
        ('2024-2025-2', '2024-2025学年第二学期')
    ], validators=[DataRequired(message='请选择学期')])
    teacher_id = SelectField('教师', coerce=int, validators=[Optional()])
    description = TextAreaField('课程描述', validators=[Optional(), Length(max=1000, message='课程描述长度不能超过1000个字符')])
    status = SelectField('状态', choices=[
        ('active', '可选'),
        ('inactive', '不可选'),
        ('ended', '已结课')
    ], validators=[DataRequired(message='请选择状态')])
    location = StringField('上课地点', validators=[Optional(), Length(max=100, message='上课地点长度不能超过100个字符')])
    schedule = StringField('上课时间', validators=[Optional(), Length(max=200, message='上课时间长度不能超过200个字符')])
    course_type = SelectField('课程类型', choices=[
        ('required', '必修课'),
        ('elective', '选修课'),
        ('optional', '任选课')
    ], validators=[DataRequired(message='请选择课程类型')])
    prerequisites = StringField('先修课程', validators=[Optional(), Length(max=200, message='先修课程长度不能超过200个字符')])
    allow_selection = SelectField('允许选课', choices=[
        ('yes', '允许'),
        ('no', '不允许')
    ], validators=[DataRequired(message='请选择是否允许选课')])
    target_grade = SelectField('面向年级', choices=[
        ('all', '所有年级'),
        ('freshman', '大一'),
        ('sophomore', '大二'),
        ('junior', '大三'),
        ('senior', '大四')
    ], validators=[DataRequired(message='请选择面向年级')])
    submit = SubmitField('保存')
    
    def __init__(self, *args, **kwargs):
        super(CourseForm, self).__init__(*args, **kwargs)
        self.original_code = None
        self.id = None
        
    def validate_code(self, field):
        """验证课程代码唯一性"""
        if hasattr(self, 'id') and self.id:
            # 编辑模式
            course = Course.query.filter(Course.id != self.id, Course.code == field.data).first()
        else:
            # 新增模式
            course = Course.query.filter_by(code=field.data).first()
            
        if course:
            raise ValidationError('该课程代码已被使用')
            
class EnrollmentForm(FlaskForm):
    """选课表单"""
    student_id = SelectField('学生', coerce=int, validators=[DataRequired(message='请选择学生')])
    status = SelectField('状态', choices=[
        ('enrolled', '已选'),
        ('pending', '待审核'),
        ('completed', '已完成'),
        ('dropped', '已退选')
    ], validators=[DataRequired(message='请选择状态')])
    grade = FloatField('成绩', validators=[Optional(), NumberRange(min=0, max=100, message='成绩必须在0-100之间')])
    comments = TextAreaField('评语', validators=[Optional(), Length(max=500, message='评语长度不能超过500个字符')])
    submit = SubmitField('保存') 