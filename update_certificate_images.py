"""
更新证书图片
此脚本用于创建示例证书图片并更新数据库中的证书记录
"""
import os
import shutil
from PIL import Image, ImageDraw, ImageFont
from datetime import datetime
from app import create_app, db
from app.models.literacy import LiteracyCertificate

def create_sample_certificate_image(output_path, name, cert_type, issuer, issue_date):
    """
    创建示例证书图片
    
    Args:
        output_path: 输出文件路径
        name: 证书名称
        cert_type: 证书类型
        issuer: 颁发机构
        issue_date: 颁发日期
    """
    # 确保目录存在
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    # 创建空白图片
    width, height = 1200, 900
    background_color = (255, 255, 255)
    img = Image.new('RGB', (width, height), background_color)
    draw = ImageDraw.Draw(img)
    
    # 边框
    border_color = (70, 130, 180)
    border_width = 20
    draw.rectangle([(border_width, border_width), (width - border_width, height - border_width)], 
                  outline=border_color, width=border_width)
    
    # 标题
    try:
        # 尝试加载字体，如果失败则使用默认字体
        title_font = ImageFont.truetype("arial.ttf", 60)
        normal_font = ImageFont.truetype("arial.ttf", 30)
    except:
        # 使用默认字体
        title_font = ImageFont.load_default()
        normal_font = ImageFont.load_default()
    
    # 绘制证书内容
    draw.text((width//2, 150), "证书", fill=(0, 0, 0), font=title_font, anchor="mm")
    draw.text((width//2, 250), name, fill=(0, 0, 0), font=title_font, anchor="mm")
    
    # 证书类型
    type_label = {
        'language': '语言能力',
        'professional': '专业能力',
        'competition': '竞赛获奖',
        'skill': '技能证书',
        'other': '其他证书'
    }
    
    cert_type_text = type_label.get(cert_type, '未知类型')
    draw.text((width//2, 350), f"证书类型: {cert_type_text}", fill=(0, 0, 0), font=normal_font, anchor="mm")
    
    # 颁发机构
    draw.text((width//2, 450), f"颁发机构: {issuer}", fill=(0, 0, 0), font=normal_font, anchor="mm")
    
    # 颁发日期
    draw.text((width//2, 550), f"颁发日期: {issue_date}", fill=(0, 0, 0), font=normal_font, anchor="mm")
    
    # 底部文字
    draw.text((width//2, height-150), "校园综合管理平台颁发", fill=(0, 0, 0), font=normal_font, anchor="mm")
    
    # 保存图片
    img.save(output_path)
    print(f"已创建证书图片: {output_path}")

def update_certificate_images():
    """更新证书图片并更新数据库记录"""
    app = create_app()
    with app.app_context():
        certificates = LiteracyCertificate.query.all()
        print(f"找到 {len(certificates)} 个证书记录")
        
        for cert in certificates:
            # 为每个证书生成唯一的图片文件名
            cert_id = cert.id
            cert_type = cert.certificate_type
            timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
            filename = f"cert_{cert_id}_{cert_type}_{timestamp}.jpg"
            
            # 构建路径
            rel_path = f"uploads/certificates/{filename}"
            abs_path = os.path.join(app.root_path, 'static', rel_path)
            
            # 创建证书图片
            create_sample_certificate_image(
                abs_path,
                cert.name,
                cert.certificate_type,
                cert.issuer,
                cert.issue_date.strftime('%Y-%m-%d')
            )
            
            # 更新数据库记录
            cert.image_url = rel_path
            print(f"更新证书 ID: {cert.id}, image_url: {rel_path}")
        
        # 提交更改
        db.session.commit()
        print("所有证书记录已更新")

if __name__ == "__main__":
    update_certificate_images() 