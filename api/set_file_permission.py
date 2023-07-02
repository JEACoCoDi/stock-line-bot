import os

def set_file_permissions():
    path = 'img.png'
    permissions = 0o666

    try:
        os.chmod(path, permissions)
        print(f"文件权限已修改为可读可写可修改：{path}")
    except OSError as e:
        print(f"修改文件权限失败：{e}")