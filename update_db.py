from app import create_app, db
from sqlalchemy import text

app = create_app('default')
with app.app_context():
    try:
        # 添加course_type字段
        db.session.execute(text('ALTER TABLE courses ADD COLUMN course_type VARCHAR(20) DEFAULT "required"'))
        print("成功添加course_type字段")
    except Exception as e:
        print(f"添加course_type字段时出错: {e}")
    
    try:
        # 添加capacity字段
        db.session.execute(text('ALTER TABLE courses ADD COLUMN capacity INTEGER DEFAULT 50'))
        print("成功添加capacity字段")
    except Exception as e:
        print(f"添加capacity字段时出错: {e}")
    
    try:
        # 添加avatar_url字段到users表
        db.session.execute(text('ALTER TABLE users ADD COLUMN avatar_url VARCHAR(256) DEFAULT "static/img/default_avatar.png"'))
        print("成功添加avatar_url字段到users表")
    except Exception as e:
        print(f"添加avatar_url字段时出错: {e}")
    
    # 提交更改
    db.session.commit()
    print("数据库更新完成") 