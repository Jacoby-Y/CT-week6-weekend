from asyncio import create_task
import json
from app import db, login
from flask_login import UserMixin # THIS IS ONLY FOR THE USER MODEL!!!!!!!!!!!!
from datetime import datetime as dt, timedelta
from werkzeug.security import generate_password_hash, check_password_hash
import secrets

pokemon_user = db.Table(
    'pokemon_user',
    db.Column('pokemon_id', db.Integer, db.ForeignKey('pokemon.id')),
    db.Column('user_id', db.Integer, db.ForeignKey('user.id')),
)

#region | User
class User(UserMixin, db.Model):
    __tablename__ = 'user'

    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String)
    last_name = db.Column(db.String)
    email = db.Column(db.String, unique=True, index=True)
    password = db.Column(db.String)
    created_on = db.Column(db.DateTime, default=dt.utcnow)
    icon = db.Column(db.Integer)
    token = db.Column(db.String, unique=True, index=True)   
    token_exp = db.Column(db.DateTime)
    wins = db.Column(db.Integer)
    losses = db.Column(db.Integer)

    pokemons = db.relationship('Pokemon', secondary='pokemon_user', backref='owners')

    ##################################################
    ############## Methods for Token auth ############
    ##################################################    
    def get_token(self, exp=86400):
        current_time = dt.utcnow()
        # if the token is valid return the token
        if self.token and self.token_exp > current_time + timedelta(seconds=60):
            return self.token
        # There was no token/ it was expired so we make a new one
        self.token=secrets.token_urlsafe(32)
        self.token_exp = current_time + timedelta(seconds=exp)
        self.save()
        return self.token

    def revoke_token(self):
        self.token_exp = dt.utcnow() - timedelta(seconds=60)
    
    @staticmethod
    def check_token(token):
        u = User.query.filter_by(token=token).first()
        if not u or u.token_exp < dt.utcnow():
            return None
        return u


    #########################################
    ############# End Methods for tokens ####
    #########################################

    # should return a unique identifing string
    def __repr__(self):
        return f'<User: {self.email} | {self.id}>'
    
    # Human readable repr
    def __str__(self):
        return f'<User: {self.email} | {self.first_name} {self.last_name}>'

    # salts and hashes our password to make it hard to steal
    def hash_password(self, original_password):
        return generate_password_hash(original_password)

    # compares the user password to the password provided in the login form
    def check_hashed_password(self, login_password):
        return check_password_hash(self.password, login_password)

    #save user to db
    def save(self):
        db.session.add(self) # add the userr to the session
        db.session.commit() # save the stuff in the session to the database

    def delete(self):
        db.session.delete(self) # remove the user from the session
        db.session.commit() # save the stuff in the session to the database
    
    def from_dict(self, data):
        self.first_name=data['first_name']
        self.last_name=data['last_name']
        self.email=data['email']
        self.password=self.hash_password(data['password'])
        self.icon=data['icon']
    

    def to_dict(self):
        return {
            'id': self.id,
            'first_name':self.first_name,
            'last_name':self.last_name,
            'email':self.email,
            'created_on':self.created_on,
            'icon':self.icon,
            'token':self.token
        }
    
    def to_json(self):
        return json.dumps({
            'id': self.id,
            'first_name':self.first_name,
            'last_name':self.last_name,
            'email':self.email,
            'icon':self.icon
        })

    def get_icon_url(self):
        return f"http://avatars.dicebear.com/api/big-smile/{self.icon}.svg"

@login.user_loader
def load_user(id):
    return User.query.get(int(id))
#endregion

#region | Pokemon
class Pokemon(db.Model):
    __tablename__ = 'pokemon'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    hp = db.Column(db.Integer)
    attack = db.Column(db.Integer)
    defense = db.Column(db.Integer)
    img = db.Column(db.String)

    # should return a unique identifing string
    def __repr__(self):
        return f'<Pokemon: {self.name} | {self.id}>'
    
    # Human readable repr
    def __str__(self):
        return f'<Pokemon: {self.name} | {self.id}>'


    #save user to db
    def save(self):
        db.session.add(self) # add the userr to the session
        db.session.commit() # save the stuff in the session to the database

    def delete(self):
        db.session.delete(self) # remove the user from the session
        db.session.commit() # save the stuff in the session to the database
    
    def from_dict(self, data):
        self.name = data['name']
        self.hp = data['hp']
        self.defense = data['defense']
        self.attack = data['attack']
        self.img = data['img']
    

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'hp': self.hp,
            'defense': self.defense,
            'attack': self.attack,
            'img': self.img,
        }

#endregion