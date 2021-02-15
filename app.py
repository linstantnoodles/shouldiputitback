import os
import time
import urllib
import query_lib
from diskcache import Cache
from flask import Flask, request, jsonify, render_template, flash, redirect, url_for
from flask_mongoengine import MongoEngine
from flask_login import LoginManager, current_user, login_user, logout_user
from dotenv import load_dotenv
load_dotenv()

app = Flask(__name__)
login = LoginManager(app)

app.config['MONGODB_SETTINGS'] = {
    'db': os.getenv("DB_NAME", "closetwitch"),
    'host': os.getenv("DB_HOST", "127.0.0.1"),
    'port': os.getenv("DB_PORT", 27017),
    'username': os.getenv("DB_USERNAME", ""),
    'password': os.getenv("DB_PASSWORD", "")
}

# For flask login
app.config['SECRET_KEY'] = os.getenv("SECRET_KEY")
db = MongoEngine(app)

cache = Cache('search-tmp')

from models import User
from forms import LoginForm, SignupForm

@app.after_request
def set_secure_headers(response):
    response.headers["Strict-Transport-Security"] = "max-age=63072000; includeSubDomains; preload"
    response.headers["X-Frame-Options"] = 'SAMEORIGIN'
    return response 

@app.route('/signup', methods=["GET", "POST"])
def signup(): 
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = SignupForm()
    if form.validate_on_submit():
        user = User(email=form.email.data)
        user.set_password(form.password.data)
        user.save()
        flash('Congratulations, you are now a registered user!')
        return redirect(url_for("login"))
    return render_template('signup.html', title='Sign up', form=form)

@app.route('/login', methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.objects(email=form.email.data).first()
        if user is None or not user.check_password(form.password.data):
            flash("Invalid email or password")
            return redirect(url_for('login'))
        login_user(user, remember=form.remember_me.data)
        return redirect(url_for('index'))
    return render_template('login.html', title='Sign In', form=form)

@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('login'))

@app.route('/')
def index():
    return render_template("comp.html")

@app.route('/share')
@app.route('/sharespell')
def sharespell():
    return render_template("sharespell.html")

@app.route("/comp")
def comp():
    return render_template("comp.html")

@app.route("/about")
def about():
    return render_template("about.html")

@app.route("/contact")
def contact():
    return render_template("contact.html")

@app.route('/comp/search')
def search():
    query, market, filter, page_number = request.args['query'], request.args.get('market', "Women"), request.args.get('filter', 'sold'), request.args.get('page_number')
    query_encoded = urllib.parse.quote(query)
    items = query_lib.get_items_by_page(query_encoded, page_number=page_number, market=market, filter=filter)
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
