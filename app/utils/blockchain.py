import json
import time
import hashlib
from web3 import Web3
from eth_account import Account
from eth_account.messages import encode_defunct
from flask import current_app

# 智能合约ABI定义
CERTIFICATE_ABI = json.loads('''
[
    {
        "anonymous": false,
        "inputs": [
            {
                "indexed": true,
                "internalType": "bytes32",
                "name": "certificateId",
                "type": "bytes32"
            },
            {
                "indexed": true,
                "internalType": "address",
                "name": "issuer",
                "type": "address"
            },
            {
                "indexed": false,
                "internalType": "string",
                "name": "studentId",
                "type": "string"
            },
            {
                "indexed": false,
                "internalType": "uint256",
                "name": "timestamp",
                "type": "uint256"
            }
        ],
        "name": "CertificateIssued",
        "type": "event"
    },
    {
        "inputs": [
            {
                "internalType": "bytes32",
                "name": "certificateId",
                "type": "bytes32"
            },
            {
                "internalType": "string",
                "name": "studentId",
                "type": "string"
            },
            {
                "internalType": "string",
                "name": "certificateDataHash",
                "type": "string"
            }
        ],
        "name": "issueCertificate",
        "outputs": [],
        "stateMutability": "nonpayable",
        "type": "function"
    },
    {
        "inputs": [
            {
                "internalType": "bytes32",
                "name": "certificateId",
                "type": "bytes32"
            }
        ],
        "name": "verifyCertificate",
        "outputs": [
            {
                "internalType": "bool",
                "name": "isValid",
                "type": "bool"
            },
            {
                "internalType": "address",
                "name": "issuer",
                "type": "address"
            },
            {
                "internalType": "string",
                "name": "studentId",
                "type": "string"
            },
            {
                "internalType": "string",
                "name": "certificateDataHash",
                "type": "string"
            },
            {
                "internalType": "uint256",
                "name": "timestamp",
                "type": "uint256"
            }
        ],
        "stateMutability": "view",
        "type": "function"
    }
]
''')

# 智能合约字节码（部署时使用）
CONTRACT_BYTECODE = "0x608060405234801561001057600080fd5b50610771806100206000396000f3fe608060405234801561001057600080fd5b50600436106100365760003560e01c80634f2be91f1461003b578063cf1d7b01146100c3575b600080fd5b6100c1600480360360608110156100515760006100a96100708660046104a8565b6100e18760046104a8565b60408051808201909152600c81526b4365727469666963617465732d60a01b60208201529091506100a184846101d0565b9695505050505050565b005b6100e1600480360360208110156100d957600080fd5b50356001600160e01b031916610393565b60098054600160a01b60ff021916905560006001600160e01b0319166001600160e01b031990911617600155600080805260046020527f38ded5600d570acae093f252664926561abb14401fe66537e3d2e2c57776bc7805460ff191660011790554260035560405161014b90610645565b60408051918290038220600080546001600160e01b0319166001600160e01b0390931692909217825582516001600160a01b0381168152915190927f9550e8dfbddd9b12334d4bbba78d6c8f74f8a3f1c04a0a3301e9e9ea183ad6989181900360200190a25060009392505050565b60008082518351146101f257600080600080fd5b600080805b84518110156102ee576000858281518110151561021057fe5b9060200101517f010000000000000000000000000000000000000000000000000000000000000090047f01000000000000000000000000000000000000000000000000000000000000000290506000858381518110151561026b57fe5b90602001015160f81c905060108104905080603060ff8216101580156102945750603960ff82161015155b801561036a575060618160ff1610801561031a575060668160ff16101580156102c05750607a60ff82161015155b801561036a575060418160ff161080156102e65750605a60ff82161015155b155b6102f7576103fa565b5060010161021f565b508451600154148015610301575082516001600160e01b031916600154145b61030a576103fa565b600084516001600160e01b03191660408051600160e01b638594f12d021815233600482015290519192507f8c8f78d9800000000000000000000000000000000000000000000000000000000836024820152925073ffffffffffffffffffffffffffffffffffffffff16916385946fbd9160448083019260209291908290030181600087803b15801561039857600080fd5b505af11580156103ac573d6000803e3d6000fd5b505050506040513d60208110156103c257600080fd5b505190506103fb565b6103e8816001600160e01b03191660023560e01c90565b1480156103f557508051825114155b90505b93925050505b60009392505050565b60008160601b90506001600160601b031982161561050357806000036150000361050057607f6001600160601b03198316016001600160601b0319821681179150610503565b90505b919050565b5080546001600160e01b0319166001600160e01b0319909116178155600181556002805460ff191690556003829055600060048290556005829055600682905560078290556008909155565b604080518082019091526000808252602082015290565b6040518060a0016040528060008152602001600073ffffffffffffffffffffffffffffffffffffffff168152602001606081526020016060815260200160008152509056fea265627a7a7231582034f7f8a42b9ca5dda5550686b58b41f877f7f10b6e3b1e47add81fbacb3ac2d964736f6c63430005100032"

class BlockchainCertificate:
    """区块链证书工具类"""
    
    def __init__(self, web3_provider=None, contract_address=None):
        """初始化区块链连接
        
        Args:
            web3_provider: Web3提供者URL
            contract_address: 智能合约地址
        """
        if web3_provider is None:
            # 默认使用本地测试网络
            web3_provider = "http://localhost:8545"
        
        self.web3 = Web3(Web3.HTTPProvider(web3_provider))
        self.contract_address = contract_address
        
        if contract_address:
            self.certificate_contract = self.web3.eth.contract(
                address=self.web3.toChecksumAddress(contract_address),
                abi=CERTIFICATE_ABI
            )
        
    def deploy_contract(self, private_key):
        """部署证书智能合约
        
        Args:
            private_key: 部署者的私钥
            
        Returns:
            部署的合约地址
        """
        account = Account.from_key(private_key)
        nonce = self.web3.eth.getTransactionCount(account.address)
        
        # 创建合约对象
        certificate_contract = self.web3.eth.contract(abi=CERTIFICATE_ABI, bytecode=CONTRACT_BYTECODE)
        
        # 构建交易
        transaction = certificate_contract.constructor().buildTransaction({
            'chainId': self.web3.eth.chainId,
            'gas': 3000000,
            'gasPrice': self.web3.toWei('50', 'gwei'),
            'nonce': nonce,
        })
        
        # 签名交易
        signed_tx = self.web3.eth.account.sign_transaction(transaction, private_key)
        
        # 发送交易
        tx_hash = self.web3.eth.sendRawTransaction(signed_tx.rawTransaction)
        
        # 等待交易被确认
        tx_receipt = self.web3.eth.waitForTransactionReceipt(tx_hash)
        
        self.contract_address = tx_receipt.contractAddress
        self.certificate_contract = self.web3.eth.contract(
            address=self.contract_address,
            abi=CERTIFICATE_ABI
        )
        
        return self.contract_address
    
    def generate_certificate_id(self, certificate_data):
        """根据证书数据生成唯一证书ID
        
        Args:
            certificate_data: 证书数据字典
            
        Returns:
            证书ID (bytes32 哈希值)
        """
        # 将证书数据序列化为JSON字符串
        data_str = json.dumps(certificate_data, sort_keys=True)
        
        # 添加时间戳确保唯一性
        data_str += str(int(time.time()))
        
        # 生成SHA-256哈希
        hash_object = hashlib.sha256(data_str.encode())
        certificate_id = '0x' + hash_object.hexdigest()
        
        return certificate_id
    
    def issue_certificate(self, certificate_data, student_id, private_key):
        """在区块链上颁发证书
        
        Args:
            certificate_data: 证书数据字典
            student_id: 学生ID
            private_key: 颁发者私钥
            
        Returns:
            交易哈希和证书ID
        """
        if not self.contract_address:
            raise ValueError("智能合约未部署，请先部署合约")
            
        # 生成证书ID
        certificate_id = self.generate_certificate_id(certificate_data)
        
        # 计算证书数据哈希
        data_hash = hashlib.sha256(json.dumps(certificate_data, sort_keys=True).encode()).hexdigest()
        
        # 准备账户
        account = Account.from_key(private_key)
        nonce = self.web3.eth.getTransactionCount(account.address)
        
        # 构建交易
        transaction = self.certificate_contract.functions.issueCertificate(
            self.web3.toBytes(hexstr=certificate_id),
            student_id,
            data_hash
        ).buildTransaction({
            'chainId': self.web3.eth.chainId,
            'gas': 3000000,
            'gasPrice': self.web3.toWei('50', 'gwei'),
            'nonce': nonce,
        })
        
        # 签名交易
        signed_tx = self.web3.eth.account.sign_transaction(transaction, private_key)
        
        # 发送交易
        tx_hash = self.web3.eth.sendRawTransaction(signed_tx.rawTransaction)
        
        # 等待交易被确认
        tx_receipt = self.web3.eth.waitForTransactionReceipt(tx_hash)
        
        return {
            'transaction_hash': tx_hash.hex(),
            'certificate_id': certificate_id,
            'data_hash': data_hash
        }
    
    def verify_certificate(self, certificate_id):
        """验证区块链上的证书
        
        Args:
            certificate_id: 证书ID
            
        Returns:
            验证结果字典
        """
        if not self.contract_address:
            raise ValueError("智能合约未部署，请先部署合约")
            
        # 调用智能合约验证证书
        result = self.certificate_contract.functions.verifyCertificate(
            self.web3.toBytes(hexstr=certificate_id)
        ).call()
        
        return {
            'is_valid': result[0],
            'issuer': result[1],
            'student_id': result[2],
            'data_hash': result[3],
            'timestamp': result[4]
        }
    
    @staticmethod
    def sign_message(message, private_key):
        """使用私钥签名消息
        
        Args:
            message: 待签名消息
            private_key: 私钥
            
        Returns:
            签名
        """
        account = Account.from_key(private_key)
        message_hash = encode_defunct(text=message)
        signed_message = account.sign_message(message_hash)
        
        return {
            'message': message,
            'messageHash': signed_message.messageHash.hex(),
            'signature': signed_message.signature.hex(),
            'signer': account.address
        }
    
    @staticmethod
    def verify_signature(message, signature, address):
        """验证签名
        
        Args:
            message: 原始消息
            signature: 签名
            address: 签名者地址
            
        Returns:
            验证结果
        """
        message_hash = encode_defunct(text=message)
        recovered_address = Account.recover_message(message_hash, signature=signature)
        
        return recovered_address.lower() == address.lower() 