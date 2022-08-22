from flask_login import LoginManager, UserMixin, login_user

from config import Config
from utils.utils import check_pw

USERS = {Config.FLASK_ADMIN: {'password': Config.FLASK_ADMIN_PWD}}


class User(UserMixin):
    pass


class Init:
    def __init__(self, app):
        login_manager = LoginManager(app)
        login_manager.init_app(app)

        @login_manager.user_loader
        def user_loader(username):
            if username not in USERS:
                return

            user = User()
            user.id = username
            return user


def auth_user(user_data: dict) -> bool:
    username = user_data.get('username', None)
    password = user_data.get('password', None)
    if username in USERS and check_pw(password, USERS[username]['password']):
        user = User()
        user.id = username
        if user:
            login_user(user=user, remember=True)
            return True
    return False
