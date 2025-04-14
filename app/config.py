import os

class Config:
    """基础配置"""
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-key-2024'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    MAIL_SERVER = os.environ.get('MAIL_SERVER', 'smtp.example.com')
    MAIL_PORT = int(os.environ.get('MAIL_PORT', '587'))
    MAIL_USE_TLS = os.environ.get('MAIL_USE_TLS', 'true').lower() in ['true', 'on', '1']
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
    ADMIN_MAIL = os.environ.get('ADMIN_MAIL', 'admin@example.com')
    UPLOAD_FOLDER = 'uploads/certificates'
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB限制
    
    @staticmethod
    def init_app(app):
        pass 