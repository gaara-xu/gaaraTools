import os

def get_all_files(folder):
    return [os.path.join(folder, f) for f in os.listdir(folder) if os.path.isfile(os.path.join(folder, f))]

def get_file_size(file_path):
    try:
        size = os.path.getsize(file_path)
        return size
    except Exception as e:
        return f"[错误] {e}"
