from flask import Blueprint

poke = Blueprint('poke', __name__) # , url_prefix="/auth"

from . import routes