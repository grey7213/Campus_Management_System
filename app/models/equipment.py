from datetime import datetime
from app import db

class Equipment(db.Model):
    """设备模型"""
    __tablename__ = 'equipments'
    
    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(20), unique=True, index=True, comment='设备编号')
    name = db.Column(db.String(50), nullable=False, comment='设备名称')
    type = db.Column(db.String(20), nullable=False, comment='设备类型')
    model = db.Column(db.String(50), comment='型号')
    brand = db.Column(db.String(50), comment='品牌')
    location = db.Column(db.String(100), nullable=False, comment='所在位置')
    purchase_date = db.Column(db.Date, comment='购入日期')
    price = db.Column(db.Numeric(10, 2), comment='购入价格')
    status = db.Column(db.String(20), default='available', comment='状态：available-可用，in_use-使用中，maintenance-维修中，scrapped-已报废')
    description = db.Column(db.Text, comment='设备描述')
    manager_id = db.Column(db.Integer, db.ForeignKey('users.id'), comment='负责人ID')
    created_at = db.Column(db.DateTime, default=datetime.now, comment='创建时间')
    updated_at = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now, comment='更新时间')
    
    # 关系
    manager = db.relationship('User', backref=db.backref('managed_equipments', lazy='dynamic'))
    borrow_records = db.relationship('EquipmentBorrow', backref='equipment', lazy='dynamic')
    maintenance_records = db.relationship('EquipmentMaintenance', backref='equipment', lazy='dynamic')
    
    def __repr__(self):
        return f'<Equipment {self.name}>'

class EquipmentBorrow(db.Model):
    """设备借用记录"""
    __tablename__ = 'equipment_borrows'
    
    id = db.Column(db.Integer, primary_key=True)
    equipment_id = db.Column(db.Integer, db.ForeignKey('equipments.id'), nullable=False, comment='设备ID')
    borrower_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, comment='借用人ID')
    borrow_time = db.Column(db.DateTime, nullable=False, comment='借用时间')
    expected_return_time = db.Column(db.DateTime, nullable=False, comment='预计归还时间')
    actual_return_time = db.Column(db.DateTime, comment='实际归还时间')
    purpose = db.Column(db.String(200), nullable=False, comment='用途')
    status = db.Column(db.String(20), default='borrowed', comment='状态：borrowed-已借出，returned-已归还，overdue-逾期未还')
    remark = db.Column(db.Text, comment='备注')
    approver_id = db.Column(db.Integer, db.ForeignKey('users.id'), comment='审批人ID')
    created_at = db.Column(db.DateTime, default=datetime.now, comment='创建时间')
    updated_at = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now, comment='更新时间')
    
    # 关系
    borrower = db.relationship('User', foreign_keys=[borrower_id], backref=db.backref('equipment_borrows', lazy='dynamic'))
    approver = db.relationship('User', foreign_keys=[approver_id], backref=db.backref('approved_equipment_borrows', lazy='dynamic'))
    
    def __repr__(self):
        return f'<EquipmentBorrow {self.id}>'

class EquipmentMaintenance(db.Model):
    """设备维护记录"""
    __tablename__ = 'equipment_maintenances'
    
    id = db.Column(db.Integer, primary_key=True)
    equipment_id = db.Column(db.Integer, db.ForeignKey('equipments.id'), nullable=False, comment='设备ID')
    maintenance_type = db.Column(db.String(20), nullable=False, comment='维护类型：routine-例行维护，repair-故障维修')
    start_time = db.Column(db.DateTime, nullable=False, comment='开始时间')
    end_time = db.Column(db.DateTime, comment='结束时间')
    maintainer = db.Column(db.String(50), nullable=False, comment='维护人员')
    cost = db.Column(db.Numeric(10, 2), default=0, comment='维护费用')
    description = db.Column(db.Text, nullable=False, comment='维护描述')
    result = db.Column(db.Text, comment='维护结果')
    status = db.Column(db.String(20), default='in_progress', comment='状态：in_progress-进行中，completed-已完成，failed-失败')
    created_at = db.Column(db.DateTime, default=datetime.now, comment='创建时间')
    updated_at = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now, comment='更新时间')
    
    def __repr__(self):
        return f'<EquipmentMaintenance {self.id}>'