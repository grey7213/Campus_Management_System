#!/usr/bin/env python
"""
证书日期修复工具
修复所有证书的错误日期
"""
from app import create_app, db
from datetime import datetime
from sqlalchemy import text

def fix_certificate_dates():
    """修复所有证书的日期问题"""
    app = create_app()
    with app.app_context():
        try:
            print("开始修复证书日期...")
            
            # 创建当前日期和目标日期
            current_date = datetime.now().date()
            target_date = datetime(2024, 4, 10).date()
            target_datetime = datetime(2024, 4, 10)
            
            # 修复发布日期 - 未来日期的证书
            issue_date_sql = text("""
                UPDATE literacy_certificates
                SET issue_date = :target_date
                WHERE issue_date > :current_date
            """)
            
            result = db.session.execute(issue_date_sql, {
                'target_date': target_date,
                'current_date': current_date
            })
            
            future_issue_dates_fixed = result.rowcount
            print(f"已修复 {future_issue_dates_fixed} 个未来颁发日期")
            
            # 修复申请时间 - created_at字段
            created_at_sql = text("""
                UPDATE literacy_certificates
                SET created_at = :target_datetime
                WHERE DATE(created_at) > :current_date
            """)
            
            result = db.session.execute(created_at_sql, {
                'target_datetime': target_datetime,
                'current_date': current_date
            })
            
            future_created_at_fixed = result.rowcount
            print(f"已修复 {future_created_at_fixed} 个未来申请时间")
            
            # 提交更改
            db.session.commit()
            print(f"成功修复所有日期问题，总共修复 {future_issue_dates_fixed + future_created_at_fixed} 个问题")
            
            # 验证修复结果
            from app.models.unity_cert import UnifiedCertificate
            certs = UnifiedCertificate.query.all()
            print("\n证书日期验证:")
            for cert in certs:
                print(f"ID: {cert.id}, 名称: {cert.name}, 颁发日期: {cert.issue_date}, 申请时间: {cert.created_at}")
            
        except Exception as e:
            db.session.rollback()
            print(f"修复证书日期时出错: {e}")

if __name__ == "__main__":
    fix_certificate_dates() 