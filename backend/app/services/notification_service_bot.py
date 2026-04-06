import os
import logging
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.user import User
from app.models.notification_settings import NotificationSettings
from app.core.bot_setup import bot
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram import types

logger = logging.getLogger(__name__)

class NotificationService:
    def __init__(self):
        self.bot = bot
        self.web_app_url = os.getenv("WEB_APP_URL", "https://wishlistprice.ru/app")

    async def _get_tg_id(self, session: AsyncSession, user_id: int):
        stmt = select(User.telegram_id).where(User.id == user_id)
        result = await session.execute(stmt)
        return result.scalar()

    async def _can_notify(self, session: AsyncSession, user_id: int, setting_field: str) -> bool:
        """Проверка настроек пользователя FS-10.2"""
        stmt = select(NotificationSettings).where(NotificationSettings.user_id == user_id)
        res = await session.execute(stmt)
        settings = res.scalar_one_or_none()
        if not settings: return True
        return getattr(settings, setting_field, True)

    async def notify_new_subscriber(self, session: AsyncSession, owner_id: int, subscriber_id: int, subscriber_name: str):
        """FS-10.1.2 Новый подписчик"""
        if not await self._can_notify(session, owner_id, "new_followers"): return
        
        tg_id = await self._get_tg_id(session, owner_id)
        if tg_id:
            link = f'<a href="{self.web_app_url}?user_id={subscriber_id}">{subscriber_name}</a>'
            await self.bot.send_message(tg_id, f"👤 У вас новый подписчик: {link}")

    async def send_access_request(self, session: AsyncSession, owner_id: int, requester_name: str, wishlist_name: str, request_id: int, requester_id: int):
        """FS-10.1.4 Заявка на доступ"""
        # Заявки на доступ обычно не отключаются, но можно добавить проверку access_requests
        tg_id = await self._get_tg_id(session, owner_id)
        if tg_id:
            builder = InlineKeyboardBuilder()
            builder.row(
                types.InlineKeyboardButton(text="✅ Одобрить", callback_data=f"approve_{request_id}"),
                types.InlineKeyboardButton(text="❌ Отклонить", callback_data=f"reject_{request_id}")
            )
            builder.row(types.InlineKeyboardButton(text="👁 Профиль", url=f"{self.web_app_url}?user_id={requester_id}"))
            
            text = f'🔑 Пользователь <b>{requester_name}</b> просит доступ к вишлисту <b>"{wishlist_name}"</b>.'
            await self.bot.send_message(tg_id, text, reply_markup=builder.as_markup())

    async def notify_birthday(self, session: AsyncSession, user_id: int, friend_name: str, friend_id: int, msg_type: str):
        """FS-10.1.1 Напоминания о ДР"""
        if not await self._can_notify(session, user_id, "birt_before"): return
        
        tg_id = await self._get_tg_id(session, user_id)
        if tg_id:
            link = f'<a href="{self.web_app_url}?user_id={friend_id}">{friend_name}</a>'
            messages = {
                "7_days": f"⏳ Через неделю день рождения у {link}! Не забудь поздравить!",
                "1_day": f"🎈 Завтра день рождения у {link}! Почти пора!",
                "today": f"🥳 Сегодня день рождения у {link}! Поздравляем!"
            }
            await self.bot.send_message(tg_id, messages.get(msg_type, f"ДР у {link}"))
