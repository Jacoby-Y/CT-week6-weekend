from flask import Flask
from flask_login import LoginManager
from config import Config
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

db = SQLAlchemy()
login = LoginManager()
migrate = Migrate()

def create_app():
  app = Flask(__name__)

  app.config.from_object(Config)

  db.init_app(app)
  login.init_app(app)
  migrate.init_app(app, db)
  
  login.login_view = 'auth.get_login'
  login.login_message = "Login yourself in, please (:"
  login.login_message_category = "info"

  from .auth import auth
  app.register_blueprint(auth)

  from .poke import poke
  app.register_blueprint(poke)

  from .api import api
  app.register_blueprint(api)

  return app

import app.models