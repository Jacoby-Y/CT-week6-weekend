from flask import Blueprint
from flask_login import LoginManager

auth = Blueprint('auth', __name__) # , url_prefix="/auth"

from . import routes