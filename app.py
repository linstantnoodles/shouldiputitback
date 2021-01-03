import time
import urllib
import query_lib
from diskcache import Cache
from flask import Flask, request, jsonify, render_template, flash, redirect, url_for, make_response
from flask_mongoengine import MongoEngine
from flask_login import LoginManager, current_user, login_user
from models import BusinessRepository, FormRepository, eval_filter

app = Flask(__name__)

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

@app.route('/items/new', methods=["GET"])
def new_item():
    business_repo = BusinessRepository()
    form_repo = FormRepository()
    business_repo.create("prog")
    business = business_repo.find_by_id(1)
    item_form = form_repo.find_by_type(1, "form")
    field_data = { question.field:"" for question in item_form.questions }
    def visible_condition(filters=None):
        if not filters:
            return "true"
        return eval_filter(filters) 
    return render_template("item.html", form=item_form, field_data=field_data, visible_condition=visible_condition)

@app.route('/items/create', methods=["POST"])
def item():
    print(request.form)
    data = {'message': 'Created', 'code': 'SUCCESS'}
    return make_response(jsonify(data), 201)

@app.route('/')
def index():
    return render_template("index.html")

@app.route('/search')
def search():
    query, cost, pages, filter = request.args['query'], request.args.get('cost', None), request.args.get('pages', 1), request.args.get('filter', 'sold')
    query_encoded = urllib.parse.quote(query)
    items = query_lib.get_items(query_encoded, num_pages=int(pages), filter=filter)
    link_to_results = query_lib.get_search_url(query_encoded, filter=filter)
    statistics = query_lib.analytics(items)
    num_items = len(items)
    selling_fee_amt = statistics.get("fee")
    avg_item_price = statistics.get("avg")
    avg_item_revenue = statistics.get("net")
    breakeven_price = '{:,.2f}'.format(round((float(cost) / 0.8), 2)) if cost else None
    log_search(link_to_results)
    return render_template(
        "search.html",
        items = items,
        query = query,
        filter = filter,
        link_to_results = link_to_results,
        cost = cost,
        num_items = num_items,
        selling_fee_amt = selling_fee_amt,
        avg_item_price = avg_item_price,
        avg_item_revenue = avg_item_revenue,
        breakeven_price = breakeven_price,
        pages = pages
    )

def log_search(url):
    from datetime import datetime
    curr_time = datetime.utcnow()
    with Cache(cache.directory) as reference:
        reference.set(curr_time, url, expire=2592000)
