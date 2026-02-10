import logging
from aiogram import Router, types
from aiogram.filters import CommandStart
from sqlalchemy import select
from app.core.db import AsyncSessionLocal
from app.models.settings import NotificationSettings
from app.models.user import User

logger = logging.getLogger(__name__)
router = Router()


@router.message(CommandStart())
async def cmd_start(message: types.Message):
    logger.info(f"Получена команда /start от {message.from_user.id}")

    async with AsyncSessionLocal() as session:
        try:
            user_stmt = select(User).where(User.telegram_id == message.from_user.id)
            user_result = await session.execute(user_stmt)
            user = user_result.scalar_one_or_none()

            if not user:
                logger.info(f"Создаем новую запись в users для TG ID: {message.from_user.id}")
                user = User(
                    telegram_id=message.from_user.id,
                    name=message.from_user.first_name or f"User_{message.from_user.id}",
                    show_sub=False
                )
                session.add(user)
                await session.flush()

            set_stmt = select(NotificationSettings).where(NotificationSettings.user_id == user.id)
            set_result = await session.execute(set_stmt)
            settings = set_result.scalar_one_or_none()

            if not settings:
                logger.info(f"Создаем настройки для системного ID: {user.id}")
                new_settings = NotificationSettings(
                    user_id=user.id,
                    new_followers=True,
                    access_requests=True,
                    birt_after=False,
                    birt_before=True
                )
                session.add(new_settings)

            await session.commit()
            logger.info(f"Успешный COMMIT для TG ID: {message.from_user.id}")

        except Exception as e:
            await session.rollback()
            logger.error(f"Ошибка в БД при /start: {e}")
            await message.answer("Произошла ошибка при регистрации. Пожалуйста, попробуйте позже.")
            return

    web_app_url = "https://wishlistprice.ru/app"
    await message.answer(
        f"Привет, {message.from_user.first_name}! 🎁\n\n"
        "Ваш профиль и настройки уведомлений настроены.",
        reply_markup=types.InlineKeyboardMarkup(inline_keyboard=[
            [types.InlineKeyboardButton(text="Открыть вишлист", web_app=types.WebAppInfo(url=web_app_url))]
        ])
    )