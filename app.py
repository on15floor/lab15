from flask import Flask
from config import Config


app = Flask(__name__)
app.secret_key = Config.FLASK_SECRET_KEY
app.debug = Config.FLASK_DEBUG

# noinspection PyUnresolvedReferences
from core import auth, views, filters
auth.Init(app)
