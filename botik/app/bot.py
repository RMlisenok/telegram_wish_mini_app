import asyncio
from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties

from app.config import BOT_TOKEN
from app.handlers.start import router as start_router
from app.handlers.recommendations import router as rec_router

async def main():
    bot = Bot(
        token=BOT_TOKEN,
        default=DefaultBotProperties(parse_mode="HTML"),
    )

    dp = Dispatcher()
    dp.include_router(start_router)
    dp.include_router(rec_router)

    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
