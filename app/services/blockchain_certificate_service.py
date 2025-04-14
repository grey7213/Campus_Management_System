import os
import json
import qrcode
from io import BytesIO
import base64
from datetime import datetime
from flask import url_for, current_app
from app import db
from app.utils.blockchain import BlockchainCertificate
from app.models.unity_cert import UnifiedCertificate
from flask_login import current_user
from app.services.mock_blockchain_service import MockBlockchainService

class BlockchainCertificateService:
    """区块链证书服务"""

    @classmethod
    def create_certificate(cls, certificate_data, enable_blockchain=True):
        """创建新证书
        
        Args:
            certificate_data: 证书数据字典
            enable_blockchain: 是否启用区块链
            
        Returns:
            创建的证书对象
        """
        try:
            # 确保user_id字段存在并且有值
            if 'user_id' not in certificate_data or certificate_data['user_id'] is None:
                raise ValueError("用户ID不能为空")
            
            # 创建证书实例
            certificate = UnifiedCertificate(
                name=certificate_data.get('name'),
                certificate_type=certificate_data.get('certificate_type'),
                issuer=certificate_data.get('issuer'),
                issue_date=certificate_data.get('issue_date'),
                certificate_no=certificate_data.get('certificate_no'),
                description=certificate_data.get('description'),
                image_url=certificate_data.get('image_url'),
                status='pending',
                # 明确设置user_id和student_id
                user_id=certificate_data.get('user_id'),  # 确保这一行存在且被正确处理
                student_id=certificate_data.get('student_id'),
                blockchain_enabled=enable_blockchain
            )
            
            # 添加并提交到数据库
            db.session.add(certificate)
            db.session.commit()
            
            return certificate
        
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"创建证书失败: {str(e)}")
            raise
    
    @classmethod
    def issue_blockchain_certificate(cls, certificate_id):
        """将证书上传到区块链
        
        Args:
            certificate_id: 证书ID
            
        Returns:
            更新的证书对象
        """
        certificate = UnifiedCertificate.query.get_or_404(certificate_id)
        
        # 只有已批准的证书才能上链
        if certificate.status != 'approved':
            return {'success': False, 'message': '只有已批准的证书才能上链'}
        
        try:
            # 检查是否使用模拟模式
            if current_app.config.get('BLOCKCHAIN_SIMULATION_MODE', False):
                # 使用模拟服务
                cert_data = certificate.to_dict()
                result = MockBlockchainService.issue_certificate(cert_data)
                
                # 更新证书信息
                certificate.blockchain_enabled = True
                certificate.blockchain_certificate_id = result['certificate_id']
                certificate.blockchain_transaction_hash = result['transaction_hash']
                certificate.blockchain_data_hash = result['data_hash']
                
                # 生成验证URL
                base_url = current_app.config.get('BASE_URL', '')
                verification_url = f"{base_url}{url_for('system.verify_certificate')}"
                verification_url += f"?id={certificate.blockchain_certificate_id}"
                certificate.blockchain_verification_url = verification_url
                
                db.session.commit()
                
                return {
                    'success': True, 
                    'message': '证书已成功上链 ',
                    'certificate': certificate
                }
            else:
                # 使用实际区块链服务的原有代码
                # 配置区块链连接
                blockchain_provider = current_app.config.get('BLOCKCHAIN_PROVIDER', 'http://localhost:8545')
                contract_address = current_app.config.get('CERTIFICATE_CONTRACT_ADDRESS')
                issuer_private_key = current_app.config.get('BLOCKCHAIN_ISSUER_PRIVATE_KEY')
                
                if not contract_address or not issuer_private_key:
                    return {'success': False, 'message': '缺少区块链配置信息'}
                
                # 初始化区块链工具
                blockchain = BlockchainCertificate(
                    web3_provider=blockchain_provider,
                    contract_address=contract_address
                )
                
                # 准备证书数据
                cert_data = certificate.to_dict()
                
                # 上传到区块链
                student_id_number = certificate.student.student_id if certificate.student else str(certificate.student_id)
                result = blockchain.issue_certificate(cert_data, student_id_number, issuer_private_key)
                
                # 更新证书信息
                certificate.blockchain_enabled = True
                certificate.blockchain_certificate_id = result['certificate_id']
                certificate.blockchain_transaction_hash = result['transaction_hash']
                certificate.blockchain_data_hash = result['data_hash']
                
                # 生成验证URL
                base_url = current_app.config.get('BASE_URL', '')
                verification_url = f"{base_url}{url_for('system.verify_certificate')}"
                verification_url += f"?id={certificate.blockchain_certificate_id}"
                certificate.blockchain_verification_url = verification_url
                
                db.session.commit()
                
                return {
                    'success': True, 
                    'message': '证书已成功上链',
                    'certificate': certificate
                }
                
        except Exception as e:
            current_app.logger.error(f"区块链上传证书失败: {str(e)}")
            return {'success': False, 'message': f'上链失败: {str(e)}'}
    
    @classmethod
    def verify_blockchain_certificate(cls, certificate_id):
        """验证区块链证书
        
        Args:
            certificate_id: 区块链证书ID
            
        Returns:
            验证结果
        """
        try:
            # 检查是否使用模拟模式
            if current_app.config.get('BLOCKCHAIN_SIMULATION_MODE', False):
                # 使用模拟服务验证
                verification_result = MockBlockchainService.verify_certificate(certificate_id)
                
                # 查询本地数据库中的证书
                certificate = UnifiedCertificate.query.filter_by(
                    blockchain_certificate_id=certificate_id
                ).first()
                
                result = {
                    'success': verification_result['is_valid'],
                    'blockchain_data': verification_result,
                    'certificate': certificate.to_dict() if certificate else None
                }
                
                if verification_result['is_valid'] and certificate:
                    result['message'] = '证书验证成功'
                elif verification_result['is_valid'] and not certificate:
                    result['message'] = '区块链验证成功，但本地数据库未找到此证书'
                else:
                    result['message'] = '证书验证失败'
                    
                return result
            else:
                # 使用实际区块链服务的原有代码
                # 配置区块链连接
                blockchain_provider = current_app.config.get('BLOCKCHAIN_PROVIDER', 'http://localhost:8545')
                contract_address = current_app.config.get('CERTIFICATE_CONTRACT_ADDRESS')
                
                if not contract_address:
                    return {'success': False, 'message': '缺少区块链配置信息'}
                
                # 初始化区块链工具
                blockchain = BlockchainCertificate(
                    web3_provider=blockchain_provider,
                    contract_address=contract_address
                )
                
                # 查询区块链
                verification_result = blockchain.verify_certificate(certificate_id)
                
                # 查询本地数据库中的证书
                certificate = UnifiedCertificate.query.filter_by(
                    blockchain_certificate_id=certificate_id
                ).first()
                
                result = {
                    'success': verification_result['is_valid'],
                    'blockchain_data': verification_result,
                    'certificate': certificate.to_dict() if certificate else None
                }
                
                if verification_result['is_valid'] and certificate:
                    result['message'] = '证书验证成功'
                elif verification_result['is_valid'] and not certificate:
                    result['message'] = '区块链验证成功，但本地数据库未找到此证书'
                else:
                    result['message'] = '证书验证失败'
                    
                return result
                
        except Exception as e:
            current_app.logger.error(f"验证区块链证书失败: {str(e)}")
            return {'success': False, 'message': f'验证失败: {str(e)}'}
    
    @staticmethod
    def generate_certificate_qrcode(verification_url):
        """生成证书验证二维码
        
        Args:
            verification_url: 验证URL
            
        Returns:
            二维码图像的base64编码
        """
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )
        qr.add_data(verification_url)
        qr.make(fit=True)
        img = qr.make_image(fill_color="black", back_color="white")
        
        # 转为base64
        buffered = BytesIO()
        img.save(buffered, format="PNG")
        img_base64 = base64.b64encode(buffered.getvalue()).decode()
        
        # 返回完整的data URI格式
        return f"data:image/png;base64,{img_base64}"
    
    @classmethod
    def generate_certificate_image(cls, certificate_id):
        """生成证书图片
        
        Args:
            certificate_id: 证书ID
            
        Returns:
            证书图片路径
        """
        certificate = UnifiedCertificate.query.get_or_404(certificate_id)
        
        # 这里应该使用模板生成证书图片
        # 简化起见，假设我们有一个模板生成器
        # template_generator = CertificateTemplateGenerator()
        # image_path = template_generator.generate(certificate)
        
        # 此处仅作示例，实际项目中可以使用PIL等库生成图片
        # 或使用预定义模板
        image_path = "static/img/certificates/template.png"
        
        # 生成验证二维码
        if certificate.blockchain_enabled and certificate.blockchain_verification_url:
            qr_code = cls.generate_certificate_qrcode(certificate.blockchain_verification_url)
            # 将二维码添加到证书图片上
            # 这里需要使用PIL等库进行图片处理
        
        return image_path 