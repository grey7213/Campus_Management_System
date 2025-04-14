from datetime import datetime
from app import db

class Venue(db.Model):
    """场地模型"""
    __tablename__ = 'venues'
    
    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(20), unique=True, index=True, comment='场地编号')
    name = db.Column(db.String(50), nullable=False, comment='场地名称')
    type = db.Column(db.String(20), nullable=False, comment='场地类型')
    location = db.Column(db.String(100), nullable=False, comment='所在位置')
    capacity = db.Column(db.Integer, nullable=False, comment='容纳人数')
    description = db.Column(db.Text, comment='场地描述')
    facilities = db.Column(db.Text, comment='配套设施')
    status = db.Column(db.String(20), default='available', comment='状态：available-可用，booked-已预约，maintenance-维护中，closed-关闭')
    manager_id = db.Column(db.Integer, db.ForeignKey('users.id'), comment='管理员ID')
    created_at = db.Column(db.DateTime, default=datetime.now, comment='创建时间')
    updated_at = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now, comment='更新时间')
    
    # 关系
    manager = db.relationship('User', backref=db.backref('managed_venues', lazy='dynamic'))
    bookings = db.relationship('VenueBooking', backref='venue', lazy='dynamic')
    
    def __repr__(self):
        return f'<Venue {self.name}>'

class VenueBooking(db.Model):
    """场地预约记录"""
    __tablename__ = 'venue_bookings'
    
    id = db.Column(db.Integer, primary_key=True)
    venue_id = db.Column(db.Integer, db.ForeignKey('venues.id'), nullable=False, comment='场地ID')
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, comment='预约人ID')
    start_time = db.Column(db.DateTime, nullable=False, comment='开始时间')
    end_time = db.Column(db.DateTime, nullable=False, comment='结束时间')
    purpose = db.Column(db.String(200), nullable=False, comment='用途')
    attendees = db.Column(db.Integer, default=0, comment='参与人数')
    status = db.Column(db.String(20), default='pending', comment='状态：pending-待审批，approved-已批准，rejected-已拒绝，cancelled-已取消')
    remark = db.Column(db.Text, comment='备注')
    approver_id = db.Column(db.Integer, db.ForeignKey('users.id'), comment='审批人ID')
    approval_time = db.Column(db.DateTime, comment='审批时间')
    approval_comment = db.Column(db.Text, comment='审批意见')
    created_at = db.Column(db.DateTime, default=datetime.now, comment='创建时间')
    updated_at = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now, comment='更新时间')
    
    # 关系
    user = db.relationship('User', foreign_keys=[user_id], backref=db.backref('venue_bookings', lazy='dynamic'))
    approver = db.relationship('User', foreign_keys=[approver_id], backref=db.backref('approved_bookings', lazy='dynamic'))
    
    def __repr__(self):
        return f'<VenueBooking {self.id}>'