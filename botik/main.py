import asyncio
import logging
from datetime import datetime, timedelta
from typing import List

from aiogram import Bot, Dispatcher, F
from aiogram.types import (
    Message,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
    CallbackQuery,
)
from aiogram.enums import ParseMode
from aiogram.utils.keyboard import InlineKeyboardBuilder
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.date import DateTrigger

API_TOKEN = "8558976967:AAFnChpNZ6TBoXOai-5OAilw0Mc1Dv_a7Go"

logging.basicConfig(level=logging.INFO)

from aiogram.client.default import DefaultBotProperties

bot = Bot(
    token=API_TOKEN,
    default=DefaultBotProperties(parse_mode=ParseMode.HTML)
)
dp = Dispatcher()
scheduler = AsyncIOScheduler()

# -----------------------------
# -----------------------------
# Database (PostgreSQL, SQLAlchemy async)
# -----------------------------
from sqlalchemy import (
    Column, Integer, BigInteger, String, Text, Date, DateTime, Boolean,
    ForeignKey, Enum
)
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import declarative_base, relationship, sessionmaker
from sqlalchemy.sql import func

DATABASE_URL = "postgresql+asyncpg://tguser:1@localhost:5432/tgminiapp"

engine = create_async_engine(DATABASE_URL, echo=False)
AsyncSessionLocal = sessionmaker(
    engine, expire_on_commit=False, class_=AsyncSession
)

Base = declarative_base()


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    telegram_id = Column(BigInteger, unique=True, nullable=False)
    name = Column(String(255))
    birthday = Column(Date)
    created_at = Column(DateTime, server_default=func.now())

    notification_settings = relationship("NotificationSettings", back_populates="user", uselist=False)


class NotificationSettings(Base):
    __tablename__ = "notification_settings"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True)
    birthday_reminders = Column(Boolean, default=True)
    new_followers = Column(Boolean, default=True)
    post_birthday = Column(Boolean, default=True)
    wishlist_requests = Column(Boolean, default=True)

    user = relationship("User", back_populates="notification_settings")


async def get_session():
    async with AsyncSessionLocal() as session:
        yield session


# -----------------------------
# Utils
# -----------------------------
# -----------------------------

def mini_app_link(profile_id: str) -> str:
    return f"https://t.me/your_bot/miniapp?profile={profile_id}"


def retry_intervals():
    return [5, 15, 30]


async def send_with_retry(chat_id: int, text: str, keyboard=None):
    for attempt, delay in enumerate([0] + retry_intervals()):
        try:
            if delay:
                await asyncio.sleep(delay * 60)
            await bot.send_message(chat_id, text, reply_markup=keyboard)
            return
        except Exception as e:
            logging.error(f"Send failed (attempt {attempt}): {e}")


# -----------------------------
# Notification builders
# -----------------------------

def birthday_text(sub, days: int) -> str:
    if days == 7:
        prefix = "Через неделю"
    elif days == 1:
        prefix = "Завтра"
    else:
        prefix = "Сегодня"

    return (
        f"{prefix} день рождения у "
        f"<a href='{sub.profile_url}'>{sub.name}</a>! 🎉"
    )


# -----------------------------
# Schedulers
# -----------------------------

async def schedule_birthday_notifications(chat_id: int, sub):
    for days in [7, 1, 0]:
        notify_time = (
            sub.birthday - timedelta(days=days)
        ).replace(hour=10, minute=0, second=0)

        scheduler.add_job(
            send_with_retry,
            trigger=DateTrigger(run_date=notify_time),
            args=[chat_id, birthday_text(sub, days)],
        )


# -----------------------------
# Recommendation system (stub)
# -----------------------------

async def generate_recommendations(user_id: int, friend_name: str) -> str:
    # Placeholder logic
    gifts = [
        ("Смарт-аксессуар", "Полезный гаджет для повседневной жизни", "https://example.com/1"),
        ("Настольная игра", "Для вечеров с друзьями", "https://example.com/2"),
        ("Подарочный сертификат", "Универсальный вариант", "https://example.com/3"),
        ("Книга", "Популярный бестселлер", "https://example.com/4"),
        ("Хобби-набор", "Для новых впечатлений", "https://example.com/5"),
    ]

    text = f"🎁 <b>Подборка для {friend_name}:</b>\n"
    for i, g in enumerate(gifts, 1):
        text += f"{i}. <b>{g[0]}</b> — {g[1]}\n{g[2]}\n"

    return text[:2000]


# -----------------------------
# Handlers
# -----------------------------

@dp.message(F.text == "/start")
async def start(message: Message):
    await message.answer(
        "Бот уведомлений и рекомендаций активирован. "
        "Основной функционал работает в связке с мини-приложением."
    )


@dp.message(F.text == "Что подарить")
async def what_to_gift(message: Message):
    await message.answer("📨 Отправили вам подборку в личные сообщения")
    text = await generate_recommendations(message.from_user.id, "Друг")

    kb = InlineKeyboardBuilder()
    kb.button(text="🔄 Обновить подборку", callback_data="refresh_reco")

    await send_with_retry(message.chat.id, text, kb.as_markup())


@dp.callback_query(F.data == "refresh_reco")
async def refresh_reco(callback: CallbackQuery):
    text = await generate_recommendations(callback.from_user.id, "Друг")
    await callback.message.edit_text(text)
    await callback.answer()


# -----------------------------
# Startup
# -----------------------------

async def main():
    scheduler.start()
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
