from loader import database

from time import time

from marketplaces import load_name, load_price

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

async def create_product(article: int, platform: str):
    '''
    Creates a new product inside of the db if one doesn't exist yet
    \nReturns id of the product in db
    '''
    plaform_id = platform_to_id(platform)
    product = database.read("products", filters={"platform_id": plaform_id, "article": article})

    if product:
        return int(product[0]["id"])
    
    name = await load_name(article, platform)
    
    if not name:
        return None
    
    price = await load_price(article, platform)

    if not price:
        return None

    data = {
        "platform_id": plaform_id,
        "article": article,
        "name": name,
        "last_followed": int(time())
    }
    database.create("products", data)
    product = database.read("products", filters={"platform_id": plaform_id, "article": article})
    product_id = int(product[0]["id"])
    insert_price(product_id, price)
    return product_id

def follow_product(user_id: int, product_id: int):
    database.create("followed_products", {"user_id": user_id, "product_id": product_id})

def is_followed(product_id: int):
    follows = database.read("followed_products", {"product_id": product_id})
    return len(follows) != 0