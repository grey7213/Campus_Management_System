"""
模拟区块链证书创建脚本
用于生成测试数据
"""
from app import create_app, db
from app.models.literacy import LiteracyCertificate
from app.models.student import Student
from app.services.mock_blockchain_service import MockBlockchainService
from datetime import datetime, date
import random

app = create_app()

def create_mock_blockchain_certificate():
    with app.app_context():
        # 确保有学生记录
        student = Student.query.first()
        
        if not student:
            print("需要先创建学生记录")
            return
        
        # 证书类型
        cert_types = ['language', 'professional', 'competition', 'skill', 'other']
        
        # 创建证书数据
        cert_data = {
            'name': f"模拟区块链测试证书 {random.randint(1000, 9999)}",
            'certificate_type': random.choice(cert_types),
            'issuer': "智证融合演示系统",
            'issue_date': date.today(),
            'student_id': student.id,
            'user_id': student.user.id,  # 确保设置user_id
            'status': 'approved'
        }
        
        # 生成模拟区块链数据
        blockchain_data = MockBlockchainService.issue_certificate(cert_data)
        
        # 创建证书记录
        certificate = LiteracyCertificate(
            name=cert_data['name'],
            certificate_type=cert_data['certificate_type'],
            issuer=cert_data['issuer'],
            issue_date=cert_data['issue_date'],
            status='approved',
            student_id=cert_data['student_id'],
            user_id=cert_data['user_id'],
            certificate_no=f"MOCK-{random.randint(1000, 9999)}",
            description="这是一个通过模拟区块链服务创建的测试证书",
            blockchain_enabled=True,
            blockchain_certificate_id=blockchain_data['certificate_id'],
            blockchain_transaction_hash=blockchain_data['transaction_hash'],
            blockchain_data_hash=blockchain_data['data_hash'],
            blockchain_verification_url=f"/system/verify_certificate?id={blockchain_data['certificate_id']}",
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        
        db.session.add(certificate)
        db.session.commit()
        
        print(f"模拟区块链证书已创建")
        print(f"证书ID: {certificate.id}")
        print(f"区块链证书ID: {certificate.blockchain_certificate_id}")
        print(f"验证URL: {certificate.blockchain_verification_url}")

if __name__ == "__main__":
    create_mock_blockchain_certificate()
