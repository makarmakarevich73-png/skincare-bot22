from aiogram import Dispatcher
from handlers import register_ui_handlers, register_flow_handlers

def register_handlers(dp: Dispatcher):
    register_ui_handlers(dp)
    register_flow_handlers(dp)
