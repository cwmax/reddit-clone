from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_bootstrap import Bootstrap

from app.config import Config


app = Flask(__name__)
app.config.from_object(Config)
db = SQLAlchemy(app)
login = LoginManager(app)
login.login_view = 'auth.login'
bootstrap = Bootstrap(app)

db.Model.metadata.reflect(db.engine)

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