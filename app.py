from flask import Flask
from config import Config


app = Flask(__name__)
app.secret_key = Config.FLASK_SECRET_KEY

from core import auth, views, filters
auth.Init(app)
