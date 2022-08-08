import random
from flask import redirect, render_template, request, flash, url_for
from flask_login import current_user, login_required, login_user, logout_user
import requests
from sqlalchemy.sql.expression import func

from app.auth.forms import LoginForm, RegisterForm
from app.models import Pokemon, User, pokemon_user
from . import poke
from app import db

#region | Pokemon Stuff
@poke.get('/search')
@login_required
def get_search():
    return render_template('search.html.j2')

@poke.post('/search')
@login_required
def post_search():
    poke_name = request.form.get("search").lower().strip()
    if not poke_name:
        return redirect(request.referrer)
    
    poke_row: Pokemon = Pokemon.query.filter_by(name=poke_name).first()
    if poke_row:
        return render_template('search.html.j2', pokemon=poke_row)

    # get pokemon from pokeapi using name
    res = requests.get(f"https://pokeapi.co/api/v2/pokemon/{poke_name}")
    if not res:
        flash("I can't find that Pokemon!", "warning")
        return redirect(request.referrer)

    poke_json = res.json()

    if "stats" not in poke_json:
        flash("I can't find that Pokemon!", "warning")
        return redirect(request.referrer)
    
    stats = {}
    for stat in poke_json["stats"]:
        stats[stat["stat"]["name"]] = stat["base_stat"]
    
    new_poke = Pokemon()
    new_poke.from_dict({
        "name": poke_name,
        "hp": stats["hp"],
        "attack": stats["attack"],
        "defense": stats["defense"],
        "img": poke_json["sprites"]["front_default"],
    })
    new_poke.save()
    
    return render_template('search.html.j2', pokemon=new_poke)

@poke.get('/catch/<int:id>')
@login_required
def catch(id):
    if len(current_user.pokemons) >= 5:
        flash("You already have enough Pokemon!")
        return
    
    to_catch = Pokemon.query.get(id)
    current_user.pokemons.append(to_catch)
    current_user.save()

    return redirect(request.referrer)

@poke.get('/find-opponent')
@login_required
def find_opponent():
    off = 0
    count = User.query.count()
    if count > 5:
        off = random.randrange(0, count-5)
    fighters = User.query.filter(~User.id.in_([current_user.id])).order_by(func.random()).limit(5).offset(off).all()
    return render_template("find-opp.html.j2", fighters=fighters)

@poke.get("/my-pokemon")
@login_required
def my_pokemon():
    return render_template("my-poke.html.j2")

@poke.get("/release/<int:id>")
@login_required
def release_pokemon(id):
    # db.session.delete(pokemon_user.query.filter_by(pokemon_id=id))
    for i, poke in enumerate(current_user.pokemons):
        if poke.id == id:
            current_user.pokemons.pop(i)
            break
    return render_template("my-poke.html.j2")

@poke.get("/fight/<int:id>")
@login_required
def fight(id):
    opponent = User.query.get(id)
    opp: list[Pokemon] = opponent.pokemons
    usr: list[Pokemon] = current_user.pokemons

    def get_score(poke: Pokemon):
        return poke.hp + poke.attack + poke.defense
    
    def chance_scores(s1, s2):
        return s1 <= random.random()*(s1+s2)
    
    def check_user_win(u, o):
        if u < o:
            return chance_scores(u, o)
        return not chance_scores(o, u)
    
    def append_poke(poke, pokes, win: bool):
        poke.append({ "name": pokes[i].name, "status": "Won!" if win else "Fainted...", "won": win })

    usr_poke = []
    opp_poke = []
    wins = 0
    loss = 0
    for i in range(5):
        usr_s = 0 if i >= len(usr) else get_score(usr[i])
        opp_s = 0 if i >= len(opp) else get_score(opp[i])
        
        if check_user_win(usr_s, opp_s):
            wins += 1
            append_poke(usr_poke, usr, True)
            append_poke(opp_poke, opp, False)
        else:
            loss += 1
            append_poke(opp_poke, opp, True)
            append_poke(usr_poke, usr, False)
        
            

    title = "You Won!"
    if wins == loss:
        title = "It's a Tie!"
    elif wins < loss:
        title = "You lost!"
        if not current_user.losses:
            current_user.losses = 1
        else:
            current_user.losses += 1
        current_user.save()
    else:
        if not current_user.wins:
            current_user.wins = 1
        else:
            current_user.wins += 1
        current_user.save()

    return render_template("fight-summary.html.j2", usr_poke=usr_poke, opp_poke=opp_poke, opp=opponent, title=title)

#endregion
