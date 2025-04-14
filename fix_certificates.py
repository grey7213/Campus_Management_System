#!/usr/bin/env python
"""
证书系统修复工具
修复证书模型不一致性并重新初始化证书数据
"""
import os
import sys
import subprocess
import time

def log(message):
    """输出日志信息"""
    print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] {message}")

def main():
    """主程序入口"""
    log("开始修复证书系统...")
    
    # 确保所需的Python包已安装
    try:
        log("检查必要的依赖项...")
        subprocess.run([sys.executable, "-m", "pip", "install", "pillow"], 
                      stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)
        log("依赖项检查完成")
    except subprocess.CalledProcessError as e:
        log(f"安装依赖项时出错: {e}")
        log("请手动安装Pillow库: pip install pillow")
    
    # 1. 运行模型一致性修复脚本
    log("正在修复模型不一致性...")
    try:
        from app.utils.init_certificates import init_certificates
        init_certificates()
        log("模型不一致性修复完成")
    except Exception as e:
        log(f"修复模型不一致性时出错: {e}")
        return False
    
    # 2. 重启应用程序（指导用户）
    log("\n证书系统修复完成！")
    log("请重启您的Flask应用程序以应用更改。")
    log("如果您使用的是开发服务器，请按Ctrl+C停止当前运行的服务器，然后重新启动。")
    log("如果您使用的是生产环境，请按照您的部署方式重启应用程序。")
    
    return True

if __name__ == "__main__":
    # 添加项目根目录到Python路径
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    if BASE_DIR not in sys.path:
        sys.path.append(BASE_DIR)
    
    success = main()
    if success:
        sys.exit(0)
    else:
        sys.exit(1) 