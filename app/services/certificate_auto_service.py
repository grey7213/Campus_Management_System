"""
证书自动生成服务
用于处理条件触发的证书生成
"""
from flask import current_app
from sqlalchemy import and_, or_
from datetime import datetime, date
import uuid
import random

from app import db
from app.models.unity_cert import UnifiedCertificate
from app.models.certificate_rule import CertificateRule
from app.models.student import Student
from app.services.blockchain_certificate_service import BlockchainCertificateService

class CertificateAutoService:
    """证书自动生成服务"""
    
    @classmethod
    def check_rules_for_student(cls, student_id):
        """检查学生是否满足任何证书生成规则
        
        Args:
            student_id: 学生ID
            
        Returns:
            生成的证书ID列表
        """
        generated_certificate_ids = []
        
        # 获取学生对象
        student = Student.query.get(student_id)
        if not student:
            current_app.logger.error(f"找不到学生 ID: {student_id}")
            return generated_certificate_ids
        
        # 获取学生已有的证书
        student_certificates = UnifiedCertificate.query.filter_by(
            student_id=student_id,
            status='approved'  # 只考虑已批准的证书
        ).all()
        
        # 获取所有活跃的规则
        active_rules = CertificateRule.query.filter_by(is_active=True).all()
        
        for rule in active_rules:
            # 检查规则是否已为该学生生成过证书
            # 避免重复生成
            existing_cert = UnifiedCertificate.query.filter(
                and_(
                    UnifiedCertificate.student_id == student_id,
                    UnifiedCertificate.name == rule.target_certificate_name,
                    UnifiedCertificate.certificate_type == rule.target_certificate_type
                )
            ).first()
            
            if existing_cert:
                current_app.logger.info(f"学生 {student_id} 已经有规则 {rule.id} 生成的证书")
                continue
            
            # 检查是否满足规则条件
            if cls._check_rule_condition(rule, student_certificates):
                # 满足条件，生成新证书
                certificate_id = cls._generate_certificate_from_rule(rule, student)
                if certificate_id:
                    generated_certificate_ids.append(certificate_id)
                    
        return generated_certificate_ids
    
    @classmethod
    def _check_rule_condition(cls, rule, student_certificates):
        """检查学生的证书是否满足规则条件
        
        Args:
            rule: 证书规则对象
            student_certificates: 学生已有的证书列表
            
        Returns:
            是否满足条件
        """
        if rule.condition_type == 'count':
            # 根据数量触发
            if not rule.required_certificate_types:
                # 如果没有指定类型，则计算所有证书数量
                return len(student_certificates) >= rule.required_certificate_count
            else:
                # 按类型统计
                required_types = rule.required_certificate_types.split(',')
                count = 0
                for cert in student_certificates:
                    if cert.certificate_type in required_types:
                        count += 1
                
                return count >= rule.required_certificate_count
        
        elif rule.condition_type == 'combination':
            # 组合条件 - 需要特定类型的证书各至少一个
            if not rule.required_certificate_types:
                return False
                
            required_types = rule.required_certificate_types.split(',')
            found_types = set()
            
            for cert in student_certificates:
                if cert.certificate_type in required_types:
                    found_types.add(cert.certificate_type)
            
            # 所有类型都找到了
            return len(found_types) == len(required_types)
        
        # 不支持的条件类型
        return False
    
    @classmethod
    def _generate_certificate_from_rule(cls, rule, student):
        """根据规则生成证书
        
        Args:
            rule: 证书规则对象
            student: 学生对象
            
        Returns:
            生成的证书ID或None
        """
        try:
            # 准备证书数据
            cert_data = {
                'name': rule.target_certificate_name,
                'certificate_type': rule.target_certificate_type,
                'issuer': rule.target_certificate_issuer or '智证校园系统',
                'issue_date': date.today(),
                'certificate_no': cls._generate_certificate_no(rule.target_certificate_type, student),
                'description': rule.target_certificate_description or f"自动生成的{rule.target_certificate_name}",
                'student_id': student.id,
                'user_id': student.user.id if student.user else None,
                'status': 'approved',  # 自动生成的证书默认为已批准
                'blockchain_enabled': rule.auto_blockchain,
                'created_at': datetime.now(),
                'updated_at': datetime.now()
            }
            
            # 创建证书
            certificate = UnifiedCertificate(**cert_data)
            db.session.add(certificate)
            db.session.commit()
            
            # 如果启用区块链，则上链
            if rule.auto_blockchain:
                BlockchainCertificateService.issue_blockchain_certificate(certificate.id)
            
            current_app.logger.info(f"为学生 {student.id} 自动生成证书: {certificate.id}")
            return certificate.id
            
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"自动生成证书失败: {str(e)}")
            return None
    
    @staticmethod
    def _generate_certificate_no(cert_type, student):
        """生成证书编号
        
        Args:
            cert_type: 证书类型
            student: 学生对象
            
        Returns:
            证书编号
        """
        # 类型缩写 + 年份 + 学号 + 随机4位数
        type_short = cert_type[:3].upper() if cert_type else "CRT"
        year = datetime.now().strftime('%Y')
        student_id = student.student_id if student else str(student.id)
        random_num = random.randint(1000, 9999)
        
        return f"{type_short}{year}{student_id}{random_num}"
    
    @classmethod
    def check_rules_for_all_students(cls):
        """为所有学生检查规则并生成证书
        
        Returns:
            生成的证书数量
        """
        total_generated = 0
        students = Student.query.all()
        
        for student in students:
            generated_ids = cls.check_rules_for_student(student.id)
            total_generated += len(generated_ids)
        
        return total_generated 