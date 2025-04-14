"""
证书处理相关定时任务
"""
import os
from datetime import datetime, timedelta
from sqlalchemy import and_

from app import db, create_app
from app.models.literacy import LiteracyCertificate
from app.services.blockchain_certificate_service import BlockchainCertificateService
from app.models.user import User
from app.utils.logger import get_logger

logger = get_logger('certificate_tasks')

def auto_approve_certificates():
    """自动审批超过指定时间的待审核证书"""
    app = create_app()
    with app.app_context():
        # 获取系统管理员作为审批人
        admin = User.query.filter_by(is_administrator=True).first()
        admin_id = admin.id if admin else 1  # 如果没有管理员，使用ID=1作为默认值
        
        if not admin:
            logger.warning("No administrator found in the system, using default admin ID=1")
        
        # 计算时间阈值 - 24小时前
        threshold_time = datetime.now() - timedelta(hours=24)
        
        # 查找超过24小时的待审核证书
        pending_certificates = LiteracyCertificate.query.filter(
            and_(
                LiteracyCertificate.status == 'pending',
                LiteracyCertificate.created_at <= threshold_time
            )
        ).all()
        
        logger.info(f"Found {len(pending_certificates)} pending certificates to auto-approve")
        
        for cert in pending_certificates:
            try:
                # 更新证书状态
                cert.status = 'approved'
                cert.verified_by = admin_id
                cert.verified_at = datetime.now()
                
                # 如果证书启用了区块链，自动发布到区块链
                if hasattr(cert, 'blockchain_enabled') and cert.blockchain_enabled:
                    logger.info(f"Auto-issuing blockchain certificate for certificate ID: {cert.id}")
                    BlockchainCertificateService.issue_blockchain_certificate(cert.id)
                
                db.session.commit()
                logger.info(f"Auto-approved certificate ID: {cert.id}")
            except Exception as e:
                db.session.rollback()
                logger.error(f"Error auto-approving certificate ID: {cert.id}: {str(e)}")
        
        logger.info("Auto-approve certificates task completed")

if __name__ == "__main__":
    # 可以直接运行此脚本来执行定时任务
    auto_approve_certificates() 