import os
from logging.handlers import RotatingFileHandler
import logging

import redis
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_bootstrap import Bootstrap

from app.config import Config


redis = redis.Redis(host=os.environ.get('REDIS_HOST'),
                    port=os.environ.get('REDIS_PORT'),
                    db=os.environ.get('REDIS_DB'))
app = Flask(__name__)
app.config.from_object(Config)
db = SQLAlchemy(app)
login = LoginManager(app)
login.login_view = 'auth.login'
bootstrap = Bootstrap(app)

db.Model.metadata.reflect(db.engine)

if not os.path.exists('logs'):
        os.mkdir('logs')
file_handler = RotatingFileHandler('logs/redditclone.log', maxBytes=10240,
                                   backupCount=10)
file_handler.setFormatter(logging.Formatter(
    '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'))
file_handler.setLevel(logging.INFO)
app.logger.addHandler(file_handler)
app.logger.setLevel(logging.INFO)
app.logger.info('redditclone startup')

# need this after db is created to avoid circular imports issue
# with undefined variable

from app.main import bp as main_bp
app.register_blueprint(main_bp)
from app.auth import bp as auth_bp
app.register_blueprint(auth_bp)

# def create_app(config=Config):
#     db.init_app(app)
#     db.Model.metadata.reflect(db.engine)
#     login.init_app(app)


from app import models