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
    query, cost, pages = request.args['query'], request.args['cost'], request.args['pages']
    items = query_lib.get_items(query, num_pages=int(pages))
    link_to_results = query_lib.get_search_url(query)
    statistics = query_lib.analytics(items)
    num_items = len(items)
    selling_fee_amt = statistics["fee"]
    avg_item_sold_price = statistics["avg"]
    avg_item_revenue = round(statistics["net"], 2)
    breakeven_price = round((float(cost) / 0.8), 2) if cost else None
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
        pages = pages,
    )

@app.route('/time')
def get_current_time():
    with open('brands.json', 'r') as f:
        response = app.response_class(
            response=f.read(),
            mimetype='application/json'
        )
        return response

@app.route('/query')
def query():
    q = request.args.get('query')
    q = urllib.parse.quote(q)
    url = f"https://poshmark.com/search?query={q}"
    search_results = query_lib.query_items_from_source(url, q)
    statistics = query_lib.analytics(search_results)
    return jsonify({
        "search_results": search_results,
        "statistics": statistics
    })
