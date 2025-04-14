"""
定时任务运行脚本

此脚本用于运行系统中的各种定时任务，可以通过计划任务（如cron）定期执行
"""
import os
import argparse
import logging
from datetime import datetime

from app.tasks.certificate_tasks import auto_approve_certificates

# 设置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler(f"logs/tasks_{datetime.now().strftime('%Y%m%d')}.log")
    ]
)
logger = logging.getLogger(__name__)

# 确保日志目录存在
os.makedirs("logs", exist_ok=True)

def main():
    parser = argparse.ArgumentParser(description='运行系统定时任务')
    parser.add_argument('--task', type=str, choices=['certificates'], 
                        help='指定要运行的任务: certificates=证书自动审批')
    
    args = parser.parse_args()
    
    if args.task == 'certificates':
        logger.info("开始运行证书自动审批任务")
        auto_approve_certificates()
        logger.info("证书自动审批任务完成")
    else:
        logger.info("运行所有定时任务")
        # 运行所有任务
        auto_approve_certificates()
        # 在此处添加其他任务
        logger.info("所有任务执行完成")

if __name__ == "__main__":
    main() 