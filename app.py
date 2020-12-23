import time
import urllib
import query_lib
from flask import Flask, request, jsonify, render_template

app = Flask(__name__)

@app.route('/')
def index():
    return render_template("index.html")

@app.route('/search')
def search():
    query, cost, pages = request.args['query'], request.args.get('cost', None), request.args.get('pages', 1)
    items = query_lib.get_items(query, num_pages=int(pages))
    link_to_results = query_lib.get_search_url(query)
    statistics = query_lib.analytics(items)
    num_items = len(items)
    selling_fee_amt = statistics.get("fee")
    avg_item_sold_price = statistics.get("avg")
    avg_item_revenue = statistics.get("net")
    breakeven_price = '{:,.2f}'.format(round((float(cost) / 0.8), 2)) if cost else None
    return render_template(
        "search.html",
        items = items,
        query = query,
        link_to_results = link_to_results,
        cost = cost,
        num_items = num_items,
        selling_fee_amt = selling_fee_amt,
        avg_item_sold_price = avg_item_sold_price,
        avg_item_revenue = avg_item_revenue,
        breakeven_price = breakeven_price,
        pages = pages
    )
