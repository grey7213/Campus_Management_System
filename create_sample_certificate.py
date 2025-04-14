from app import create_app, db
from app.models.student import Student
from app.models.user import User
from datetime import datetime, date
import hashlib
import uuid
from sqlalchemy import text

app = create_app()

def create_blockchain_certificate_example():
    with app.app_context():
        # 确保有学生和用户记录
        student = Student.query.first()
        user = User.query.first()
        
        if not student or not user:
            print("需要先创建学生和用户记录")
            return
        
        # 生成区块链ID和哈希
        cert_id = str(uuid.uuid4().hex)
        blockchain_id = "0x" + hashlib.sha256(f"demo-certificate-{cert_id}".encode()).hexdigest()
        tx_hash = "0x" + hashlib.sha256(f"transaction-{cert_id}".encode()).hexdigest()
        data_hash = hashlib.sha256(f"data-{cert_id}".encode()).hexdigest()
        
        # 直接执行SQL插入
        sql = text("""
        INSERT INTO literacy_certificates 
        (name, certificate_type, issuer, issue_date, certificate_no, description, 
         student_id, image_url, status, blockchain_certificate_id, 
         blockchain_transaction_hash, blockchain_data_hash, blockchain_verification_url, 
         created_at, updated_at, user_id) 
        VALUES 
        (:name, :type, :issuer, :date, :cert_no, :desc, :student_id, :image, :status,
         :bc_id, :tx_hash, :data_hash, :verify_url, :created, :updated, :user_id)
        """)
        
        db.session.execute(sql, {
            'name': "优秀程序设计能力证书",
            'type': "skill",
            'issuer': "校园技能认证中心",
            'date': date.today(),
            'cert_no': "CERT-2025-001",
            'desc': "该证书证明持有者具备优秀的程序设计能力，能够熟练运用多种编程语言解决实际问题。",
            'student_id': student.id,
            'image': "static/img/certificates/sample_certificate.jpg",
            'status': "approved",
            'bc_id': blockchain_id,
            'tx_hash': tx_hash,
            'data_hash': data_hash,
            'verify_url': f"/verify_certificate?id={blockchain_id}",
            'created': datetime.now(),
            'updated': datetime.now(),
            'user_id': user.id
        })
        
        db.session.commit()
        
        print(f"样例区块链证书已创建，区块链ID: {blockchain_id}")

if __name__ == "__main__":
    create_blockchain_certificate_example()
