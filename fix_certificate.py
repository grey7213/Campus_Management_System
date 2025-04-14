from app import create_app, db
from sqlalchemy import text

app = create_app()

with app.app_context():
    # 只更新现有记录的blockchain_enabled字段
    sql = text("""
    UPDATE literacy_certificates SET blockchain_enabled = 1 WHERE blockchain_certificate_id IS NOT NULL;
    """)
    
    db.session.execute(sql)
    db.session.commit()
    print("已更新证书的blockchain_enabled状态")
