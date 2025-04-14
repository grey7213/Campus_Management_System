from datetime import datetime
from app import db

class Announcement(db.Model):
    """通知公告模型"""
    __tablename__ = 'announcements'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(128), nullable=False)
    content = db.Column(db.Text, nullable=False)
    author_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    status = db.Column(db.String(20), default='published')  # published, draft, revoked
    priority = db.Column(db.Integer, default=0)  # 优先级，数字越大优先级越高
    start_date = db.Column(db.Date, default=datetime.utcnow)  # 公告开始日期
    end_date = db.Column(db.Date)  # 公告结束日期，为空表示永久有效
    target_type = db.Column(db.String(20), default='all')  # all, student, teacher, admin
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # 关联
    author = db.relationship('User', backref='announcements')
    
    def __repr__(self):
        return f'<Announcement {self.title}>'
    
    @property
    def is_active(self):
        """检查公告是否在有效期内且状态为已发布"""
        today = datetime.utcnow().date()
        # 检查状态是否为已发布
        if self.status != 'published':
            return False
        # 检查是否在有效期内
        if self.start_date and self.start_date > today:
            return False
        if self.end_date and self.end_date < today:
            return False
        return True