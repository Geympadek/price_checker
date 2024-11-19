from time import time
import asyncio
from aiogram import types

import menu
from loader import database, bot
import marketplaces
import products
from log import log
from config import UPDATE_RATE, PRODUCT_LIFETIME, DISABLE_UPDATE

async def update():
    if DISABLE_UPDATE:
        return

    followed_products = database.read("followed_products")

    for fol_product in followed_products:
        await check_price(fol_product)
    
    update_time = int(time())
    products = database.read("products")
    for product in products:
        update_follow_time(product["id"], update_time)
    # must do separate loops `products` become invalid after update_follow_time
    products = database.read("products")
    for product in products:
        remove_if_old(product, update_time)

async def check_price(fol_product: dict):
    product_id = fol_product["product_id"]
    product = database.read("products", filters={"id": product_id})[0]
    platform_id = product["platform_id"]

    article = int(product["article"])

    last_price = products.last_price(product_id)
    info = await marketplaces.load_info(article, products.platform_from_id(platform_id))

    if not info:
        log(f"Unable to get info about '{product['name']}'")
        return

    price = info["price"]

    if price != last_price:
        # if price has changed, write the change to the database
        products.insert_price(product_id, price)

        if last_price:
            msg = f'Цена на "{product["name"]}" '
            if price < last_price:
                msg += f"снизилась на {(last_price - price) / 100} ₽ 📉"
            else:
                msg += f"повысилась на {(price - last_price) / 100} ₽ 📈"
            
            kb = types.InlineKeyboardMarkup(inline_keyboard=[[
                menu.TO_MENU_BTN, menu.create_product_btn(fol_product, "🛍️ Товар")
            ]])
            await bot.send_message(chat_id=fol_product["user_id"], text=msg, reply_markup=kb)

def update_follow_time(product_id: int, update_time: int):
    if products.is_followed(product_id):
        log(f"Updated follow time of product {product_id}")
        database.update("products", {"last_followed": update_time}, {"id": product_id})
    else:
        log(f"Product {product_id} is not followed, skip time updating")

def remove_if_old(product: dict, update_time: int):
    if update_time - int(product["last_followed"]) > PRODUCT_LIFETIME:
        log(f"Product {product['id']} is too old, deleting all info about it")
        products.delete_product_info(product["id"])

async def loop():
    while True:
        await update()
        await asyncio.sleep(UPDATE_RATE)