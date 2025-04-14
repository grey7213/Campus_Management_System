import os
from app import create_app
from app.models.user import User, Role, Permission
from app.models.student import Student, Class, Major
from app.models.teacher import Teacher, Department
from app.models.course import Course
from app import db

app = create_app(os.getenv('FLASK_CONFIG') or 'default')

@app.shell_context_processor
def make_shell_context():
    return dict(
        db=db, 
        User=User, 
        Role=Role, 
        Permission=Permission,
        Student=Student, 
        Class=Class, 
        Major=Major,
        Teacher=Teacher, 
        Department=Department,
        Course=Course
    )

@app.cli.command()
def init_db():
    """初始化数据库"""
    db.create_all()
    Role.insert_roles()
    print('数据库初始化完成')

if __name__ == '__main__':
    app.run(host='127.0.0.1', debug=True)