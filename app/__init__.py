import os
from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_bootstrap import Bootstrap
from flask_moment import Moment
from flask_migrate import Migrate
from flask_wtf.csrf import CSRFProtect
from config import config
from flask_mail import Mail
from datetime import datetime
from flask_babel import Babel

db = SQLAlchemy()
login_manager = LoginManager()
login_manager.login_view = 'auth.login'
login_manager.login_message = '请先登录'
login_manager.login_message_category = 'info'
bootstrap = Bootstrap()
moment = Moment()
migrate = Migrate()
csrf = CSRFProtect()
mail = Mail()
babel = Babel()

# 错误处理函数
def forbidden(e):
    return render_template('errors/403.html'), 403

def page_not_found(e):
    return render_template('errors/404.html'), 404

def internal_server_error(e):
    return render_template('errors/500.html'), 500

def create_app(config_name='default'):
    """创建Flask应用实例"""
    # 打印配置名称
    print(f"Creating app with config: {config_name}")
    
    app = Flask(__name__)
    app.config.from_object(config[config_name])
    config[config_name].init_app(app)
    
    # 初始化扩展
    bootstrap.init_app(app)
    db.init_app(app)
    migrate.init_app(app, db)
    moment.init_app(app)
    login_manager.init_app(app)
    mail.init_app(app)
    babel.init_app(app)
    csrf.init_app(app)
    
    # 配置登录视图
    login_manager.login_view = 'auth.login'
    
    # 注册蓝图
    try:
        print("Registering main blueprint")
        from app.routes.main import main
        print("Registering auth blueprint")
        from app.routes.auth import auth
        print("Registering admin blueprint")
        from app.routes.admin import admin
        print("Registering student blueprint")
        from app.routes.student import student
        print("Registering teacher blueprint")
        from app.routes.teacher import teacher
        print("Registering course blueprint")
        from app.routes.course import course
        print("Registering system blueprint")
        from app.routes.system import system
        print("Registering system extended blueprint")
        from app.routes.system_extended import system_extended
        print("Registering announcement blueprint")
        from app.routes.announcement import announcement
        print("Registering statistics blueprint")
        from app.routes.statistics import statistics
        # 注册微信蓝图
        from app.routes.wechat import wechat
        # 注册用户微信绑定蓝图
        from app.routes.user_wechat import user_wechat
    except Exception as e:
        print(f"Error importing blueprints: {e}")
        raise
    
    app.register_blueprint(main, url_prefix='/')
    app.register_blueprint(auth, url_prefix='/auth')
    app.register_blueprint(admin, url_prefix='/admin')
    app.register_blueprint(student, url_prefix='/student')
    app.register_blueprint(teacher, url_prefix='/teacher')
    app.register_blueprint(course, url_prefix='/course')
    app.register_blueprint(system, url_prefix='/system')
    app.register_blueprint(system_extended, url_prefix='/system_extended')
    app.register_blueprint(announcement, url_prefix='/announcement')
    app.register_blueprint(statistics, url_prefix='/statistics')
    # 注册微信蓝图
    app.register_blueprint(wechat, url_prefix='')
    # 注册用户微信绑定蓝图
    app.register_blueprint(user_wechat, url_prefix='')
    
    # 注册错误处理
    app.register_error_handler(403, forbidden)
    app.register_error_handler(404, page_not_found)
    app.register_error_handler(500, internal_server_error)
    
    # 注册上下文处理器，使系统设置在所有模板中可用
    @app.context_processor
    def inject_system_settings():
        from app.models.system import SystemSettingService
        return dict(settings=SystemSettingService)
    
    @app.context_processor
    def inject_now():
        """向所有模板注入now变量"""
        return {'now': datetime.now()}
    
    # 创建上传目录
    with app.app_context():
        uploads_dir = os.path.join(app.static_folder, 'uploads')
        if not os.path.exists(uploads_dir):
            os.makedirs(uploads_dir)
        
        # 创建证书上传目录
        certificates_dir = os.path.join(uploads_dir, 'certificates')
        if not os.path.exists(certificates_dir):
            os.makedirs(certificates_dir)
        
        # 创建素养资源上传目录
        literacy_resources_dir = os.path.join(uploads_dir, 'literacy_resources')
        if not os.path.exists(literacy_resources_dir):
            os.makedirs(literacy_resources_dir)
        
        # 创建默认管理员账号
        from app.models.user import User, Role
        from app.models.system import init_default_settings
        
        # 确保数据库表已创建
        db.create_all()
        
        # 初始化角色
        Role.insert_roles()
        
        # 初始化系统设置
        init_default_settings()
        
        # 检查是否已存在管理员账号
        admin_role = Role.query.filter_by(name='Administrator').first()
        if admin_role:
            admin_user = User.query.filter_by(role_id=admin_role.id).first()
            if not admin_user:
                # 创建默认管理员账号
                admin_user = User(
                    username='admin',
                    email='admin@example.com',
                    name='系统管理员',
                    password='admin123456',
                    role_id=admin_role.id,
                    is_active=True
                )
                db.session.add(admin_user)
                db.session.commit()
                print("Default administrator account created")
        
        # 初始化默认专业
        from app.models.major import Major
        Major.insert_default_majors()
    
    return app

# 仅在直接运行应用时初始化设置
def init_app_settings(app):
    with app.app_context():
        try:
            # 确保数据库表已创建
            db.create_all()
            # 初始化系统设置
            from app.models.system import init_default_settings
            init_default_settings()
            print("Default settings initialized")
        except Exception as e:
            print(f"Error initializing settings: {e}")