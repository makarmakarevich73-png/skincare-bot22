import logging
from aiogram import Bot, Dispatcher, executor
from aiogram.contrib.fsm_storage.memory import MemoryStorage  # добавлено
from main import register_handlers

# 🔐 Токен бота
TOKEN = "8389430141:AAE5HTxNDjyXN_xoVASwAJJi4QrkldJ5wyo"

# 🧠 FSM-память
storage = MemoryStorage()

# 🔧 Настройка логгирования
logging.basicConfig(level=logging.INFO)

# 🤖 Инициализация бота и диспетчера
bot = Bot(token=TOKEN)
dp = Dispatcher(bot, storage=storage)  # ← добавили storage

# 📥 Регистрируем все хендлеры
register_handlers(dp)

# 🚀 Запуск
if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True)
