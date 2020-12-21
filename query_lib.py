import requests
import os
import sys
import json
from bs4 import BeautifulSoup 
import argparse
from diskcache import Cache

cache = Cache('tmp')

def query_items_from_source(url, query, limit=None): 
    params = "&department=Women&availability=sold_out&sort_by=best_match&all_size=true&my_size=false"
    full_url = f"{url}{params}"
    print(f"Querying items from {full_url}")
    with Cache(cache.directory) as reference:
        results = reference.get(full_url)
        if results:
            return process_data(json.loads(results), query)
    response = requests.get(full_url) 
    data_soup = BeautifulSoup(response.text, features="html.parser")
    cards = data_soup.find_all("div", class_="card card--small")
    results = []
    limit = limit or len(cards)
    for card in cards[:limit]:
        item_path = card.find("a", class_="tile__covershot")['href']
        try: 
            info = item_information(item_path)
            results.append(info)
        except Exception as e:
            print(f"Error: {e} for {item_path}")
    with Cache(cache.directory) as reference:
        reference.set(full_url, json.dumps(results), expire=3600)
    return process_data(results, query)

def process_data(data, query):
    query = query.lower()
    query_items = set([q.strip() for q in query.split(" ")])
    data = sorted(data, key=lambda x: int(x["sold_price"]), reverse=True)
    # filtered_data = []
    # for d in data:
    #     title =  d['title']
    #     details =  d['details']
    #     body = (title + details).lower()
    #     filtered_data.append(d)
    # data = filtered_data
    return data
    
def analytics(data):
    targetCategories = set(["Accessories",
        "Bags",
        "Dresses",
        "Intimates & Sleepwear",
        "Jackets & Coats",
        "Jeans",
        "Jewelry",
        "Makeup",
        "Pants & Jumpsuits",
        "Shoes",
        "Shorts",
        "Skirts",
        "Sweaters",
        "Swim",
        "Tops",
        "Skincare",
        "Hair",
        "Bath & Body",
        "all"
    ])
    categories = set([])
    for item in data:
        for t in item["tags"]:
            if t in targetCategories:
                categories.add(t)
    res = {
        "averages": {
            "all": {
                "count": len(data),
                "avg": Average([int(x["sold_price"]) for x in data])
            }
        }
    }
    exclude = set(["Women"]) 
    for c in [x for x in categories if x not in exclude]:
        res["averages"][c] = avg_price(c, data)
    return res

def Average(lst):
    return round(sum(lst) / len(lst), 2)

def avg_price(c, data):
    matches = []
    for d in data:
        if c in d["tags"]:
            matches.append(d)
    sps = [int(x["sold_price"]) for x in matches]
    return {
        "count": len(sps),
        "avg": Average(sps)
    }

def item_information(item_path):
    base_url = "https://poshmark.com"
    full_url = f"{base_url}{item_path}" 
    print(f"Checking {full_url}")
    response = requests.get(full_url) 
    data_soup = BeautifulSoup(response.text, features="html.parser")
    title = data_soup.find("div", class_="listing__title").find("h1").text.strip()
    brand_name = data_soup.find("a", class_="listing__brand").text.strip()
    prices = [x.strip() for x in data_soup.find("div", class_="listing__ipad-centered").find("h1").text.split('\n') if x.strip()]
    slide_images = data_soup.find("div", class_="slideshow").find_all("img")
    sold_price = prices[0].replace("$","")
    list_price = prices[1].replace("$","")
    size = data_soup.find("button", class_="size-selector__size-option").text
    details = data_soup.find("div", class_="listing__description").text.strip()
    tags = data_soup.find_all("a", class_="tag-details__btn")
    tags = [x.text.strip() for x in tags]
    images = [x["src"] for x in slide_images if x["src"]]
    res = {
        "title": title,
        "url": full_url,
        "brand_name": brand_name,
        "sold_price": sold_price,
        "list_price": list_price,
        "images": images,
        "details": details,
        "size": size,
        "tags": tags
    }
    return res


if __name__ == '__main__': 
    # JjAanalyze()
    # write_brands()
    url = "https://poshmark.com/search?query=premise%20studio"
    url = "https://poshmark.com/search?query=beatrix%20ost&type=listings&src=dir"
    url = "https://poshmark.com/search?query=flying%20monkey%20jeans&type=listings&src=dir"
    url = "https://poshmark.com/search?query=bdg%20mid%20rise%20slim%20straight&type=listings&src=dir"
    url = "https://poshmark.com/search?query=7%20for%20all%20mankind%20dojo&type=listings&src=dir"
    url = "https://poshmark.com/search?query=natural%20reflections&type=listings&src=dir"
    url = "https://poshmark.com/search?query=lavender%20field&type=listings&src=dir"
    url = "https://poshmark.com/search?"
    import urllib
    argument_parser = argparse.ArgumentParser()
    argument_parser.add_argument("query")
    args = argument_parser.parse_args()
    query = urllib.parse.quote(args.query)
    url = f"https://poshmark.com/search?query={query}"
    query_items_from_source(url, args.query)

