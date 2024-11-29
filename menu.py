from aiogram import types
from aiogram.fsm.context import FSMContext
from math import ceil

from loader import database
import config
import products

CANCEL_BTN = types.InlineKeyboardButton(text="✖️ Отмена", callback_data="cancel")
CANCEL_KB = types.InlineKeyboardMarkup(inline_keyboard=[[CANCEL_BTN]])

TO_MENU_BTN = types.InlineKeyboardButton(text="⬅️ Меню", callback_data="menu")
TO_MENU_KB = types.InlineKeyboardMarkup(inline_keyboard=[[TO_MENU_BTN]])

LIST_PRODUCTS_BTN = types.InlineKeyboardButton(text="📋 Товары", callback_data="list_products")
ADD_PRODUCT_BTN = types.InlineKeyboardButton(text="➕ Добавить", callback_data="add_product")

FEEDBACK_BTN = types.InlineKeyboardButton(text="💬 Контакты", callback_data="feedback")

WB_BTN = types.InlineKeyboardButton(text="🟣 Wildberries", callback_data="platform:wildberries")
OZON_BTN = types.InlineKeyboardButton(text="🔵 Ozon", callback_data="platform:ozon")

PLATFORM_MENU_KB = types.InlineKeyboardMarkup(inline_keyboard=[[WB_BTN, OZON_BTN], [CANCEL_BTN]])

MAIN_MENU_KB = types.InlineKeyboardMarkup(inline_keyboard=[
    [LIST_PRODUCTS_BTN],
    [ADD_PRODUCT_BTN, FEEDBACK_BTN]
])

def list_controls(callback_prefix: str, items_count = 0, page = 0, max_page = 1, page_size = config.ITEMS_PER_PAGE):
    """
    Creates control buttons at the bottom of a list so that it's possible to display more than `config.ITEMS_PER_PAGE` elements
    \n`callback_name` - prefix, that appears before all callback_data
    \n`items_count` - number of elements in the list
    \n`page` - current page index (starting from zero)
    \n`max_page` - number of pages
    \n`page_size` - size of a single page
    """
    if items_count <= page_size:
        return None
    
    btns = []
    btns.append(types.InlineKeyboardButton(text="<", callback_data=f"{callback_prefix}:left"))
    btns.append(types.InlineKeyboardButton(text=f"{page + 1}/{max_page}", callback_data=" "))
    btns.append(types.InlineKeyboardButton(text=">", callback_data=f"{callback_prefix}:right"))

    return btns

def create_product_btn(fol_product: dict, text: str | None = None):
    """
    Returns a button that leads user to the followed product's page
    \n`fol_product` - followed_product from the database
    \n`text` - text displayed on the button. If null, displays the name of the product
    """
    product_id = fol_product["product_id"]

    if not text:
        product = database.read("products", filters={"id": product_id})[0]
        text = product["name"]
    
    return types.InlineKeyboardButton(
        text=text,
        callback_data=f"product_selected:{fol_product['id']}"
    )

def create_info_btn(data: str):
    """
    Creates a question button, with `callback_data` prefix - `"info:"`
    """
    return types.InlineKeyboardButton(
        text="❔",
        callback_data=f"info:{data}"
    )

async def list_products(user_id: int, state: FSMContext):
    """
    Creates a list of all the of followed products by the user, if the size is bigger than `config.ITEMS_PER_PAGE`, adds navigation buttons  
    \n`user_id` - id of the user
    \n`state` - fsm state machine for getting and setting data (such as current page index)
    \n`return` - message and keyboard for sending
    """
    usr_data = await state.get_data()

    fol_products = database.read("followed_products", {"user_id": user_id})

    followed_count = len(fol_products)

    msg = ""
    btns = []
    if followed_count == 0:
        msg = "Список отслеживаемых товаров пуст."
        btns.append([ADD_PRODUCT_BTN])
    else:
        msg = f"Вы отслеживаете цены {followed_count} товаров"

        page = usr_data.setdefault("products_page", 0)
        max_page = usr_data.setdefault("products_pages_count", ceil(followed_count / config.ITEMS_PER_PAGE))

        start_index = page * config.ITEMS_PER_PAGE
        end_index = start_index + config.ITEMS_PER_PAGE

        for fol_product in fol_products[start_index:end_index]:
            btns.append([create_product_btn(fol_product)])
        
        controls = list_controls("products_controls", followed_count, page, max_page)
        if controls:
            btns.append(controls)
    
    await state.set_data(usr_data)

    return msg, types.InlineKeyboardMarkup(inline_keyboard=btns)

def product_menu(fol_product_id: int):
    """
    Creates product's page
    `fol_product_id` - id of the followed_product
    `return` - msg and keyboard for sending
    """
    fol_product = database.read("followed_products", {"id": fol_product_id})[0]
    product_id = fol_product["product_id"]
    product = database.read("products", {"id": product_id})[0]

    name = product["name"]
    article = product["article"]
    platform = products.platform_from_id(product["platform_id"])

    price = products.last_price(product_id)

    text = f'<b>{name}</b>'\
            f'\n\nПлатформа: {platform}'\
            f'\nАртикул: <code>{article}</code>'\
            f'\nТекущая цена: {price} ₽'
    
    link = ""
    if platform == "wildberries":
        link = f"https://www.wildberries.ru/catalog/{article}/detail.aspx"
    elif platform == "ozon":
        link = f"https://www.ozon.ru/product/{article}"

    buy_btn = types.InlineKeyboardButton(text="🛒 Купить", url=link)
    remove_btn = types.InlineKeyboardButton(text="❌ Удалить", callback_data=f"remove_product:{fol_product_id}")
    return text, types.InlineKeyboardMarkup(inline_keyboard=[[buy_btn], [TO_MENU_BTN, remove_btn]])