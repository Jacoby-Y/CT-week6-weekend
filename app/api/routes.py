import json
from flask import make_response, redirect, render_template, request, flash, url_for
from flask_login import current_user, login_required, login_user, logout_user
import requests

from app.auth.forms import LoginForm, RegisterForm
from app.models import Pokemon, User
from . import api

@api.get('/poke')
def get_pokes():
    return make_response(json.dumps([poke.to_dict() for poke in Pokemon.query.all()]))

@api.delete('/poke')
def delete_pokes():
    count = 0
    for poke in Pokemon.query.all():
        poke.delete()
        count += 1
    return make_response(f"Deleted {count} Pokemon")
    

@api.get("/user")
def get_users():
    return make_response("{ [ " + f"{', '.join([user.to_json() for user in User.query.all()])}" + " ] }")

@api.get("/user/<int:id>")
def get_user(id):
    return make_response(User.query.filter_by(id=id).first().to_json())