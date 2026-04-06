import sys
import os
from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode
from aiogram.client.default import DefaultBotProperties
from app.api.routers.bot_router import router as bot_router


TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
print(f"DEBUG: Loaded token is: {TOKEN}")

if not TOKEN:
    TOKEN = "8558976967:AAFnChpNZ6TBoXOai-5OAilw0Mc1Dv_a7Go"

bot = Bot(token=TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
dp = Dispatcher()

dp.include_router(bot_router)
