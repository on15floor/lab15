import os

import bcrypt
import markdown

from config import STATIC_PATH


def get_markdown(fname):
    file_path = os.path.join(STATIC_PATH, f'hints/{fname}')
    with open(file_path) as file:
        return markdown.markdown(file.read())


def check_pw(password, hash_password):
    return bcrypt.checkpw(bytes(password, 'utf-8'), bytes(hash_password, 'utf-8'))


def hash_pw(password):
    password_hash = bcrypt.hashpw(bytes(password, 'utf-8'), bcrypt.gensalt(10))
    return password_hash.decode('utf-8')


def get_ip(request):
    return request.environ.get('HTTP_X_REAL_IP', request.remote_addr)
