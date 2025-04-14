from datetime import datetime
from app import db

class LiteracyCertificate(db.Model):
    """素养证书模型"""
    __tablename__ = 'literacy_certificates'
    __table_args__ = {'extend_existing': True}
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(128), nullable=False)  # 证书名称
    certificate_type = db.Column(db.String(32), default='other')  # 证书类型
    issuer = db.Column(db.String(128))  # 颁发机构
    issue_date = db.Column(db.Date)  # 颁发日期
    certificate_no = db.Column(db.String(64))  # 证书编号
    description = db.Column(db.Text)  # 证书描述
    student_id = db.Column(db.Integer, db.ForeignKey('students.id'))  # 学生ID
    image_url = db.Column(db.String(256))  # 证书图片URL
    status = db.Column(db.String(20), default='pending')  # 状态：pending, approved, rejected
    rejected_reason = db.Column(db.Text)  # 拒绝原因
    
    # 区块链相关字段
    blockchain_enabled = db.Column(db.Boolean, default=False)  # 是否启用区块链
    blockchain_certificate_id = db.Column(db.String(66))  # 区块链上的证书ID
    blockchain_transaction_hash = db.Column(db.String(66))  # 区块链交易哈希
    blockchain_data_hash = db.Column(db.String(66))  # 证书数据哈希
    blockchain_verification_url = db.Column(db.String(256))  # 证书验证URL
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # 只保留student关系
    student = db.relationship('Student', backref='literacy_certificates')
    
    def to_dict(self):
        """将证书数据转换为字典"""
        return {
            'id': self.id,
            'name': self.name,
            'certificate_type': self.certificate_type,
            'issuer': self.issuer,
            'issue_date': self.issue_date.isoformat() if self.issue_date else None,
            'certificate_no': self.certificate_no,
            'description': self.description,
            'student_id': self.student_id,
            'student_name': self.student.name if self.student else None,
            'student_id_number': self.student.student_id if self.student else None,
            'status': self.status,
            'image_url': self.image_url,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'blockchain_enabled': self.blockchain_enabled,
            'blockchain_certificate_id': self.blockchain_certificate_id,
            'blockchain_transaction_hash': self.blockchain_transaction_hash,
            'blockchain_verification_url': self.blockchain_verification_url
        }
    
    def __repr__(self):
        return f'<LiteracyCertificate {self.name}>' 