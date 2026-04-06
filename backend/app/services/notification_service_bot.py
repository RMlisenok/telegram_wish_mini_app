import os
import logging
from datetime import date, timedelta
from sqlalchemy import select, extract
from sqlalchemy.ext.asyncio import AsyncSession

from aiogram import types, html
from aiogram.utils.keyboard import InlineKeyboardBuilder

from app.models.user import User
from app.models.notification_settings import NotificationSettings
from app.models.subscription import Subscription
from app.core.bot_setup import bot

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
        if not settings: 
            return True  # По умолчанию уведомления включены
        return getattr(settings, setting_field, True)

    def _get_link(self, user_id: int, name: str):
        """Создает безопасную HTML ссылку на профиль пользователя"""
        safe_name = html.quote(name)
        return f'<a href="{self.web_app_url}?user_id={user_id}">{safe_name}</a>'

    # --- Метод-оркестратор для проверки ДР ---
    
    async def check_birthdays_and_notify(self, session: AsyncSession):
        """
        Проверяет ДР на сегодня, завтра и через 7 дней.
        Находит подписчиков именинников и отправляет им уведомления.
        """
        today = date.today()
        
        # Конфигурация: через сколько дней уведомлять и какой тип сообщения слать
        notification_targets = {
            0: "today",
            1: "1_day",
            7: "7_days"
        }

        for days_delta, msg_type in notification_targets.items():
            target_date = today + timedelta(days=days_delta)
            
            # 1. Ищем всех именинников на целевую дату (сравнение по дню и месяцу)
            stmt = select(User).where(
                extract('month', User.birth_date) == target_date.month,
                extract('day', User.birth_date) == target_date.day
            )
            res = await session.execute(stmt)
            birthday_users = res.scalars().all()

            for b_user in birthday_users:
                # 2. Ищем всех подписчиков (type_sub=True означает подписку на профиль)
                sub_stmt = select(Subscription).where(
                    Subscription.target_user_id == b_user.id,
                    Subscription.type_sub == True
                )
                sub_res = await session.execute(sub_stmt)
                subscribers = sub_res.scalars().all()

                for sub in subscribers:
                    try:
                        # 3. Вызываем метод отправки для каждого подписчика
                        await self.notify_birthday(
                            session=session,
                            user_id=sub.subscriber_id,
                            friend_id=b_user.id,
                            friend_name=b_user.name,
                            msg_type=msg_type
                        )
                    except Exception as e:
                        logger.error(f"Ошибка при уведомлении о ДР для пользователя {sub.subscriber_id}: {e}")

    # --- Конкретные типы уведомлений ---

    # FS-10.1.1 Напоминания о ДР друзей
    async def notify_birthday(self, session: AsyncSession, user_id: int, friend_id: int, friend_name: str, msg_type: str):
        if not await self._can_notify(session, user_id, "birt_before"): 
            return
        
        user = await self._get_user_info(session, user_id)
        if not user or not user.telegram_id: 
            return

        link = self._get_link(friend_id, friend_name)
        messages = {
            "7_days": f"⏳ Через неделю день рождения у {link}! Не забудь поздравить!",
            "1_day": f"🎈 Завтра день рождения у {link}! Почти пора!",
            "today": f"🥳 Сегодня день рождения у {link}! Поздравляем!"
        }
        
        text = messages.get(msg_type, f"Скоро день рождения у {link}")
        await self.bot.send_message(user.telegram_id, text, parse_mode="HTML")

    # FS-10.1.2 Новый подписчик
    async def notify_new_subscriber(self, session: AsyncSession, owner_id: int, subscriber_id: int, subscriber_name: str):
        if not await self._can_notify(session, owner_id, "new_followers"): 
            return
        
        owner = await self._get_user_info(session, owner_id)
        if owner and owner.telegram_id:
            link = self._get_link(subscriber_id, subscriber_name)
            await self.bot.send_message(
                owner.telegram_id, 
                f"👤 У вас новый подписчик: {link}", 
                parse_mode="HTML"
            )

    # FS-10.1.3 Пост-ДР (Архивация подарков)
    async def notify_post_birthday(self, session: AsyncSession, user_id: int):
        if not await self._can_notify(session, user_id, "post_birt_action"): 
            return
        
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
        if not await self._can_notify(session, owner_id, "access_requests"): 
            return
        
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