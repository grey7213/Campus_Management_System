"""
更新证书区块链启用状态
"""
from app import create_app, db
from app.models.literacy import LiteracyCertificate

def update_blockchain_enabled():
    """将所有证书的blockchain_enabled字段设置为True"""
    app = create_app()
    with app.app_context():
        # 获取所有证书
        certificates = LiteracyCertificate.query.all()
        print(f"找到 {len(certificates)} 个证书记录")
        
        for cert in certificates:
            print(f"正在更新证书 ID: {cert.id}, 名称: {cert.name}")
            # 将blockchain_enabled字段设置为True
            if hasattr(cert, 'blockchain_enabled'):
                cert.blockchain_enabled = True
                print(f"  blockchain_enabled 设置为 True")
            else:
                print(f"  注意: 证书对象没有 blockchain_enabled 属性")
                # 尝试使用__setattr__方法
                try:
                    setattr(cert, 'blockchain_enabled', True)
                    print("  已使用setattr添加blockchain_enabled属性")
                except Exception as e:
                    print(f"  无法设置属性: {str(e)}")
            
            # 检查并修正blockchain_certificate_id
            if hasattr(cert, 'blockchain_certificate_id'):
                if cert.blockchain_certificate_id is not None and cert.blockchain_certificate_id.strip() == '':
                    cert.blockchain_certificate_id = None
                print(f"  blockchain_certificate_id: {cert.blockchain_certificate_id}")
        
        # 提交更改
        db.session.commit()
        print("所有证书记录已更新")

if __name__ == "__main__":
    update_blockchain_enabled() 