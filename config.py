from os import environ
from dotenv import load_dotenv
load_dotenv()

class Config():
    SECRET_KEY = environ.get('SECRET_KEY')
    SQLALCHEMY_DATABASE_URI = environ.get('SQLALCHEMY_DATABASE_URI')
    SQLALCHEMY_TRACK_MODIFICATIONS=False
    SECRET_KEY = environ.get('SECRET_KEY')
