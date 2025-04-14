from app import create_app, db
from sqlalchemy import text

app = create_app('default')
with app.app_context():
    try:
        # 添加 level 字段到 majors 表
        db.session.execute(text('ALTER TABLE majors ADD COLUMN level VARCHAR(20) DEFAULT "本科"'))
        print("成功添加 level 字段到 majors 表")
        
        # 提交更改
        db.session.commit()
        print("数据库更新完成")
    except Exception as e:
        print(f"更新数据库时出错: {e}")
        db.session.rollback() 