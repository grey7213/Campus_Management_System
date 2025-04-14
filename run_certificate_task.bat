@echo off
cd /d "%~dp0"
echo 开始执行证书自动审批任务 %date% %time%
python run_tasks.py --task certificates
echo 证书自动审批任务完成 %date% %time%
pause 