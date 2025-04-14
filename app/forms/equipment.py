from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SubmitField, SelectField, FloatField, DateField, DateTimeField, HiddenField
from wtforms.validators import DataRequired, Length, Optional, NumberRange, ValidationError
from datetime import datetime, date

class EquipmentForm(FlaskForm):
    """设备表单"""
    code = StringField('设备编号', validators=[DataRequired(), Length(1, 20)])
    name = StringField('设备名称', validators=[DataRequired(), Length(1, 50)])
    type = SelectField('设备类型', choices=[
        ('computer', '计算机设备'),
        ('network', '网络设备'),
        ('office', '办公设备'),
        ('teaching', '教学设备'),
        ('laboratory', '实验设备'),
        ('other', '其他设备')
    ], validators=[DataRequired()])
    model = StringField('型号', validators=[Optional(), Length(0, 50)])
    brand = StringField('品牌', validators=[Optional(), Length(0, 50)])
    location = StringField('所在位置', validators=[DataRequired(), Length(1, 100)])
    purchase_date = DateField('购入日期', format='%Y-%m-%d', validators=[Optional()])
    price = FloatField('购入价格', validators=[Optional(), NumberRange(min=0)])
    status = SelectField('状态', choices=[
        ('available', '可用'),
        ('in_use', '使用中'),
        ('maintenance', '维修中'),
        ('scrapped', '已报废')
    ], validators=[DataRequired()])
    description = TextAreaField('设备描述', validators=[Optional(), Length(0, 500)])
    manager_id = SelectField('负责人', coerce=int, validators=[Optional()])
    submit = SubmitField('提交')
    
    def validate_purchase_date(self, field):
        if field.data and field.data > date.today():
            raise ValidationError('购入日期不能晚于今天')

class EquipmentBorrowForm(FlaskForm):
    """设备借用表单"""
    equipment_id = SelectField('设备', coerce=int, validators=[DataRequired()])
    borrower_id = HiddenField()
    borrow_time = DateTimeField('借用时间', format='%Y-%m-%d %H:%M', validators=[DataRequired()])
    expected_return_time = DateTimeField('预计归还时间', format='%Y-%m-%d %H:%M', validators=[DataRequired()])
    purpose = StringField('用途', validators=[DataRequired(), Length(1, 200)])
    remark = TextAreaField('备注', validators=[Optional(), Length(0, 500)])
    submit = SubmitField('提交')
    
    def validate_expected_return_time(self, field):
        if field.data and self.borrow_time.data and field.data <= self.borrow_time.data:
            raise ValidationError('预计归还时间必须晚于借用时间')

class EquipmentReturnForm(FlaskForm):
    """设备归还表单"""
    borrow_id = HiddenField(validators=[DataRequired()])
    actual_return_time = DateTimeField('实际归还时间', format='%Y-%m-%d %H:%M', default=datetime.now, validators=[DataRequired()])
    remark = TextAreaField('备注', validators=[Optional(), Length(0, 500)])
    submit = SubmitField('确认归还')

class EquipmentMaintenanceForm(FlaskForm):
    """设备维护表单"""
    equipment_id = SelectField('设备', coerce=int, validators=[DataRequired()])
    maintenance_type = SelectField('维护类型', choices=[
        ('routine', '例行维护'),
        ('repair', '故障维修')
    ], validators=[DataRequired()])
    start_time = DateTimeField('开始时间', format='%Y-%m-%d %H:%M', validators=[DataRequired()])
    end_time = DateTimeField('结束时间', format='%Y-%m-%d %H:%M', validators=[Optional()])
    maintainer = StringField('维护人员', validators=[DataRequired(), Length(1, 50)])
    cost = FloatField('维护费用', validators=[Optional(), NumberRange(min=0)])
    description = TextAreaField('维护描述', validators=[DataRequired(), Length(1, 500)])
    result = TextAreaField('维护结果', validators=[Optional(), Length(0, 500)])
    status = SelectField('状态', choices=[
        ('in_progress', '进行中'),
        ('completed', '已完成'),
        ('failed', '失败')
    ], validators=[DataRequired()])
    submit = SubmitField('提交')
    
    def validate_end_time(self, field):
        if field.data and self.start_time.data and field.data <= self.start_time.data:
            raise ValidationError('结束时间必须晚于开始时间')