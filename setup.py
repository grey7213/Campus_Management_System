from app import create_app, db
import os

def setup():
    # 确保 instance 目录存在
    if not os.path.exists('instance'):
        os.makedirs('instance')
    
    # 创建应用实例
    app = create_app()
    
    with app.app_context():
        # 创建数据库表
        db.create_all()
        
        # 初始化迁移
        from flask_migrate import stamp
        stamp()
        
        print("Setup completed successfully!")

if __name__ == '__main__':
    setup() 