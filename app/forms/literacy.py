from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed, FileRequired
from wtforms import StringField, TextAreaField, SelectField, DateField, SubmitField, HiddenField
from wtforms.validators import DataRequired, Length, Optional
from datetime import date

class CertificateApplicationForm(FlaskForm):
    """素养证书申请表单"""
    name = StringField('证书名称', validators=[
        DataRequired(message='证书名称不能为空'),
        Length(1, 128, message='证书名称长度必须在1-128个字符之间')
    ])
    certificate_type = SelectField('证书类型', choices=[
        ('professional', '专业技能证书'),
        ('language', '语言能力证书'),
        ('competition', '竞赛获奖证书'),
        ('academic', '学术证书'),
        ('other', '其他证书')
    ], validators=[
        DataRequired(message='请选择证书类型')
    ])
    student_id = SelectField('持有人', validators=[
        DataRequired(message='请选择证书持有人')
    ], coerce=int)
    issue_date = DateField('颁发日期', validators=[
        DataRequired(message='颁发日期不能为空')
    ])
    expiry_date = DateField('有效期至', validators=[
        Optional()
    ])
    issuer = StringField('颁发机构', validators=[
        DataRequired(message='颁发机构不能为空'),
        Length(1, 128, message='颁发机构长度必须在1-128个字符之间')
    ])
    description = TextAreaField('证书描述', validators=[
        Optional()
    ])
    proof_file = FileField('证明文件', validators=[
        FileAllowed(['jpg', 'jpeg', 'png', 'pdf'], '只允许上传jpg, jpeg, png, pdf格式的文件')
    ])
    submit = SubmitField('提交申请')


class LiteracyReportForm(FlaskForm):
    """素养报告表单"""
    title = StringField('报告标题', validators=[
        DataRequired(message='报告标题不能为空'),
        Length(1, 128, message='报告标题长度必须在1-128个字符之间')
    ])
    report_type = SelectField('报告类型', choices=[
        ('comprehensive', '综合素养评估'),
        ('professional', '专业能力评估'),
        ('social', '社会实践评估'),
        ('innovation', '创新能力评估'),
        ('other', '其他评估')
    ], validators=[
        DataRequired(message='请选择报告类型')
    ])
    content = TextAreaField('报告内容', validators=[
        DataRequired(message='报告内容不能为空')
    ])
    report_date = DateField('报告日期', default=date.today, validators=[
        DataRequired(message='报告日期不能为空')
    ])
    evaluation_data = HiddenField('评估数据')
    user_id = HiddenField('用户ID')
    submit = SubmitField('保存报告')


class LiteracyResourceForm(FlaskForm):
    """素养资源表单"""
    title = StringField('资源标题', validators=[
        DataRequired(message='资源标题不能为空'),
        Length(1, 128, message='资源标题长度必须在1-128个字符之间')
    ])
    category = SelectField('资源类别', choices=[
        ('video', '视频资源'),
        ('document', '文档资源'),
        ('book', '书籍资源'),
        ('article', '文章资源'),
        ('course', '课程资源'),
        ('software', '软件资源'),
        ('other', '其他资源')
    ], validators=[
        DataRequired(message='请选择资源类别')
    ])
    description = TextAreaField('资源描述', validators=[
        Optional()
    ])
    content = TextAreaField('资源内容', validators=[
        Optional()
    ])
    resource_file = FileField('资源文件', validators=[
        Optional(),
        FileAllowed(['pdf', 'doc', 'docx', 'ppt', 'pptx', 'xls', 'xlsx', 'zip', 'rar', 'mp4', 'mp3'], 
                   '请上传允许的文件格式')
    ])
    thumbnail = FileField('缩略图', validators=[
        Optional(),
        FileAllowed(['jpg', 'jpeg', 'png'], '只允许上传jpg, jpeg, png格式的图片')
    ])
    submit = SubmitField('提交资源') 