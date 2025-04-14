from app import db
from datetime import datetime
from app.models.user import User

class LiteracyCertificate(db.Model):
    """素养证书模型"""
    __tablename__ = 'literacy_certificates'
    __table_args__ = {'extend_existing': True}
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(128), nullable=False)
    certificate_type = db.Column(db.String(64), nullable=False)
    issue_date = db.Column(db.Date, nullable=False)
    expiry_date = db.Column(db.Date)
    issuer = db.Column(db.String(128), nullable=False)
    description = db.Column(db.Text)
    proof_file = db.Column(db.String(256))  # 证明文件路径
    status = db.Column(db.String(20), default='pending')  # pending, approved, rejected
    rejected_reason = db.Column(db.Text)
    
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    verified_by = db.Column(db.Integer, db.ForeignKey('users.id'))
    verified_at = db.Column(db.DateTime)
    
    created_at = db.Column(db.DateTime, default=datetime.now)
    updated_at = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now)
    
    # 关联
    user = db.relationship('User', foreign_keys=[user_id], backref='certificates')
    verifier = db.relationship('User', foreign_keys=[verified_by])
    
    def __repr__(self):
        return f"<LiteracyCertificate {self.name}>"


class LiteracyReport(db.Model):
    """素养报告模型"""
    __tablename__ = 'literacy_reports'
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(128), nullable=False)
    report_type = db.Column(db.String(64), nullable=False)
    content = db.Column(db.Text)
    report_date = db.Column(db.Date, default=datetime.now)
    
    # 评估数据，存储为JSON格式
    evaluation_data = db.Column(db.Text)  # 存储评估结果的JSON字符串
    
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'))
    
    created_at = db.Column(db.DateTime, default=datetime.now)
    updated_at = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now)
    
    # 关联
    user = db.relationship('User', foreign_keys=[user_id], backref='literacy_reports')
    creator = db.relationship('User', foreign_keys=[created_by])
    
    def __repr__(self):
        return f"<LiteracyReport {self.title}>"


class LiteracyResource(db.Model):
    """素养资源模型"""
    __tablename__ = 'literacy_resources'
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(128), nullable=False)
    category = db.Column(db.String(64), nullable=False)
    description = db.Column(db.Text)
    content = db.Column(db.Text)
    file_path = db.Column(db.String(256))  # 资源文件路径
    thumbnail = db.Column(db.String(256))  # 缩略图路径
    views = db.Column(db.Integer, default=0)  # 浏览次数
    downloads = db.Column(db.Integer, default=0)  # 下载次数
    
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'))
    created_at = db.Column(db.DateTime, default=datetime.now)
    updated_at = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now)
    
    # 关联
    creator = db.relationship('User', foreign_keys=[created_by], backref='literacy_resources')
    
    def __repr__(self):
        return f"<LiteracyResource {self.title}>"


class LiteracyImage(db.Model):
    """素养图像模型 - 用于存储与素养相关的图像"""
    __tablename__ = 'literacy_images'
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(128))
    image_type = db.Column(db.String(64))  # 图像类型：证书模板、报告背景等
    file_path = db.Column(db.String(256), nullable=False)  # 图像文件路径
    description = db.Column(db.Text)
    is_active = db.Column(db.Boolean, default=True)
    
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'))
    created_at = db.Column(db.DateTime, default=datetime.now)
    updated_at = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now)
    
    # 关联
    creator = db.relationship('User', foreign_keys=[created_by])
    
    def __repr__(self):
        return f"<LiteracyImage {self.title}>" 