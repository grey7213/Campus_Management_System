"""
证书规则模型
用于定义基于条件自动生成证书的规则
"""
from app import db
from datetime import datetime

class CertificateRule(db.Model):
    """证书生成规则模型"""
    __tablename__ = 'certificate_rules'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(128), nullable=False)  # 规则名称
    description = db.Column(db.Text)  # 规则描述
    
    # 触发条件
    condition_type = db.Column(db.String(64))  # 条件类型：count, score, combination
    required_certificate_types = db.Column(db.String(256))  # 需要的证书类型，逗号分隔
    required_certificate_count = db.Column(db.Integer, default=1)  # 需要的证书数量
    required_certificate_score = db.Column(db.Float)  # 需要的证书分数
    
    # 生成的证书信息
    target_certificate_name = db.Column(db.String(128))  # 生成的证书名称
    target_certificate_type = db.Column(db.String(64))  # 生成的证书类型
    target_certificate_issuer = db.Column(db.String(128))  # 生成的证书颁发者
    target_certificate_description = db.Column(db.Text)  # 生成的证书描述
    
    # 是否自动上链
    auto_blockchain = db.Column(db.Boolean, default=True)  # 是否自动上链
    
    # 状态
    is_active = db.Column(db.Boolean, default=True)  # 是否启用规则
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def to_dict(self):
        """转换为字典"""
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'condition_type': self.condition_type,
            'required_certificate_types': self.required_certificate_types,
            'required_certificate_count': self.required_certificate_count,
            'required_certificate_score': self.required_certificate_score,
            'target_certificate_name': self.target_certificate_name,
            'target_certificate_type': self.target_certificate_type,
            'target_certificate_issuer': self.target_certificate_issuer,
            'target_certificate_description': self.target_certificate_description,
            'auto_blockchain': self.auto_blockchain,
            'is_active': self.is_active,
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M:%S'),
            'updated_at': self.updated_at.strftime('%Y-%m-%d %H:%M:%S'),
        }
    
    @staticmethod
    def from_dict(data):
        """从字典创建规则"""
        rule = CertificateRule()
        for field in ['name', 'description', 'condition_type', 
                     'required_certificate_types', 'required_certificate_count',
                     'required_certificate_score', 'target_certificate_name',
                     'target_certificate_type', 'target_certificate_issuer',
                     'target_certificate_description', 'auto_blockchain', 'is_active']:
            if field in data:
                setattr(rule, field, data[field])
        return rule 