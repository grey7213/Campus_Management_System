#!/usr/bin/env python
"""
证书系统简易修复工具
直接使用SQL更新证书图片URL和生成缺失的图片
"""
import os
import sys
import sqlite3
from datetime import datetime
from PIL import Image, ImageDraw, ImageFont

def log(message):
    """记录日志信息"""
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    print(f"[{timestamp}] {message}")

def ensure_directory_exists(directory):
    """确保目录存在"""
    if not os.path.exists(directory):
        os.makedirs(directory)
        log(f"创建目录: {directory}")

def create_certificate_image(cert_id, cert_name, cert_type, filename, cert_dir):
    """为证书创建图片"""
    # 图片文件路径
    image_path = os.path.join(cert_dir, filename)
    if os.path.exists(image_path):
        log(f"证书图片已存在: {image_path}")
        return f"uploads/certificates/{filename}"
    
    # 创建证书图片
    width, height = 800, 600
    image = Image.new('RGB', (width, height), color=(255, 255, 255))
    draw = ImageDraw.Draw(image)
    
    # 尝试使用默认字体
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

def fix_certificates():
    """修复证书数据"""
    conn = None
    try:
        # 连接到数据库
        db_path = 'data-dev.sqlite'
        if not os.path.exists(db_path):
            log(f"数据库文件不存在: {db_path}")
            # 尝试在项目根目录中查找数据库文件
            for file in os.listdir('.'):
                if file.endswith('.sqlite') or file.endswith('.db'):
                    db_path = file
                    log(f"找到数据库文件: {db_path}")
                    break
        
        log(f"使用数据库文件: {db_path}")
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        log("已连接到数据库")
        
        # 检查表结构
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = cursor.fetchall()
        log(f"数据库中的表: {', '.join([t[0] for t in tables])}")
        
        # 检查literacy_certificates表是否存在
        if ('literacy_certificates',) not in tables:
            log("错误: 找不到literacy_certificates表")
            return
        
        # 获取表结构
        cursor.execute("PRAGMA table_info(literacy_certificates)")
        columns = cursor.fetchall()
        column_names = [col[1] for col in columns]
        log(f"literacy_certificates表列: {', '.join(column_names)}")
        
        # 检查必要的列
        if 'image_url' not in column_names:
            cursor.execute("ALTER TABLE literacy_certificates ADD COLUMN image_url TEXT")
            log("已添加image_url列")
        
        if 'blockchain_enabled' not in column_names:
            cursor.execute("ALTER TABLE literacy_certificates ADD COLUMN blockchain_enabled BOOLEAN")
            log("已添加blockchain_enabled列")
        
        # 获取所有证书
        cursor.execute("SELECT id, name, certificate_type, image_url, blockchain_enabled FROM literacy_certificates")
        certificates = cursor.fetchall()
        log(f"找到 {len(certificates)} 个证书记录")
        
        # 创建证书图片目录
        base_dir = os.path.dirname(os.path.abspath(__file__))
        cert_dir = os.path.join(base_dir, 'app', 'static', 'uploads', 'certificates')
        ensure_directory_exists(cert_dir)
        
        # 遍历证书并修复
        for cert in certificates:
            cert_id, name, cert_type, image_url, blockchain_enabled = cert
            
            # 检查并设置区块链启用状态
            if blockchain_enabled is None:
                cursor.execute(
                    "UPDATE literacy_certificates SET blockchain_enabled = ? WHERE id = ?",
                    (1, cert_id)  # SQLite中的布尔值用1表示True
                )
                log(f"更新证书ID {cert_id} 的区块链启用状态为 True")
            
            # 检查并设置图片URL
            image_file_path = None
            if image_url:
                image_file_path = os.path.join(base_dir, 'app', 'static', image_url)
            
            if not image_url or not os.path.exists(image_file_path or ''):
                # 生成唯一的文件名
                timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
                filename = f"cert_{cert_id}_{cert_type or 'general'}_{timestamp}.png"
                
                # 创建证书图片
                new_image_url = create_certificate_image(
                    cert_id, name, cert_type, filename, cert_dir
                )
                
                # 更新证书记录
                cursor.execute(
                    "UPDATE literacy_certificates SET image_url = ? WHERE id = ?",
                    (new_image_url, cert_id)
                )
                log(f"更新证书ID {cert_id} 的图片URL: {new_image_url}")
        
        # 提交更改
        conn.commit()
        log("已成功提交所有更改到数据库")
        
    except Exception as e:
        if conn:
            conn.rollback()
        log(f"修复证书数据时发生错误: {str(e)}")
        raise
    
    finally:
        if conn:
            conn.close()

if __name__ == "__main__":
    try:
        fix_certificates()
        log("\n证书系统修复完成！")
        log("请重启您的Flask应用程序以应用更改。")
    except Exception as e:
        log(f"证书修复失败: {str(e)}")
        sys.exit(1) 