import datetime
from sqlalchemy import select, extract
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.user import User
from app.models.notification_settings import NotificationSettings
from app.models.subscription import Subscription
from aiogram import types
from aiogram.utils.keyboard import InlineKeyboardBuilder
from typing import Optional, List, Tuple
from app.repositories.notification_settings_repository import NotificationSettingsRepository
from app.schemas.notification_settings import (
    NotificationSettingsResponse,
    NotificationSettingsUpdate
)


class NotificationSettingsService:
    def __init__(self, session: AsyncSession):
        self.rep_settings = NotificationSettingsRepository(session)

    async def get_user_notification(
        self,
        user_id: int
    ) -> NotificationSettingsResponse:
        settings = await self.rep_settings.get_user_settings(user_id)
        if not settings:
            create_settings = await self.rep_settings.create_notification_settings(user_id)
            return NotificationSettingsResponse.model_validate(create_settings)
        return NotificationSettingsResponse.model_validate(settings)

    async def update_notification(
        self,
        data: NotificationSettingsUpdate,
        user_id: int
    ) -> Optional[NotificationSettingsUpdate]:
        update_data = await self.rep_settings.update_settings(data, user_id)
        if update_data:
            return NotificationSettingsResponse.model_validate(update_data)
        return None
