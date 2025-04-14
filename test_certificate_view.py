#!/usr/bin/env python
"""
证书视图功能诊断工具
验证证书显示功能是否正常工作
"""
import os
import sys
import requests
from urllib.parse import urljoin
import re

# 添加项目根目录到Python路径
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
if BASE_DIR not in sys.path:
    sys.path.append(BASE_DIR)

def log(message):
    """输出日志信息"""
    print(f"[INFO] {message}")

def login(session, base_url, username="admin", password="admin"):
    """模拟用户登录"""
    login_url = urljoin(base_url, "/auth/login")
    log(f"尝试登录: {login_url}")
    
    # 首先获取登录页面以获取CSRF令牌
    response = session.get(login_url)
    csrf_token = None
    
    # 尝试从HTML中提取CSRF令牌
    if response.status_code == 200:
        match = re.search(r'name="csrf_token" value="([^"]+)"', response.text)
        if match:
            csrf_token = match.group(1)
            log("成功获取CSRF令牌")
        else:
            log("无法在登录页面中找到CSRF令牌")
    else:
        log(f"无法访问登录页面，状态码: {response.status_code}")
        return False
    
    # 提交登录表单
    login_data = {
        "username": username,
        "password": password
    }
    
    if csrf_token:
        login_data["csrf_token"] = csrf_token
    
    response = session.post(login_url, data=login_data, allow_redirects=True)
    
    # 检查登录是否成功
    if response.status_code == 200 and "登录成功" in response.text:
        log("登录成功")
        return True
    elif response.status_code == 200 and "登录" in response.text and "密码" in response.text:
        log("登录失败，可能是用户名或密码错误")
        return False
    else:
        log(f"登录过程中出现问题，状态码: {response.status_code}")
        return "管理" in response.text or "Dashboard" in response.text  # 粗略判断是否已登录

def test_certificate_view():
    """测试证书视图功能"""
    # 基础URL
    base_url = "http://127.0.0.1:5000"
    
    # 创建会话以保持登录状态
    session = requests.Session()
    
    # 登录
    if not login(session, base_url):
        log("登录失败，测试终止")
        return
    
    # 测试证书列表页面
    certificates_url = urljoin(base_url, "/literacy/certificates")
    log(f"测试证书列表页面: {certificates_url}")
    
    try:
        response = session.get(certificates_url)
        if response.status_code == 200:
            log("证书列表页面访问成功")
            
            # 检查页面是否包含证书列表
            if "证书列表" in response.text or "证书" in response.text:
                log("页面包含证书列表内容")
            else:
                log("警告: 页面可能不包含证书列表内容")
        else:
            log(f"证书列表页面访问失败，状态码: {response.status_code}")
            
    except Exception as e:
        log(f"访问证书列表页面时出错: {str(e)}")
    
    # 测试证书详情页面
    certificate_ids = [1, 2]  # 已知的证书ID
    
    for cert_id in certificate_ids:
        certificate_url = urljoin(base_url, f"/literacy/certificates/{cert_id}")
        log(f"测试证书详情页面 ID={cert_id}: {certificate_url}")
        
        try:
            response = session.get(certificate_url)
            if response.status_code == 200:
                log(f"证书ID={cert_id}详情页面访问成功")
                
                # 检查HTML内容中是否包含图片
                has_image = 'img src' in response.text
                if has_image:
                    log(f"证书ID={cert_id}页面包含图片元素")
                    
                    # 尝试提取图片URL
                    img_matches = re.findall(r'<img[^>]+src=[\'"](.*?)[\'"]', response.text)
                    for img_url in img_matches:
                        if 'certificates' in img_url:
                            log(f"发现证书图片URL: {img_url}")
                            
                            # 测试图片是否可访问
                            full_img_url = urljoin(base_url, img_url)
                            try:
                                img_response = session.get(full_img_url)
                                if img_response.status_code == 200:
                                    log(f"证书图片可以正常访问: {full_img_url}")
                                else:
                                    log(f"警告: 证书图片无法访问，状态码: {img_response.status_code}")
                            except Exception as e:
                                log(f"访问证书图片时出错: {str(e)}")
                else:
                    log(f"警告: 证书ID={cert_id}页面不包含图片元素")
                    
                # 检查页面内容中是否包含关键信息
                keywords = ['证书', '类型', '颁发日期', '颁发机构']
                for keyword in keywords:
                    if keyword in response.text:
                        log(f"证书页面包含关键信息: {keyword}")
                    else:
                        log(f"警告: 证书页面不包含关键信息: {keyword}")
                        
            else:
                log(f"证书ID={cert_id}详情页面访问失败，状态码: {response.status_code}")
                
        except Exception as e:
            log(f"访问证书ID={cert_id}详情页面时出错: {str(e)}")
    
    log("证书视图功能诊断完成")

if __name__ == "__main__":
    test_certificate_view() 