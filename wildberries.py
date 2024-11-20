import requests

# async def get_async(url):

def load_json(id: int):
    url = f"https://card.wb.ru/cards/v2/detail?appType=1&curr=rub&dest=-971647&spp=30&ab_testing=false&nm={id}"
    data = requests.get(url).json()
    return data["data"]["products"]

def load_info(id: int):
    try:
        products = load_json(id)

        name = products[0]["name"]
        
        price = int(products[0]["sizes"][0]["price"]["total"])
        return {"name": name, "price": price / 100}
    except:
        return None