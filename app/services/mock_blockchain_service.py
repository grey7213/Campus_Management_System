from datetime import datetime
import hashlib
import uuid

class MockBlockchainService:
    """模拟区块链服务，用于演示和测试"""
    
    @staticmethod
    def generate_certificate_id():
        """生成模拟的区块链证书ID"""
        # 生成一个16字节的随机ID
        random_id = uuid.uuid4().hex
        # 添加0x前缀，使其看起来像以太坊地址
        return f"0x{random_id}"
    
    @staticmethod
    def generate_transaction_hash():
        """生成模拟的交易哈希"""
        # 生成一个32字节的随机哈希
        random_hash = uuid.uuid4().hex + uuid.uuid4().hex
        # 添加0x前缀
        return f"0x{random_hash}"
    
    @staticmethod
    def generate_data_hash(data):
        """根据数据生成哈希"""
        # 将数据转换为字符串并生成SHA-256哈希
        data_str = str(data)
        return hashlib.sha256(data_str.encode()).hexdigest()
    
    @staticmethod
    def issue_certificate(certificate_data):
        """模拟上链操作"""
        # 生成必要的区块链数据
        certificate_id = MockBlockchainService.generate_certificate_id()
        transaction_hash = MockBlockchainService.generate_transaction_hash()
        data_hash = MockBlockchainService.generate_data_hash(certificate_data)
        
        # 构造返回结果
        return {
            'certificate_id': certificate_id,
            'transaction_hash': transaction_hash,
            'data_hash': data_hash,
            'timestamp': int(datetime.now().timestamp()),
            'success': True
        }
    
    @staticmethod
    def verify_certificate(certificate_id):
        """模拟验证操作"""
        # 在实际应用中，这里会检查区块链上的证书
        # 在模拟模式下，我们假设所有格式正确的ID都是有效的
        
        if certificate_id and certificate_id.startswith('0x') and len(certificate_id) >= 42:
            return {
                'is_valid': True,
                'issuer': '0x71C7656EC7ab88b098defB751B7401B5f6d8976F',
                'student_id': 'SimulatedStudent',
                'data_hash': 'simulatedDataHash',
                'timestamp': int(datetime.now().timestamp())
            }
        else:
            return {
                'is_valid': False,
                'issuer': None,
                'student_id': None,
                'data_hash': None,
                'timestamp': None
            }
