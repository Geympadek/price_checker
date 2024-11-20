from loader import database

from time import time

import marketplaces

def platform_to_id(name: str):
    '''
    Converts name of the platform to id
    '''
    entry = database.read("platforms", filters={"name": name})[0]

    return int(entry["id"]) if entry else None

def platform_from_id(id: int):
    '''
    Converts id of the platform from name
    '''
    entry = database.read("platforms", filters={"id": id})[0]

    return entry["name"] if entry else None

def push_price(product_id: int, price: int):
    '''
    Adds new price to the database with current time
    '''
    data = {
        "product_id": product_id,
        "price": price,
        "date": int(time())
    }
    database.create("prices", data)

def last_price(product_id: int) -> None | int:
    '''
    Returns latest price on product stored in the db
    '''
    prices = database.read("prices", filters={"product_id": product_id})
    
    if not len(prices):
        return None

    last_price = max(prices, key=lambda price: price["price"])
    return last_price["price"]

async def create_product(article: int, platform: str):
    '''
    Creates a new product inside of the db if one doesn't exist yet, load it's price
    \nReturns id of the created product
    '''
    plaform_id = platform_to_id(platform)
    product = database.read("products", filters={"platform_id": plaform_id, "article": article})

    if product:
        return int(product[0]["id"])
    
    info = await marketplaces.load_info(article, platform)
    
    if not info:
        return None
    
    name = info["name"]
    price = info["price"]

    data = {
        "platform_id": plaform_id,
        "article": article,
        "name": name,
        "last_followed": int(time())
    }
    database.create("products", data)
    product = database.read("products", filters={"platform_id": plaform_id, "article": article})
    product_id = int(product[0]["id"])
    push_price(product_id, price)
    return product_id

def follow_product(user_id: int, product_id: int):
    '''
    Creates a new element followed_products table
    '''
    database.create("followed_products", {"user_id": user_id, "product_id": product_id})

def is_followed(product_id: int):
    '''
    Returns true if there's at least one followed_product with that `product_id`
    '''
    follows = database.read("followed_products", {"product_id": product_id})
    return len(follows) != 0

def delete_product_info(product_id: int):
    '''
    Deletes all info about the product and everything that has it's `product_id` in it
    '''
    database.delete("products", {"id": product_id})
    database.delete("prices", {"product_id": product_id})
    database.delete("followed_products", {"product_id": product_id})

if __name__ == "__main__":
    print(last_price(6))