"""
修复证书图片问题

1. 为证书添加image_url属性
2. 生成实际的证书图片文件
"""
import os
from PIL import Image, ImageDraw, ImageFont
from datetime import datetime
from app import create_app, db
from sqlalchemy import text

def create_certificate_image(cert_id, cert_name, cert_type, output_path):
    """创建证书图片"""
    # 确保目录存在
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    # 创建图片尺寸
    width, height = 1200, 900
    img = Image.new('RGB', (width, height), color=(255, 255, 255))
    draw = ImageDraw.Draw(img)
    
    # 绘制证书边框
    border_color = (70, 130, 180)  # 深蓝色
    border_width = 10
    draw.rectangle(
        [(border_width//2, border_width//2), 
         (width-border_width//2, height-border_width//2)],
        outline=border_color, width=border_width
    )
    
    # 绘制装饰图案
    for i in range(4):
        corner_size = 50
        # 左上
        draw.rectangle(
            [(border_width*2, border_width*2), 
             (border_width*2+corner_size, border_width*2+corner_size)],
            outline=border_color, width=3
        )
        # 右上
        draw.rectangle(
            [(width-border_width*2-corner_size, border_width*2), 
             (width-border_width*2, border_width*2+corner_size)],
            outline=border_color, width=3
        )
        # 左下
        draw.rectangle(
            [(border_width*2, height-border_width*2-corner_size), 
             (border_width*2+corner_size, height-border_width*2)],
            outline=border_color, width=3
        )
        # 右下
        draw.rectangle(
            [(width-border_width*2-corner_size, height-border_width*2-corner_size), 
             (width-border_width*2, height-border_width*2)],
            outline=border_color, width=3
        )
    
    # 尝试加载字体
    try:
        title_font = ImageFont.truetype("arial.ttf", 60)
        heading_font = ImageFont.truetype("arial.ttf", 48)
        normal_font = ImageFont.truetype("arial.ttf", 30)
    except:
        # 使用默认字体
        title_font = ImageFont.load_default()
        heading_font = ImageFont.load_default()
        normal_font = ImageFont.load_default()
    
    # 绘制证书标题
    draw.text((width//2, 120), "证书", fill=(0, 0, 128), font=title_font, anchor="mm")
    
    # 绘制证书名称
    draw.text((width//2, 220), cert_name, fill=(0, 0, 0), font=heading_font, anchor="mm")
    
    # 证书类型
    type_label = {
        'language': '语言能力',
        'professional': '专业能力',
        'competition': '竞赛获奖',
        'skill': '技能证书',
        'other': '其他证书'
    }
    cert_type_text = type_label.get(cert_type, '未知类型')
    
    # 绘制证书信息
    draw.text((width//2, 320), f"证书类型: {cert_type_text}", fill=(0, 0, 0), font=normal_font, anchor="mm")
    draw.text((width//2, 380), f"证书编号: CERT-{cert_id}-{datetime.now().strftime('%Y%m%d')}", fill=(0, 0, 0), font=normal_font, anchor="mm")
    draw.text((width//2, 440), f"颁发日期: {datetime.now().strftime('%Y-%m-%d')}", fill=(0, 0, 0), font=normal_font, anchor="mm")
    
    # 绘制校徽位置
    logo_position = (width//2, 550)
    logo_size = 150
    draw.ellipse(
        [(logo_position[0]-logo_size//2, logo_position[1]-logo_size//2),
         (logo_position[0]+logo_size//2, logo_position[1]+logo_size//2)],
        outline=(200, 200, 200), width=2
    )
    draw.text((logo_position[0], logo_position[1]), "校徽", fill=(150, 150, 150), font=normal_font, anchor="mm")
    
    # 绘制底部信息
    draw.text((width//2, height-150), "校园综合管理平台", fill=(0, 0, 0), font=normal_font, anchor="mm")
    draw.text((width//2, height-100), "证书真伪查询: 192.168.151.175:5000/verify_certificate", fill=(100, 100, 100), font=ImageFont.load_default(), anchor="mm")
    
    # 保存图片
    img.save(output_path)
    print(f"已创建证书图片: {output_path}")
    return True

def fix_certificate_images():
    """修复证书图片问题"""
    app = create_app()
    with app.app_context():
        # 查询所有证书
        with db.session.begin():
            # 1. 首先检查数据库表是否有image_url列
            print("检查数据库表结构...")
            try:
                db.session.execute(text("SELECT image_url FROM literacy_certificates LIMIT 1"))
                print("image_url列已存在")
            except Exception as e:
                print(f"检查image_url列时出错: {e}")
                print("添加image_url列...")
                try:
                    db.session.execute(text("ALTER TABLE literacy_certificates ADD COLUMN image_url VARCHAR(255)"))
                    db.session.commit()
                    print("已添加image_url列")
                except Exception as e:
                    print(f"添加列时出错: {e}")
                    return
        
        # 2. 获取所有证书并更新image_url
        print("更新证书图片...")
        try:
            # 使用原始SQL查询获取所有证书
            result = db.session.execute(text("SELECT id, name, certificate_type, status FROM literacy_certificates"))
            certificates = [dict(row._mapping) for row in result]
            
            if not certificates:
                print("未找到任何证书记录")
                return
            
            print(f"找到 {len(certificates)} 个证书记录")
            
            for cert in certificates:
                cert_id = cert['id']
                cert_name = cert['name']
                cert_type = cert['certificate_type']
                
                # 生成唯一的文件名
                filename = f"cert_{cert_id}_{cert_type}_{datetime.now().strftime('%Y%m%d%H%M%S')}.png"
                relative_path = f"uploads/certificates/{filename}"
                full_path = os.path.join(app.root_path, 'static', relative_path)
                
                # 创建证书图片
                if create_certificate_image(cert_id, cert_name, cert_type, full_path):
                    # 更新数据库
                    db.session.execute(
                        text("UPDATE literacy_certificates SET image_url = :image_url WHERE id = :id"),
                        {"image_url": relative_path, "id": cert_id}
                    )
                    print(f"已更新证书ID {cert_id} 的image_url: {relative_path}")
            
            db.session.commit()
            print("所有证书图片已更新")
            
        except Exception as e:
            print(f"更新证书图片时出错: {e}")
            db.session.rollback()

if __name__ == "__main__":
    fix_certificate_images() 