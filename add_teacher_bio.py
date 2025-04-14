from app import create_app, db
from sqlalchemy import text

app = create_app('default')
with app.app_context():
    try:
        # 添加 bio 字段到 teachers 表
        db.session.execute(text('ALTER TABLE teachers ADD COLUMN bio TEXT'))
        print("成功添加 bio 字段到 teachers 表")
        
        # 提交更改
        db.session.commit()
        print("数据库更新完成")
    except Exception as e:
        print(f"更新数据库时出错: {e}")
        db.session.rollback() 