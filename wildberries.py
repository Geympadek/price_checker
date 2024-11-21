import requests
import asyncio

def async_get(*args):
    return asyncio.to_thread(requests.get, *args)

async def load_json(id: int) -> dict:
    url = f"https://card.wb.ru/cards/v2/detail?appType=1&curr=rub&dest=-971647&spp=30&ab_testing=false&nm={id}"
    data = (await async_get(url)).json()
    return data["data"]["products"]

async def load_info(id: int):
    try:
        products = await load_json(id)

        name = products[0]["name"]
        
        price = int(products[0]["sizes"][0]["price"]["total"])
        return {"name": name, "price": price / 100}
    except:
        return None