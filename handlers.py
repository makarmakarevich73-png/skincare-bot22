\
from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery

from parser import analyze_product

class Steps(StatesGroup):
    waiting_ingredients = State()

def kb_products():
    kb = InlineKeyboardMarkup(row_width=3)
    kb.add(
        InlineKeyboardButton("Крем", callback_data="prod:крем"),
        InlineKeyboardButton("Тоник", callback_data="prod:тоник"),
        InlineKeyboardButton("Умывалка", callback_data="prod:умывалка"),
    )
    return kb

def kb_skin():
    kb = InlineKeyboardMarkup(row_width=3)
    buttons = [
        ("Сухая", "skin:сухая"),
        ("Жирная", "skin:жирная"),
        ("Комбинированная", "skin:комбинированная"),
        ("Нормальная", "skin:нормальная"),
        ("Чувствительная", "skin:чувствительная"),
        ("Зрелая", "skin:зрелая"),
    ]
    for text, data in buttons:
        kb.insert(InlineKeyboardButton(text, callback_data=data))
    return kb

def kb_after_result():
    kb = InlineKeyboardMarkup(row_width=2)
    kb.add(
        InlineKeyboardButton("🔄 Выбрать другой продукт", callback_data="action:change_product"),
        InlineKeyboardButton("➕ Ещё один состав", callback_data="action:another"),
    )
    return kb

async def cmd_start(message: types.Message, state: FSMContext):
    await state.finish()
    await message.answer(
        "Привет! Что проверяем? Выбери тип продукта:",
        reply_markup=kb_products()
    )

async def on_choose_product(call: CallbackQuery, state: FSMContext):
    await call.answer()
    product = call.data.split(":", 1)[1]
    await state.update_data(product_type=product)
    await call.message.edit_text(
        f"Окей, продукт: <b>{product}</b>.\nТеперь выбери тип кожи:",
        reply_markup=kb_skin()
    )

async def on_choose_skin(call: CallbackQuery, state: FSMContext):
    await call.answer()
    skin = call.data.split(":", 1)[1]
    await state.update_data(skin_type=skin)
    await Steps.waiting_ingredients.set()
    await call.message.edit_text(
        f"Тип кожи: <b>{skin}</b>.\nТеперь пришли <b>состав через запятую</b>:"
    )

async def on_ingredients(message: types.Message, state: FSMContext):
    user_data = await state.get_data()
    product_type = user_data.get("product_type")
    skin_type = user_data.get("skin_type")

    ingredients_raw = message.text
    ingredients = [i.strip() for i in ingredients_raw.split(",") if i.strip()]

    result = analyze_product(
        ingredients_list=ingredients,
        product_type=product_type,
        skin_type=skin_type
    )

    await message.answer(
        f"🔍 <b>Результат анализа</b>:\\n{result}",
        reply_markup=kb_after_result()
    )

async def on_action(call: CallbackQuery, state: FSMContext):
    await call.answer()
    action = call.data.split(":", 1)[1]
    data = await state.get_data()

    if action == "change_product":
        await state.finish()
        await call.message.edit_text("Окей, выбери тип продукта:", reply_markup=kb_products())
        return

    if action == "another":
        if not data.get("product_type") or not data.get("skin_type"):
            await state.finish()
            await call.message.edit_text("Похоже, данные потерялись. Выбери тип продукта:", reply_markup=kb_products())
            return
        await Steps.waiting_ingredients.set()
        await call.message.edit_text(
            f"Ещё один состав для <b>{data['product_type']}</b> / кожа: <b>{data['skin_type']}</b>.\\nПришли список через запятую:"
        )

def register_ui_handlers(dp):
    dp.register_message_handler(cmd_start, commands=["start"], state="*")

def register_flow_handlers(dp):
    dp.register_callback_query_handler(on_choose_product, lambda c: c.data and c.data.startswith("prod:"), state="*")
    dp.register_callback_query_handler(on_choose_skin, lambda c: c.data and c.data.startswith("skin:"), state="*")
    dp.register_callback_query_handler(on_action, lambda c: c.data and c.data.startswith("action:"), state="*")
    dp.register_message_handler(on_ingredients, state=Steps.waiting_ingredients)
