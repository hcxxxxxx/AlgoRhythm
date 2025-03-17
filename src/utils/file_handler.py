import os
import uuid
from werkzeug.utils import secure_filename
from config import UPLOAD_FOLDER

def get_upload_path(session_id, filename):
    """获取上传文件的路径
    
    Args:
        session_id: 会话ID
        filename: 文件名
        
    Returns:
        str: 文件路径
    """
    session_folder = os.path.join(UPLOAD_FOLDER, session_id)
    return os.path.join(session_folder, filename)

def save_uploaded_file(file, session_id):
    """保存上传的文件
    
    Args:
        file: 文件对象
        session_id: 会话ID
        
    Returns:
        str: 保存后的文件名
    """
    # 创建会话文件夹
    session_folder = os.path.join(UPLOAD_FOLDER, session_id)
    os.makedirs(session_folder, exist_ok=True)
    
    # 安全处理文件名
    filename = secure_filename(file.filename)
    
    # 如果文件名不合法，使用随机生成的UUID作为文件名
    if not filename:
        ext = file.filename.rsplit('.', 1)[1].lower() if '.' in file.filename else 'audio'
        filename = f"{uuid.uuid4().hex}.{ext}"
    
    # 保存文件
    file_path = os.path.join(session_folder, filename)
    file.save(file_path)
    
    return filename

def clean_old_files(max_age=24*60*60):
    """清理过期的文件
    
    Args:
        max_age: 最大保留时间(秒)，默认24小时
    """
    import time
    
    current_time = time.time()
    
    for session_id in os.listdir(UPLOAD_FOLDER):
        session_folder = os.path.join(UPLOAD_FOLDER, session_id)
        
        # 跳过非文件夹
        if not os.path.isdir(session_folder):
            continue
            
        # 检查文件夹修改时间
        folder_mtime = os.path.getmtime(session_folder)
        if current_time - folder_mtime > max_age:
            # 删除过期文件夹
            for root, dirs, files in os.walk(session_folder, topdown=False):
                for file in files:
                    os.remove(os.path.join(root, file))
                for dir in dirs:
                    os.rmdir(os.path.join(root, dir))
            os.rmdir(session_folder)