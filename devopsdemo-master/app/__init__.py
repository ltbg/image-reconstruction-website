from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
import pymysql
pymysql.install_as_MySQLdb()
import os
APP_ROOT = os.path.dirname(os.path.abspath(__file__))
from flask_bootstrap import Bootstrap


app = Flask(__name__, static_url_path='')
bootstrap = Bootstrap(app)
app.config.from_object('config')
db = SQLAlchemy(app)
lm = LoginManager()
lm.init_app(app)
lm.login_view = 'login'

from app import views, models
