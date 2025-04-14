from flask import Blueprint, render_template, redirect, url_for
from flask_login import current_user

main = Blueprint('main', __name__)

@main.route('/')
def index():
    """网站首页"""
    if current_user.is_authenticated:
        if current_user.is_administrator():
            return redirect(url_for('admin.dashboard'))
        elif current_user.is_teacher():
            return redirect(url_for('teacher.dashboard'))
        else:
            return redirect(url_for('student.dashboard'))
    return render_template('index.html')

@main.route('/about')
def about():
    """关于页面"""
    return render_template('about.html')

@main.route('/contact')
def contact():
    """联系我们"""
    return render_template('contact.html')

@main.route('/test')
def test():
    """测试路由"""
    return "校园管理系统测试成功！"