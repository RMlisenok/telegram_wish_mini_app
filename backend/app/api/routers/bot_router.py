import logging
from aiogram import Router, types, F
from aiogram.filters import CommandStart
from sqlalchemy import select
from app.core.db import AsyncSessionLocal
from app.models.user import User
from app.models.notification_settings import NotificationSettings
from app.services.access_request_service import AccessRequestService
from app.schemas.access_request import UpdateAccessRequest, AccessRequestStatus

logger = logging.getLogger(__name__)
router = Router()

@router.message(CommandStart())
async def cmd_start(message: types.Message):
    async with AsyncSessionLocal() as session:
        try:
            # Регистрация пользователя
            user_stmt = select(User).where(User.telegram_id == message.from_user.id)
            user = (await session.execute(user_stmt)).scalar_one_or_none()
            
            if not user:
                user = User(
                    telegram_id=message.from_user.id,
                    name=message.from_user.first_name or f"User_{message.from_user.id}"
                )
                session.add(user)
                await session.flush()
                
                # Создаем настройки по умолчанию
                new_settings = NotificationSettings(user_id=user.id)
                session.add(new_settings)
            
            await session.commit()
            await message.answer(f"Привет, {message.from_user.first_name}! Профиль настроен. Используйте Mini App для управления вишлистами.")
        except Exception as e:
            logger.error(f"Error start: {e}")
            await message.answer("Ошибка при регистрации.")

@router.callback_query(F.data.startswith("approve_"))
async def handle_approve(callback: types.CallbackQuery):
    request_id = int(callback.data.split("_")[1])
    async with AsyncSessionLocal() as session:
        service = AccessRequestService(session)
        # Находим владельца по TG ID, чтобы сервис проверил права
        res = await session.execute(select(User.id).where(User.telegram_id == callback.from_user.id))
        owner_id = res.scalar()
        
        try:
            await service.update_request_status(request_id, UpdateAccessRequest(status=AccessRequestStatus.APPROVED), owner_id)
            await session.commit()
            await callback.message.edit_text(callback.message.text + "\n\n✅ <b>Одобрено</b>")
        except Exception as e:
            await callback.answer(f"Ошибка: {e}", show_alert=True)

@router.callback_query(F.data.startswith("reject_"))
async def handle_reject(callback: types.CallbackQuery):
    # Аналогично для отклонения
    await callback.message.edit_text(callback.message.text + "\n\n❌ <b>Отклонено</b>")
    await callback.answer()