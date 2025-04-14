"""
统一证书模型
确保应用中所有位置使用同一个证书定义模型
"""
from app import db
from datetime import datetime
from sqlalchemy.orm import relationship

# 定义一个完整的证书模型，包含所有可能的属性
class UnifiedCertificate(db.Model):
    """统一的证书模型"""
    __tablename__ = 'literacy_certificates'
    __table_args__ = {'extend_existing': True}  # 关键: 允许扩展已存在的表
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(128), nullable=False)  # 证书名称
    certificate_type = db.Column(db.String(32), default='other')  # 证书类型
    issuer = db.Column(db.String(128))  # 颁发机构
    issue_date = db.Column(db.Date)  # 颁发日期
    expiry_date = db.Column(db.Date)  # 过期日期
    certificate_no = db.Column(db.String(64))  # 证书编号
    description = db.Column(db.Text)  # 证书描述
    
    # 关联关系 - 只保留必要的关系
    student_id = db.Column(db.Integer, db.ForeignKey('students.id'))  # 学生ID
    
    # 状态信息
    status = db.Column(db.String(20), default='pending')  # 状态：pending, approved, rejected
    rejected_reason = db.Column(db.Text)  # 拒绝原因
    proof_file = db.Column(db.String(256))  # 证明文件路径
    image_url = db.Column(db.String(256))  # 证书图片URL
    
    # 区块链相关字段
    blockchain_enabled = db.Column(db.Boolean, default=True)  # 是否启用区块链
    blockchain_certificate_id = db.Column(db.String(66))  # 区块链上的证书ID
    blockchain_transaction_hash = db.Column(db.String(66))  # 区块链交易哈希
    blockchain_data_hash = db.Column(db.String(66))  # 证书数据哈希
    blockchain_verification_url = db.Column(db.String(256))  # 证书验证URL
    
    # 时间记录
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # 关系定义 - 仅保留基本关系
    student = relationship('Student', backref=db.backref('literacy_certificates', lazy='dynamic'))
    
    def __repr__(self):
        return f'<Certificate {self.name}>'
    
    def to_dict(self):
        """将证书数据转换为字典"""
        # 安全地获取学生信息
        student_name = None
        student_id_number = None
        if self.student:
            student_name = self.student.name
            student_id_number = self.student.student_id
        
        return {
            'id': self.id,
            'name': self.name,
            'certificate_type': self.certificate_type,
            'issuer': self.issuer,
            'issue_date': self.issue_date.isoformat() if self.issue_date else None,
            'certificate_no': self.certificate_no,
            'description': self.description,
            'student_id': self.student_id,
            'student_name': student_name,
            'student_id_number': student_id_number,
            'status': self.status,
            'image_url': self.image_url,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'blockchain_enabled': self.blockchain_enabled,
            'blockchain_certificate_id': self.blockchain_certificate_id,
            'blockchain_transaction_hash': self.blockchain_transaction_hash,
            'blockchain_verification_url': self.blockchain_verification_url
        }

# 为了向后兼容，提供别名
LiteracyCertificate = UnifiedCertificate 