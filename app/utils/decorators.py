from functools import wraps
from flask import abort
from flask_login import current_user
from app.models.user import Permission

def permission_required(permission):
    """权限检查装饰器"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not current_user.can(permission):
                abort(403)
            return f(*args, **kwargs)
        return decorated_function
    return decorator

def admin_required(f):
    """管理员权限检查装饰器"""
    return permission_required(Permission.ADMIN)(f)

def teacher_required(f):
    """教师权限检查装饰器"""
    return permission_required(Permission.TEACHER)(f)

def student_required(f):
    """学生权限检查装饰器"""
    return permission_required(Permission.STUDENT)(f)