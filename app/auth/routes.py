from flask import redirect, render_template, request, flash, url_for
from flask_login import current_user, login_required, login_user, logout_user

from app.auth.forms import LoginForm, RegisterForm
from app.models import Pokemon, User
from . import auth

#region | Index
@auth.get('/')
def index():
    return render_template('index.html.j2')
#endregion

#region | Login Things
@auth.get('/login')
def get_login():
    return render_template('login.html.j2', form=LoginForm())

@auth.post('/login')
def post_login():
    form = LoginForm()
    if not form.validate_on_submit():
        flash("Not a valid login", "warning")
        return render_template('login.html.j2', form=LoginForm())
    email = form.email.data.lower()
    password = form.password.data

    u = User.query.filter_by(email=email).first()
    if u and u.check_hashed_password(password):
        #Login Success!!!!!
        flash('Successfully logged in','success')
        login_user(u)
        return redirect(url_for('auth.index'))
    flash("Not a valid login", "warning")
    return render_template('login.html.j2', form=form)

@auth.get('/register')
def get_register():
    return render_template('register.html.j2', form=RegisterForm())

@auth.post('/register')
def post_register():
    form = RegisterForm()
    try:
        new_user_data={
            "first_name": form.first_name.data.title(),
            "last_name": form.last_name.data.title(),
            "email": form.email.data.lower(),
            "password": form.password.data,
            "icon": form.icon.data
        }
        # Create an Empty user
        new_user_object = User()

        #build our user from the form data
        new_user_object.from_dict(new_user_data)
        print(new_user_object.to_dict())

        # Save new user to the database
        new_user_object.save()
    except:
        # Flash user Error
        flash("An Unexpected Error occurred", "danger")
        return render_template('register.html.j2', form=form)
    # Flash user here telling you have been register
    flash("Successfully registered", "success")
    return redirect(url_for('auth.get_login'))

@auth.get('/logout')
def get_logout():
    logout_user()
    flash('Successfully logged out', 'info')
    return redirect(url_for('auth.get_login'))

#endregion

#region | Profile Stuff
@auth.post('/edit-profile')
@login_required
def edit_profile():
    data = request.form.to_dict()
    data["icon"] = current_user.icon if data["icon"] == "-1" else data["icon"]
    # print(current_user)
    current_user.from_dict(data)
    current_user.save()
    return render_template('index.html.j2')
#endregion

