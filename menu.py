from aiogram import types

import labels
from loader import database

import config

from math import ceil

from aiogram.fsm.context import FSMContext

LIST_PRODUCTS_BTN = types.InlineKeyboardButton(text=labels.LIST_PRODUCTS, callback_data="list_products")
ADD_PRODUCT_BTN = types.InlineKeyboardButton(text=labels.ADD_PRODUCTS, callback_data="add_product")

MAIN_MENU_KB = types.InlineKeyboardMarkup(inline_keyboard=[[LIST_PRODUCTS_BTN, ADD_PRODUCT_BTN]])

OZON_BTN = types.InlineKeyboardButton(text="Ozon", callback_data="platform:ozon")
WB_BTN = types.InlineKeyboardButton(text="Wildberries", callback_data="platform:wildberries")

PLATFORM_MENU_KB = types.InlineKeyboardMarkup(inline_keyboard=[[WB_BTN, OZON_BTN]])

def list_controls(callback_name: str, items_count = 0, page = 0, max_page = 1, page_size = config.ITEMS_PER_PAGE):
    if items_count <= page_size:
        return None
    
    btns = []
    btns.append(types.InlineKeyboardButton(text="<", callback_data=f"{callback_name}:left"))
    btns.append(types.InlineKeyboardButton(text=f"{page + 1}/{max_page}", callback_data=" "))
    btns.append(types.InlineKeyboardButton(text=">", callback_data=f"{callback_name}:right"))

    return btns
    
async def list_products(user_id: int, state: FSMContext):
    usr_data = await state.get_data()

    fol_products = database.read("followed_products", {"user_id": user_id})

    followed_count = len(fol_products)

    msg = ""
    btns = []
    if not fol_products or followed_count == 0:
        msg = "Список отслеживаемых товаров пуст."
        btns.append([ADD_PRODUCT_BTN])
    else:
        msg = f"Вы отслеживаете цены {followed_count} товаров"

        page = usr_data.setdefault("products_page", 0)
        max_page = usr_data.setdefault("products_pages_count", ceil(followed_count / config.ITEMS_PER_PAGE))

        start_index = page * config.ITEMS_PER_PAGE
        end_index = start_index + config.ITEMS_PER_PAGE

        for fol_product in fol_products[start_index:end_index]:
            product_id = fol_product["product_id"]
            product = database.read("products", filters={"id": product_id})[0]

            name = product["name"]
            btns.append([types.InlineKeyboardButton(
                text=name,
                callback_data=f"product_selected:{product_id}"
            )])
        
        controls = list_controls("products_controls", followed_count, page, max_page)
        if controls:
            btns.append(controls)
    
    await state.set_data(usr_data)

    return msg, types.InlineKeyboardMarkup(inline_keyboard=btns)