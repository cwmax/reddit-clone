from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager

from app.config import Config
from app.main import bp as main_bp
app = Flask(__name__)
app.config.from_object(Config)
db = SQLAlchemy(app)
login = LoginManager(app)

db.Model.metadata.reflect(db.engine)

app.register_blueprint(main_bp)

# def create_app(config=Config):
#     db.init_app(app)
#     db.Model.metadata.reflect(db.engine)
#     login.init_app(app)


from app import models