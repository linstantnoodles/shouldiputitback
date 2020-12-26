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
