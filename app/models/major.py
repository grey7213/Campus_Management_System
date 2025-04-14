from datetime import datetime
from app import db

class Major(db.Model):
    """专业模型"""
    __tablename__ = 'majors'
    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(20), unique=True, index=True)  # 专业代码
    name = db.Column(db.String(64))  # 专业名称
    description = db.Column(db.Text())  # 专业描述
    department_id = db.Column(db.Integer, db.ForeignKey('departments.id'))
    enrollment_year = db.Column(db.String(20))  # 招生年份
    level = db.Column(db.String(20), default='本科')  # 专业级别：本科、专科、硕士、博士
    years = db.Column(db.Integer, default=4)  # 学制年限
    status = db.Column(db.String(20), default='active')  # 专业状态：active, inactive
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # 关联
    classes = db.relationship('Class', backref='major', lazy='dynamic')
    department = db.relationship('Department', back_populates='majors')

    def __repr__(self):
        return f'<Major {self.name}>'

    def get_class_count(self):
        """获取专业班级总数"""
        return self.classes.count()

    def get_student_count(self):
        """获取专业学生总数"""
        count = 0
        for class_ in self.classes.all():
            count += class_.students.count()
        return count

    @staticmethod
    def insert_default_majors():
        """插入默认的专业信息"""
        default_majors = [
            {
                'code': 'CS001',
                'name': '计算机科学与技术',
                'description': '培养具备计算机科学与技术领域的基础理论知识和专业技能，能从事软件开发、系统设计、网络工程等工作的高级专门人才。'
            },
            {
                'code': 'CS002',
                'name': '软件工程',
                'description': '培养掌握软件开发方法、项目管理和质量保证等专业知识，能够从事软件设计、开发、测试和维护等工作的专业人才。'
            },
            {
                'code': 'CS003',
                'name': '人工智能',
                'description': '培养具备人工智能、机器学习、深度学习等领域的专业知识，能够从事智能系统开发和应用的创新型人才。'
            },
            {
                'code': 'CS004',
                'name': '网络工程',
                'description': '培养掌握计算机网络技术、网络安全、网络管理等专业知识，能够从事网络系统规划、设计和运维的专业人才。'
            },
            {
                'code': 'CS005',
                'name': '数据科学与大数据技术',
                'description': '培养具备数据采集、分析、挖掘和可视化等能力，能够从事大数据应用开发和数据分析的专业人才。'
            },
            {
                'code': 'CS006',
                'name': '物联网工程',
                'description': '培养掌握物联网技术、嵌入式系统、传感网络等专业知识，能够从事物联网应用开发和系统集成的专业人才。'
            },
            {
                'code': 'CS007',
                'name': '信息安全',
                'description': '培养具备网络安全、系统安全、密码学等专业知识，能够从事信息安全防护和安全系统开发的专业人才。'
            }
        ]

        for major_data in default_majors:
            # 检查专业是否已存在
            major = Major.query.filter_by(code=major_data['code']).first()
            if major is None:
                major = Major(
                    code=major_data['code'],
                    name=major_data['name'],
                    description=major_data['description']
                )
                db.session.add(major)
        
        try:
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            print(f'Error inserting default majors: {str(e)}') 