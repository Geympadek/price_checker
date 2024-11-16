import loader
from loader import dp, bot, database

import asyncio

from aiogram import types
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.filters import Command, StateFilter
from aiogram import F

import menu
import update

import config

import products

from log import log

@dp.startup()
async def on_startup():
    log("Bot's running!")

@dp.message(Command("start"))
async def on_start(msg: types.Message, state: FSMContext):
    log(f"/start on user {msg.from_user.first_name}.")

    await msg.answer(text="Привет!\nЭтот бот следит за ценами на маркетплейсах и уведомляет об их изменении.")
    await display_menu(msg.from_user.id, state)

async def display_menu(chat_id: int, state: FSMContext):
    log("Displaying menu.")

    kb = menu.MAIN_MENU_KB
    await bot.send_message(chat_id, "Меню :D", reply_markup=kb)

async def add_product(chat_id: int, state: FSMContext):
    log("Adding a new product")
    await ask_article(chat_id, state)

@dp.callback_query(F.data == "add_product")
async def add_product_on_query(query: CallbackQuery, state: FSMContext):
    await add_product(query.from_user.id, state)

@dp.message(Command("add"))
async def add_product_message(msg: Message, state: FSMContext):
    await add_product(msg.from_user.id, state)

async def list_products(chat_id: int, state: FSMContext):
    log("Listing all the products")
    text, kb = await menu.list_products(chat_id, state)

    await bot.send_message(chat_id, text, reply_markup=kb)

@dp.message(Command("list"))
async def list_products_command(msg: Message, state: FSMContext):
    await list_products(msg.from_user.id, state)

@dp.callback_query(F.data == "list_products")
async def list_products_on_query(query: CallbackQuery, state: FSMContext):
    await list_products(query.from_user.id, state)

@dp.callback_query(F.data.startswith("product_selected"))
async def product_selected(query: CallbackQuery, state: FSMContext):
    log("Product selected.")

@dp.callback_query(F.data.startswith("products_controls"))
async def product_controls(query: CallbackQuery, state: FSMContext):
    log("Arrow btn pressed.")

    usr_data = await state.get_data()

    data = query.data
    direction = data.split(':', 1)[1]

    page = usr_data["products_page"]

    if direction == "left":
        usr_data["products_page"] = max(0, page - 1)
    elif direction == "right":
        usr_data["products_page"] = min(usr_data["products_pages_count"] - 1, page + 1)
    
    await state.set_data(usr_data)

    msg, kb = await menu.list_products(query.from_user.id, state)
    await query.message.edit_reply_markup(reply_markup=kb)

async def ask_article(chat_id: int, state: FSMContext):
    await state.set_state("article")
    await bot.send_message(chat_id, "Введите артикул товара:")

@dp.message(StateFilter("article"))
async def on_article(msg: Message, state: FSMContext):
    data = await state.get_data()

    try:
        article = int(msg.text)
    except:
        await msg.answer("Артикул не может содержать никаких символов кроме цифр.")
        return

    state.set_state(None)

    data["article"] = article
    await state.set_data(data)

    await ask_platform(msg.from_user.id, state)

async def ask_platform(chat_id: int, state: FSMContext):
    await bot.send_message(chat_id, "Выберите платформу товара", reply_markup=menu.PLATFORM_MENU_KB)

@dp.callback_query(F.data.startswith("platform"))
async def on_platform(query: CallbackQuery, state: FSMContext):
    platform = query.data.split(":", 1)[1]
    data = await state.get_data()
    product_id = products.create_product(data["article"], platform)
    products.follow_product(query.from_user.id, product_id)

    name = database.read("products", {"id": product_id})[0]["name"]

    await bot.send_message(query.from_user.id, f'Товар "{name}" успешно добавлен.')

async def main():
    event_loop = asyncio.get_event_loop()
    event_loop.create_task(update.loop())
    
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())