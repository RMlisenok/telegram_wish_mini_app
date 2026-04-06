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

    async def _get_user_info(self, session: AsyncSession, user_id: int):
        stmt = select(User).where(User.id == user_id)
        res = await session.execute(stmt)
        return res.scalar_one_or_none()

    async def _can_notify(self, session: AsyncSession, user_id: int, setting_field: str) -> bool:
        """Проверка настроек пользователя FS-10.2"""
        stmt = select(NotificationSettings).where(NotificationSettings.user_id == user_id)
        res = await session.execute(stmt)
        settings = res.scalar_one_or_none()
        if not settings: return True  # По умолчанию включено
        return getattr(settings, setting_field, True)

    def _get_link(self, user_id: int, name: str):
        return f'<a href="{self.web_app_url}?user_id={user_id}">{name}</a>'

    # FS-10.1.1 Напоминания о ДР друзей
    async def notify_birthday(self, session: AsyncSession, user_id: int, friend_id: int, friend_name: str, msg_type: str):
        if not await self._can_notify(session, user_id, "birt_before"): return
        
        user = await self._get_user_info(session, user_id)
        if not user or not user.telegram_id: return

        link = self._get_link(friend_id, friend_name)
        messages = {
            "7_days": f"⏳ Через неделю день рождения у {link}! Не забудь поздравить!",
            "1_day": f"🎈 Завтра день рождения у {link}! Почти пора!",
            "today": f"🥳 Сегодня день рождения у {link}! Поздравляем!"
        }
        await self.bot.send_message(user.telegram_id, messages.get(msg_type, f"ДР у {link}"), parse_mode="HTML")

    # FS-10.1.2 Новый подписчик
    async def notify_new_subscriber(self, session: AsyncSession, owner_id: int, subscriber_id: int, subscriber_name: str):
        if not await self._can_notify(session, owner_id, "new_followers"): return
        
        owner = await self._get_user_info(session, owner_id)
        if owner and owner.telegram_id:
            link = self._get_link(subscriber_id, subscriber_name)
            await self.bot.send_message(owner.telegram_id, f"👤 У вас новый подписчик: {link}", parse_mode="HTML")

    # FS-10.1.3 Пост-ДР (Архивация подарков)
    async def notify_post_birthday(self, session: AsyncSession, user_id: int):
        if not await self._can_notify(session, user_id, "post_birt_action"): return
        
        user = await self._get_user_info(session, user_id)
        if user and user.telegram_id:
            builder = InlineKeyboardBuilder()
            builder.row(
                types.InlineKeyboardButton(text="✅ Переместить", callback_data="archive_gifts_yes"),
                types.InlineKeyboardButton(text="❌ Не перемещать", callback_data="archive_gifts_no")
            )
            text = "🎂 Надеемся, день рождения прошел отлично! Хотите переместить забронированные подарки в «исполненные»?"
            await self.bot.send_message(user.telegram_id, text, reply_markup=builder.as_markup())

    # FS-10.1.4 Заявка на доступ
    async def send_access_request(self, session: AsyncSession, owner_id: int, requester_id: int, requester_name: str, wishlist_name: str, request_id: int):
        if not await self._can_notify(session, owner_id, "access_requests"): return
        
        owner = await self._get_user_info(session, owner_id)
        if owner and owner.telegram_id:
            builder = InlineKeyboardBuilder()
            builder.row(
                types.InlineKeyboardButton(text="✅ Одобрить", callback_data=f"approve_{request_id}"),
                types.InlineKeyboardButton(text="❌ Отклонить", callback_data=f"reject_{request_id}")
            )
            builder.row(types.InlineKeyboardButton(text="👁 Профиль", url=f"{self.web_app_url}?user_id={requester_id}"))
            
            link = self._get_link(requester_id, requester_name)
            text = f'🔑 Пользователь {link} просит доступ к вашему вишлисту <b>"{wishlist_name}"</b>.'
            await self.bot.send_message(owner.telegram_id, text, reply_markup=builder.as_markup(), parse_mode="HTML")