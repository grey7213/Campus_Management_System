import os
import uuid
from datetime import datetime
from werkzeug.utils import secure_filename
from flask import current_app

def save_uploaded_file(file_obj, subfolder, prefix=''):
    """
    保存上传的文件到指定子文件夹
    
    Args:
        file_obj: 文件对象 (来自request.files)
        subfolder: 保存的子文件夹 (相对于static/uploads)
        prefix: 文件名前缀
        
    Returns:
        保存的文件路径 (相对于static目录)
    """
    if not file_obj:
        return None
        
    # 确保文件名安全
    original_filename = secure_filename(file_obj.filename)
    # 生成唯一的文件名
    filename = f"{prefix}_{uuid.uuid4().hex}{os.path.splitext(original_filename)[1]}"
    
    # 确保目标子文件夹存在
    upload_folder = os.path.join(current_app.static_folder, 'uploads', subfolder)
    os.makedirs(upload_folder, exist_ok=True)
    
    # 保存文件
    file_path = os.path.join(upload_folder, filename)
    file_obj.save(file_path)
    
    # 返回相对路径 (相对于static目录)
    return f"uploads/{subfolder}/{filename}"
