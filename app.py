import time
import urllib
import query_lib
from diskcache import Cache
from flask import Flask, request, jsonify, render_template, flash, redirect, url_for
from flask_mongoengine import MongoEngine
from flask_login import LoginManager, current_user, login_user
from forms import LoginForm

app = Flask(__name__)
login = LoginManager(app)

from models import User

app.config['MONGODB_SETTINGS'] = {
    'db': 'closetwitch',
    'host': '127.0.0.1',
    'port': 27017
}

# FIXME: replace with env value soon
app.config['SECRET_KEY'] = 'you-will-never-guess'
db = MongoEngine(app)

cache = Cache('search-tmp')

@app.route('/login', methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.objects(username=form.username.data).first()
        if user is None or not user.check_password(form.password.data):
            flash("Invalid username or password")
            return redirect(url_for('login'))
        login_user(user, remember=form.remember_me.data)
        return redirect('/index')
    return render_template('login.html', title='Sign In', form=form)

@app.route('/')
def index():
    return render_template("index.html")

@app.route('/search')
def search():
    query, market, filter = request.args['query'], request.args.get('market', "Women"), request.args.get('filter', 'sold')
    query_encoded = urllib.parse.quote(query)
    items = query_lib.get_items(query_encoded, market=market, filter=filter)
    link_to_results = query_lib.get_search_url(query_encoded, market=market, filter=filter)
    statistics = query_lib.analytics(items)
    num_items = len(items)
    avg_item_price = statistics.get("avg")
    log_search(link_to_results)
    return render_template(
        "search.html",
        items = items,
        query = query,
        filter = filter,
        market = market,
        link_to_results = link_to_results,
        num_items = num_items,
        avg_item_price = avg_item_price
    )

@app.route('/inventory')
def inventory():
    import json
    with open("items.json", "r") as f:
        items = json.loads(f.read())
        return render_template("inventory.html", items=items)

def log_search(url):
    from datetime import datetime
    curr_time = datetime.utcnow()
    with Cache(cache.directory) as reference:
        reference.set(curr_time, url, expire=2592000)
