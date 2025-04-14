from app import db
from datetime import datetime
import json

class SystemSetting(db.Model):
    """系统设置模型"""
    __tablename__ = 'system_settings'
    
    id = db.Column(db.Integer, primary_key=True)
    key = db.Column(db.String(64), unique=True, index=True, nullable=False)
    value = db.Column(db.Text)
    value_type = db.Column(db.String(32), default='string')  # string, int, float, boolean, json
    description = db.Column(db.String(255))
    updated_at = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now)
    
    def __init__(self, key, value, value_type='string', description=None):
        self.key = key
        self.value = self._format_value(value, value_type)
        self.value_type = value_type
        self.description = description
    
    def _format_value(self, value, value_type):
        """根据类型格式化值"""
        if value_type == 'json' and not isinstance(value, str):
            return json.dumps(value)
        return str(value)
    
    def get_value(self):
        """根据类型返回值"""
        if self.value is None:
            return None
            
        if self.value_type == 'int':
            return int(self.value)
        elif self.value_type == 'float':
            return float(self.value)
        elif self.value_type == 'boolean':
            return self.value.lower() in ('true', '1', 'yes', 'y')
        elif self.value_type == 'json':
            return json.loads(self.value)
        else:
            return self.value
    
    def __repr__(self):
        return f"<SystemSetting {self.key}>"


# 系统设置管理类
class SystemSettingService:
    """系统设置管理服务"""
    
    @staticmethod
    def get(key, default=None):
        """获取设置值"""
        setting = SystemSetting.query.filter_by(key=key).first()
        if setting is None:
            return default
        return setting.get_value()
    
    @staticmethod
    def set(key, value, value_type='string', description=None):
        """设置值"""
        setting = SystemSetting.query.filter_by(key=key).first()
        if setting is None:
            setting = SystemSetting(key=key, value=value, value_type=value_type, description=description)
            db.session.add(setting)
        else:
            setting.value = setting._format_value(value, value_type)
            setting.value_type = value_type
            if description:
                setting.description = description
        db.session.commit()
        return setting
    
    @staticmethod
    def delete(key):
        """删除设置"""
        setting = SystemSetting.query.filter_by(key=key).first()
        if setting:
            db.session.delete(setting)
            db.session.commit()
            return True
        return False
    
    @staticmethod
    def get_all():
        """获取所有设置"""
        settings = SystemSetting.query.all()
        return {setting.key: setting.get_value() for setting in settings}
    
    @staticmethod
    def get_dict():
        """获取所有系统设置作为字典，键为设置的key，值为设置的值"""
        settings_dict = {}
        for setting in SystemSetting.query.all():
            settings_dict[setting.key] = setting.get_value()
        return settings_dict


# 初始化默认设置
def init_default_settings():
    """初始化默认的系统设置"""
    default_settings = [
        # 基本设置
        {'key': 'site_name', 'value': '智证融合', 'value_type': 'string', 'description': '系统名称'},
        {'key': 'school_name', 'value': '示例大学', 'value_type': 'string', 'description': '学校名称'},
        {'key': 'contact_email', 'value': 'admin@example.com', 'value_type': 'string', 'description': '联系邮箱'},
        {'key': 'current_semester', 'value': '2023-2024-2', 'value_type': 'string', 'description': '当前学期'},
        {'key': 'items_per_page', 'value': '10', 'value_type': 'int', 'description': '每页显示条目数'},
        {'key': 'allow_registration', 'value': 'true', 'value_type': 'boolean', 'description': '允许用户注册'},
        {'key': 'allow_course_selection', 'value': 'true', 'value_type': 'boolean', 'description': '允许学生选课'},
        {'key': 'maintenance_mode', 'value': 'false', 'value_type': 'boolean', 'description': '维护模式'},
        
        # 外观设置
        {'key': 'theme_color', 'value': '#0d6efd', 'value_type': 'string', 'description': '主题颜色'},
        {'key': 'system_logo', 'value': '/static/img/logo.png', 'value_type': 'string', 'description': '系统Logo路径'},
        {'key': 'favicon', 'value': '/static/img/favicon.ico', 'value_type': 'string', 'description': '网站图标路径'},
        {'key': 'layout_style', 'value': 'default', 'value_type': 'string', 'description': '布局样式'},
        
        # 安全设置
        {'key': 'password_policy', 'value': 'strong', 'value_type': 'string', 'description': '密码策略'},
        {'key': 'session_timeout', 'value': '30', 'value_type': 'int', 'description': '会话超时时间(分钟)'},
        {'key': 'enable_two_factor', 'value': 'false', 'value_type': 'boolean', 'description': '启用双因素认证'},
        {'key': 'log_failed_logins', 'value': 'true', 'value_type': 'boolean', 'description': '记录登录失败'},
        {'key': 'lock_after_failures', 'value': 'true', 'value_type': 'boolean', 'description': '多次登录失败后锁定账户'},
        
        # 备份设置
        {'key': 'auto_backup', 'value': 'true', 'value_type': 'boolean', 'description': '启用自动备份'},
        {'key': 'backup_frequency', 'value': 'daily', 'value_type': 'string', 'description': '备份频率'},
        
        # 日志设置
        {'key': 'log_level', 'value': 'normal', 'value_type': 'string', 'description': '日志级别'},
    ]
    
    for setting in default_settings:
        # 仅在设置不存在时添加
        existing = SystemSetting.query.filter_by(key=setting['key']).first()
        if existing is None:
            SystemSettingService.set(
                setting['key'], 
                setting['value'], 
                setting['value_type'], 
                setting['description']
            ) 