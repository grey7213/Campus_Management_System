from app import create_app, db
from app.models.literacy_certificate import LiteracyCertificate
from sqlalchemy import inspect, text

app = create_app()

with app.app_context():
    # 获取检查器
    inspector = inspect(db.engine)
    
    # 检查表是否存在
    if 'literacy_certificates' in inspector.get_table_names():
        # 删除现有表 - 使用text()函数包装SQL语句
        db.session.execute(text('DROP TABLE IF EXISTS literacy_certificates'))
        db.session.commit()
    
    # 创建表
    db.create_all()
