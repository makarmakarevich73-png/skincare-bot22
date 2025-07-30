import os
import asyncio
import threading
from flask import Flask, request
from dotenv import load_dotenv

from aiogram import Bot, Dispatcher, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage

from main import register_handlers

load_dotenv()
BOT_TOKEN = os.getenv("BOT_TOKEN")
if not BOT_TOKEN:
    raise RuntimeError("BOT_TOKEN is not set. Define it in .env or hosting Variables")

app = Flask(__name__)

# Background event loop for aiogram 2.x
loop = asyncio.new_event_loop()
asyncio.set_event_loop(loop)
threading.Thread(target=loop.run_forever, daemon=True).start()

bot = Bot(token=BOT_TOKEN, parse_mode="HTML")
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage, loop=loop)
register_handlers(dp)

@app.route("/", methods=["GET"])
def health():
    return "Bot webhook is alive ✓", 200

@app.route("/", methods=["POST"])
def telegram_webhook():
    data = request.get_json(force=True, silent=True)
    if not data:
        return "no data", 400
    update = types.Update.to_object(data)
    asyncio.run_coroutine_threadsafe(dp.process_update(update), loop)
    return "ok", 200

# Helpers to set/delete webhook once deployed
@app.route("/set-webhook", methods=["GET"])
def set_webhook():
    url = request.url_root
    fut = asyncio.run_coroutine_threadsafe(bot.set_webhook(url), loop)
    try:
        ok = fut.result(timeout=10)
    except Exception as e:
        return f"set_webhook error: {e}", 500
    return f"set_webhook: {ok}", 200

@app.route("/delete-webhook", methods=["GET"])
def delete_webhook():
    fut = asyncio.run_coroutine_threadsafe(bot.delete_webhook(), loop)
    try:
        ok = fut.result(timeout=10)
    except Exception as e:
        return f"delete_webhook error: {e}", 500
    return f"delete_webhook: {ok}", 200
