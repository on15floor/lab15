from flask_login import LoginManager, UserMixin

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

        @login_manager.request_loader
        def request_loader(request):
            username = request.form.get('username')
            if username not in USERS:
                return

            user = User()
            user.id = username
            return user


def auth_user(username: str, password: str) -> User:
    if username in USERS and check_pw(password, USERS[username]['password']):
        user = User()
        user.id = username
        return user
