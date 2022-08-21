import os

from dotenv import load_dotenv

load_dotenv()


PROJECT_PATH = os.getenv('FLASK_PATH')
STATIC_PATH = os.path.join(PROJECT_PATH, 'static')


class Config:
    FLASK_ADMIN = os.getenv('FLASK_ADMIN')
    FLASK_ADMIN_PWD = os.getenv('FLASK_ADMIN_PWD')
    FLASK_SECRET_KEY = os.getenv('FLASK_SECRET_KEY')
    FLASK_DEBUG = os.getenv('FLASK_DEBUG') == 'True'


class DataBase:
    SQL_MAIN = os.path.join(PROJECT_PATH, 'db/db.sqlite3')

    MONGO_USER = os.getenv('MONGO_USER')
    MONGO_PASS = os.getenv('MONGO_PASS')
    MONGO_CONN_STRING = f'mongodb+srv://{MONGO_USER}:{MONGO_PASS}' \
                        f'@cluster0.f5t4t.mongodb.net/' \
                        f'myFirstDatabase?retryWrites=true&w=majority'


class Tokens:
    BINANCE_API_KEY = os.getenv('BINANCE_API_KEY')
    BINANCE_API_SECRET = os.getenv('BINANCE_API_SECRET')
    TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
    API_TOKEN = os.getenv('API_TOKEN')


class Vars:
    HOST_LGN = os.getenv('HOST_LGN')
    HOST_PWD = os.getenv('HOST_PWD')
    HOST_SRV = os.getenv('HOST_SRV')
    SNOWY_MONTH = (1, 12)
