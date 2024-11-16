import requests
from loader import database

from time import time

def load_price(id: int, platform: str):
    '''
    Get product's price
    '''
    if platform == "wildberries":
        url = f"https://card.wb.ru/cards/v2/detail?appType=1&curr=rub&dest=-971647&spp=30&ab_testing=false&nm={id}"
        
        try:
            data = requests.get(url).json()
            products = data["data"]["products"]
            
            price = products[0]["sizes"][0]["price"]["total"]
            return int(price)
        except:
            return None

def load_name(id: int, platform: str):
    if platform == "wildberries":
        url = f"https://card.wb.ru/cards/v2/detail?appType=1&curr=rub&dest=-971647&spp=30&ab_testing=false&nm={id}"
        data = requests.get(url).json()

        products = data["data"]["products"]

        if len(products) == 0:
            return None
        
        name = products[0]["name"]
        return name

def platform_to_id(name: str):
    entry = database.read("platforms", filters={"name": name})[0]

    return int(entry["id"]) if entry else None

def platform_from_id(id: int):
    entry = database.read("platforms", filters={"id": id})[0]

    return entry["name"] if entry else None

def insert_price(product_id: int, price: int):
    data = {
        "product_id": product_id,
        "price": price,
        "date": int(time())
    }
    database.create("prices", data)

def last_price(product_id: int):
    '''
    Returns latest price stored in the db   
    '''
    prices = database.read("prices", filters={"product_id": product_id})
    
    if not prices:
        return None

    last_date = 0
    last_price = None
    for price in prices:
        date = int(price["date"])
        if last_date < date:
            last_date = date
            last_price = price

    return last_price["price"]

def create_product(article: int, platform: str):
    '''
    Creates a new product inside of the db if one doesn't exist yet
    \nReturns id of the product in db
    '''
    plaform_id = platform_to_id(platform)
    product = database.read("products", filters={"platform_id": plaform_id, "article": article})

    if product:
        return product[0]["id"]
    
    name = load_name(article, platform)

    data = {
        "platform_id": plaform_id,
        "article": article,
        "name": name
    }
    database.create("products", data)
    return create_product(article, platform)

def follow_product(user_id: int, product_id: int):
    database.create("followed_products", {"user_id": user_id, "product_id": product_id})