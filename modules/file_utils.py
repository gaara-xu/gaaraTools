import os
import hashlib

def get_all_files(folder):
    return [os.path.join(folder, f) for f in os.listdir(folder) if os.path.isfile(os.path.join(folder, f))]

def get_file_size(file_path):
    try:
        size = os.path.getsize(file_path)
        return size
    except Exception as e:
        return f"[错误] {e}"

def get_file_md5(file_path: str) -> str:
    """
    计算文件的 MD5 值。
    :param file_path: 文件路径
    :return: 文件的 MD5 值
    """
    hash_md5 = hashlib.md5()
    with open(file_path, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_md5.update(chunk)
    return hash_md5.hexdigest()
