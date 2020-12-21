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
    return (request.args['query'])

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
