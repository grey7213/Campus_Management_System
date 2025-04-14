"""
证书系统初始化工具
确保证书模型一致性，并生成缺失的证书图片
"""
import os
import sys
from datetime import datetime
from PIL import Image, ImageDraw, ImageFont
import importlib

# 添加项目根目录到Python路径
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if BASE_DIR not in sys.path:
    sys.path.append(BASE_DIR)

from app import create_app, db
from app.models.unity_cert import UnifiedCertificate

# 创建应用实例
app = create_app()

def log(message):
    """记录日志信息"""
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    print(f"[{timestamp}] {message}")

def ensure_directory_exists(directory):
    """确保目录存在"""
    if not os.path.exists(directory):
        os.makedirs(directory)
        log(f"创建目录: {directory}")

def create_certificate_image(cert_id, cert_name, cert_type, filename):
    """为证书创建图片"""
    # 创建目录
    cert_dir = os.path.join(app.root_path, 'static', 'uploads', 'certificates')
    ensure_directory_exists(cert_dir)
    
    # 图片文件路径
    image_path = os.path.join(cert_dir, filename)
    if os.path.exists(image_path):
        log(f"证书图片已存在: {image_path}")
        return f"uploads/certificates/{filename}"
    
    # 创建证书图片
    width, height = 800, 600
    image = Image.new('RGB', (width, height), color=(255, 255, 255))
    draw = ImageDraw.Draw(image)
    
    # 尝试加载字体，如果失败则使用默认字体
    try:
        font_path = os.path.join(app.root_path, 'static', 'fonts', 'arial.ttf')
        if not os.path.exists(font_path):
            font_path = os.path.join(app.root_path, 'static', 'fonts')
            ensure_directory_exists(font_path)
            # 使用系统字体或创建一个简单的字体文件
            font = None
        else:
            font = ImageFont.truetype(font_path, 20)
    except Exception as e:
        log(f"无法加载字体: {str(e)}")
        font = None
    
    # 绘制证书内容
    draw.rectangle([20, 20, width-20, height-20], outline=(0, 0, 0))
    
    # 标题
    title = f"证书 - {cert_name}"
    title_width = draw.textlength(title, font=font) if font else 300
    draw.text(((width - title_width) / 2, 50), title, fill=(0, 0, 0), font=font)
    
    # 证书类型
    type_text = f"类型: {cert_type}"
    draw.text((50, 120), type_text, fill=(0, 0, 0), font=font)
    
    # 证书ID
    id_text = f"证书ID: {cert_id}"
    draw.text((50, 170), id_text, fill=(0, 0, 0), font=font)
    
    # 颁发日期
    date_text = f"颁发日期: {datetime.now().strftime('%Y-%m-%d')}"
    draw.text((50, 220), date_text, fill=(0, 0, 0), font=font)
    
    # 区块链验证信息
    blockchain_text = "此证书已在区块链上验证"
    draw.text((50, 270), blockchain_text, fill=(0, 128, 0), font=font)
    
    # 保存图片
    image.save(image_path)
    log(f"已创建证书图片: {filename}")
    
    return f"uploads/certificates/{filename}"

def init_certificates():
    """初始化证书数据"""
    with app.app_context():
        try:
            # 确保我们使用的是统一的证书模型
            importlib.reload(sys.modules['app.models.unity_cert'])
            log("已重新加载证书模型")
            
            # 获取所有证书
            certificates = UnifiedCertificate.query.all()
            log(f"找到 {len(certificates)} 个证书记录")
            
            for cert in certificates:
                # 检查并设置区块链启用状态
                if cert.blockchain_enabled is None:
                    cert.blockchain_enabled = True
                    log(f"更新证书ID {cert.id} 的区块链启用状态为 True")
                
                # 检查并设置图片URL
                if not cert.image_url or not os.path.exists(
                    os.path.join(app.root_path, 'static', cert.image_url)
                ):
                    # 生成唯一的文件名
                    timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
                    filename = f"cert_{cert.id}_{cert.certificate_type or 'general'}_{timestamp}.png"
                    
                    # 创建证书图片
                    image_url = create_certificate_image(
                        cert.id, cert.name, cert.certificate_type, filename
                    )
                    
                    # 更新证书记录
                    cert.image_url = image_url
                    log(f"更新证书ID {cert.id} 的图片URL: {image_url}")
            
            # 提交更改
            db.session.commit()
            log("已成功提交所有更改到数据库")
            
        except Exception as e:
            db.session.rollback()
            log(f"初始化证书数据时发生错误: {str(e)}")
            raise

if __name__ == "__main__":
    init_certificates() 