from time import sleep
import asyncio

from loader import database, bot
import products
from log import log
from config import UPDATE_RATE

async def update():
    followed_products = database.read("followed_products")

    for fol_product in followed_products:
        product_id = fol_product["product_id"]
        product = database.read("products", filters={"id": product_id})[0]
        platform_id = product["platform_id"]

        article = int(product["article"])

        last_price = products.last_price(product_id)
        price = products.load_price(article, products.platform_from_id(platform_id))

        if not price:
            log(f"Unable to get the price of '{product['name']}'")
            continue

        if price != last_price:
            products.insert_price(product_id, price)

            if last_price:
                msg = f'Цена на "{product["name"]}" '
                if price < last_price:
                    msg += f"снизилась на {(last_price - price) / 100} ₽"
                else:
                    msg += f"повысилась на {(price - last_price) / 100} ₽"

                await bot.send_message(chat_id=fol_product["user_id"], text=msg)

async def loop():
    while True:
        await update()
        await asyncio.sleep(UPDATE_RATE)