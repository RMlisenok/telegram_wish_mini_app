import logging
from aiogram import Router, types, F
from aiogram.filters import CommandStart, Command
from sqlalchemy import select
from app.core.db import AsyncSessionLocal
from app.models.notification_settings import NotificationSettings
from app.models.user import User
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.db import get_db
from app.services.notification_service_bot import NotificationService
from app.core.bot_setup import bot
from app.services.access_request_service import AccessRequestService
from app.schemas.access_request import UpdateAccessRequest, AccessRequestStatus


logger = logging.getLogger(__name__)
router = Router()

WEB_APP_URL = os.getenv("WEB_APP_URL")

@router.message(CommandStart())
async def cmd_start(message: types.Message):
    logger.info(f"Получена команда /start от {message.from_user.id}")

    async with AsyncSessionLocal() as session:
        try:
            user_stmt = select(User).where(User.telegram_id == message.from_user.id)
            user_result = await session.execute(user_stmt)
            user = user_result.scalar_one_or_none()

            if not user:
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
                new_settings = NotificationSettings(
                    user_id=user.id,
                    new_followers=True,
                    access_requests=True,
                    birt_after=False,
                    birt_before=True
                )
                session.add(new_settings)

            await session.commit()
        except Exception as e:
            await session.rollback()
            logger.error(f"Ошибка в БД: {e}")
            await message.answer("Ошибка базы данных. Попробуйте позже.")
            return

    web_app_url = "https://wishlistprice.ru/app"
    await message.answer(
        f"Привет, {message.from_user.first_name}! 🎁\n\n"
        "Я буду присылать тебе уведомления о праздниках друзей и помогать с выбором подарков.",
        reply_markup=types.InlineKeyboardMarkup(inline_keyboard=[
            [types.InlineKeyboardButton(text="🎁 Открыть вишлист", web_app=types.WebAppInfo(url=web_app_url))],
            [types.InlineKeyboardButton(text="ℹ️ Помощь", callback_data="help_info")]
        ])
    )

@router.callback_query(F.data == "help_info")
async def handle_help(callback: types.CallbackQuery):
    help_text = (
        "✨ <b>Как пользоваться ботом:</b>\n\n"
        "• <b>Вишлист:</b> Нажми кнопку ниже, чтобы добавить свои желания.\n"
        "• <b>Друзья:</b> Подписывайся на друзей, чтобы видеть их списки.\n"
        "• <b>Подарки:</b> Выбирай подарок из списка друга и бронируй его, чтобы не подарить одинаковое.\n"
        "• <b>Рекомендации:</b> Я сам предложу идеи подарков на основе анкет!"
    )
    await callback.message.answer(help_text, parse_mode="HTML")
    await callback.answer()

# Обработка заявок на доступ (FS-10.1.4)
@router.callback_query(F.data.startswith("access_"))
async def handle_access_request(callback: types.CallbackQuery):
    action, target_id = callback.data.split("_")[1], callback.data.split("_")[2]

    if action == "approve":
        await callback.message.edit_text("✅ Вы одобрили доступ к вишлисту!")
        await callback.bot.send_message(target_id, "Владелец одобрил ваш доступ! 🎉")
    else:
        await callback.message.edit_text("❌ Заявка отклонена.")
        await callback.bot.send_message(target_id, "К сожалению, доступ отклонен.")
    await callback.answer()


# Команда для тестов рекомендаций локально (FS-10.3)
@router.message(Command("test_rec"))
async def test_rec_cmd(message: types.Message):
    await message.answer("🧪 Генерация рекомендаций...")
    from app.services.recommendations_service import RecommendationService
    from app.core.bot_setup import bot
    await RecommendationService.generate_and_send_via_bot(
        db_factory=AsyncSessionLocal,
        requester_id=message.from_user.id,
        target_id=message.from_user.id,
        bot=bot
    )


@router.callback_query(F.data.startswith("refresh_rec_"))
async def refresh_recommendations(callback: types.CallbackQuery, bot: "Bot"):  # Добавь кавычки!
    from app.services.recommendations_service import RecommendationService
    from app.core.db import AsyncSessionLocal

    target_id = int(callback.data.split("_")[-1])

    await RecommendationService.generate_and_send_via_bot(
        db_factory=AsyncSessionLocal,
        requester_id=callback.from_user.id,
        target_id=target_id,
        bot=bot
    )
    await callback.answer()


# Хендлер для одобрения заявки
@router.callback_query(F.data.startswith("approve_"))
async def approve_request_callback(callback: types.CallbackQuery):
    request_id = int(callback.data.split("_")[1])

    async with AsyncSessionLocal() as session:
        service = AccessRequestService(session)
        try:
            update_data = UpdateAccessRequest(status=AccessRequestStatus.APPROVED)
            # callback.from_user.id — это telegram_id владельца, нам нужно найти его внутренний user_id
            from app.repositories.user_repository import UserRepository
            user_repo = UserRepository(session)
            owner = await user_repo.get_user_by_tg_id(callback.from_user.id)

            if not owner:
                await callback.answer("Ошибка: пользователь не найден", show_alert=True)
                return

            await service.update_request_status(request_id, update_data, owner.id)
            await session.commit()

            await callback.message.edit_text(
                text=callback.message.text + "\n\n✅ <b>Одобрено</b>",
                parse_mode="HTML"
            )
            await callback.answer("Доступ одобрен!")

        except Exception as e:
            await session.rollback()
            await callback.answer(f"Ошибка: {str(e)}", show_alert=True)


# Хендлер для отклонения заявки
@router.callback_query(F.data.startswith("reject_"))
async def reject_request_callback(callback: types.CallbackQuery):
    request_id = int(callback.data.split("_")[1])

    async with AsyncSessionLocal() as session:
        service = AccessRequestService(session)
        try:
            update_data = UpdateAccessRequest(status=AccessRequestStatus.REJECTED)

            from app.repositories.user_repository import UserRepository
            user_repo = UserRepository(session)
            owner = await user_repo.get_user_by_tg_id(callback.from_user.id)

            if not owner:
                await callback.answer("Ошибка: пользователь не найден", show_alert=True)
                return

            await service.update_request_status(request_id, update_data, owner.id)
            await session.commit()

            await callback.message.edit_text(
                text=callback.message.text + "\n\n❌ <b>Отклонено</b>",
                parse_mode="HTML"
            )
            await callback.answer("Заявка отклонена")

        except Exception as e:
            await session.rollback()
            await callback.answer(f"Ошибка: {str(e)}", show_alert=True)
