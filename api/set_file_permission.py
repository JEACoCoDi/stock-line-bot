import os

def handler(req, res):
    path = 'img.png'
    permissions = 0o644

    os.chmod(path, permissions)

    res.status(200).json({
        'message': 'File permissions updated successfully.'
    })