import requests
import os
import sys
import json
from bs4 import BeautifulSoup 
import argparse
from diskcache import Cache
import re

cache = Cache('tmp')

def get_items(query, num_pages=1, filter="sold"):
    search_url = get_search_url(query, filter=filter)
    items = []
    for i in range(1, num_pages+1):
        paginated_url = f"{search_url}&max_id={i}"
        items.extend(query_items_from_source(paginated_url, query))
    return items

def get_search_url(query, filter="sold"):
    base_url = f"https://poshmark.com/search?query={query}"
    if filter == "available":
        params = "&department=Women&sort_by=best_match&all_size=true&my_size=false"
    else:
        params = "&department=Women&availability=sold_out&sort_by=best_match&all_size=true&my_size=false"
    return f"{base_url}{params}"

def query_items_from_source(full_url, query, limit=None): 
    with Cache(cache.directory) as reference:
        results = reference.get(full_url)
        if results:
            return json.loads(results)
    response = requests.get(full_url) 
    data_soup = BeautifulSoup(response.text, features="html.parser")
    cards = data_soup.find_all("div", class_="card card--small")
    results = []
    limit = limit or len(cards)
    prog = re.compile(r"(\d{4}/\d{2}/\d{2})")
    for card in cards[:limit]:
        item_path = card.find("a", class_="tile__covershot")['href']
        title = card.find("a", class_="tile__title tc--b").text.strip()
        new_with_tag = True if card.find("span", class_="condition-tag") else False
        like_el = card.find("div", class_="social-action-bar__like").find("span")
        likes = like_el.text if like_el else 0
        image_url = card.find("div", class_="img__container").find("img")["data-src"]
        list_date = prog.search(image_url).group(1)
        price = card.find("div", class_="item__details").find("span", class_="fw--bold").text.replace("$","").replace(",","").strip()
        size_element = card.find("a", class_="tile__details__pipe__size") or card.find("div", class_="tile__details__pipe__size")
        size = size_element.text.strip()
        res = {
            "title": title,
            "url": f"https://poshmark.com{item_path}",
            "image_url": image_url,
            "likes": likes,
            "price": price,
            "new_with_tag": new_with_tag,
            "list_date": list_date,
            "size": size
        }
        results.append(res)
    with Cache(cache.directory) as reference:
        reference.set(full_url, json.dumps(results), expire=3600)
    return results

def analytics(data):
    if not data:
        return {}
    # For sales under $15, the fee is a flat rate of $2.95. For sales above $15, the fee is 20% and you keep 80%.
    def fee_amt(num):
        if num < 15:
            return 2.95
        else:
            return (0.2 * num)
    avg_price = Average([int(x["price"]) for x in data])
    total_count = len(data)
    fee = round(fee_amt(avg_price), 2)
    net = round(avg_price - fee, 2)
    return {
        "count": total_count,
        "avg": avg_price,
        "fee": fee,
        "net": net
    }

def Average(lst):
    return round(sum(lst) / len(lst), 2)

def avg_price(c, data):
    matches = []
    for d in data:
        if c in d["tags"]:
            matches.append(d)
    sps = [int(x["price"]) for x in matches]
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
    res = query_items_from_source(url, args.query)
    print(res)

