import datetime
from sqlalchemy import select, extract
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.user import User
from app.models.notification_settings import NotificationSettings
from app.models.subscription import Subscription
from aiogram import types
from aiogram.utils.keyboard import InlineKeyboardBuilder


class NotificationService:
    def __init__(self, bot):
        self.bot = bot

    async def check_birthdays_and_notify(self, session: AsyncSession):
        today = datetime.date.today()
        intervals = [0, 1, 7]

        for interval in intervals:
            target_date = today + datetime.timedelta(days=interval)

            # Ищем пользователей, у которых ДР в целевую дату
            stmt = select(User).where(
                extract('month', User.birth_date) == target_date.month,
                extract('day', User.birth_date) == target_date.day
            )
            result = await session.execute(stmt)
            birthday_users = result.scalars().all()

            for b_user in birthday_users:
                sub_stmt = select(User).join(Subscription, Subscription.follower_id == User.id).where(
                    Subscription.target_id == b_user.id
                )
                sub_result = await session.execute(sub_stmt)
                followers = sub_result.scalars().all()

                for follower in followers:
                    set_stmt = select(NotificationSettings).where(NotificationSettings.user_id == follower.id)
                    res_set = await session.execute(set_stmt)
                    settings = res_set.scalars().first()

                    if settings and settings.birt_before:
                        text = self._format_birthday_text(b_user.full_name, interval)
                        try:
                            await self.bot.send_message(follower.telegram_id, text, parse_mode="HTML")
                        except Exception as e:
                            print(f"Ошибка отправки: {e}")

    def _format_birthday_text(self, name, days_left):
        link = f"<b>{name}</b>" # ДОБАВИТЬ ССЫЛКУ НА ЧЕЛОВЕЧКА
        if days_left == 7:
            return f"Через неделю день рождения у {link}! Не забудь поздравить!"
        elif days_left == 1:
            return f"Завтра день рождения у {link}! Не забудь поздравить!"
        else:
            return f"Сегодня день рождения у {link}! 🎉"

    async def notify_new_follower(self, session: AsyncSession, follower_id: int, target_id: int):
        stmt = select(User).where(User.id == follower_id)
        follower = (await session.execute(stmt)).scalar()

        settings_stmt = select(NotificationSettings).where(NotificationSettings.user_id == target_id)
        settings = (await session.execute(settings_stmt)).scalar()

        if settings and settings.new_followers and follower:
            link = f'<a href="https://t.me/your_bot/app?startapp=user_{follower.id}">{follower.full_name}</a>'
            text = f"👤 У вас новый подписчик: {link}"

            target_stmt = select(User).where(User.id == target_id)
            target = (await session.execute(target_stmt)).scalar()

            if target and target.telegram_id:
                await self.bot.send_message(target.telegram_id, text, parse_mode="HTML")

    async def notify_access_request(self, session: AsyncSession, requester_id: int, owner_id: int, wishlist_name: str,
                                    request_id: int):
        settings_stmt = select(NotificationSettings).where(NotificationSettings.user_id == owner_id)
        settings = (await session.execute(settings_stmt)).scalar()

        if settings and settings.access_requests:
            requester_stmt = select(User).where(User.id == requester_id)
            requester = (await session.execute(requester_stmt)).scalar()

            owner_stmt = select(User).where(User.id == owner_id)
            owner = (await session.execute(owner_stmt)).scalar()

            if requester and owner:
                text = (f"📩 Пользователь {requester.full_name} отправил заявку на доступ "
                        f"к вашему вишлисту \"{wishlist_name}\"")

                builder = InlineKeyboardBuilder()
                builder.row(
                    types.InlineKeyboardButton(text="✅ Одобрить", callback_data=f"approve_{request_id}"),
                    types.InlineKeyboardButton(text="❌ Отклонить", callback_data=f"reject_{request_id}")
                )
                builder.row(
                    types.InlineKeyboardButton(text="👀 Посмотреть профиль",
                                               url=f"https://t.me/your_bot/app?startapp=user_{requester.id}")
                )

                await self.bot.send_message(owner.telegram_id, text, reply_markup=builder.as_markup())

    async def check_post_birthday(self, session: AsyncSession):
        yesterday = datetime.date.today() - datetime.timedelta(days=1)

        stmt = select(User).where(
            extract('month', User.birth_date) == yesterday.month,
            extract('day', User.birth_date) == yesterday.day
        )
        birthday_people = (await session.execute(stmt)).scalars().all()

        for person in birthday_people:
            set_stmt = select(NotificationSettings).where(NotificationSettings.user_id == person.id)
            settings = (await session.execute(set_stmt)).scalar()

            if settings and settings.birt_after:
                text = "🎁 У вас были забронированы желания. Хотите переместить их в исполненные?"
                builder = InlineKeyboardBuilder()
                builder.row(
                    types.InlineKeyboardButton(text="✅ Переместить", callback_data="move_to_executed"),
                    types.InlineKeyboardButton(text="❌ Не перемещать", callback_data="keep_as_is")
                )
                await self.bot.send_message(person.telegram_id, text, reply_markup=builder.as_markup())
