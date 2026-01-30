from typing import Optional, List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, func, desc, asc, and_
from app.models.notification_settings import NotificationSettings
from app.schemas.notification_settings import NotificationSettingsUpdate

class NotificationSettingsRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_notification_settings(
        self,
        user_id: int
    ) -> NotificationSettings:
        settings = NotificationSettings(
            user_id=user_id,
            new_followers=True,
            access_requests=True,
            birt_after=False,
            birt_before=True
        )
        self.session.add(settings)
        await self.session.commit()
        await self.session.refresh(settings)
        return settings

    async def get_user_settings(
        self,
        user_id: int
    ) -> Optional[NotificationSettings]:
        query = (
            select(NotificationSettings)
            .where(NotificationSettings.user_id == user_id)
        )
        result = await self.session.execute(query)
        return result.scalar_one_or_none()

    async def update_settings(
        self,
        data: NotificationSettingsUpdate,
        user_id: int
    ) -> Optional[NotificationSettings]:
        update_data = data.model_dump(exclude_unset=True)

        if not update_data:
            return await self.get_user_settings(user_id)

        stmt = (
            update(NotificationSettings)
            .where(NotificationSettings.user_id == user_id)
            .values(**update_data)
            .returning(NotificationSettings)
        )

        result = await self.session.execute(stmt)
        await self.session.commit()
        settings = result.scalar_one_or_none()
        if settings:
            await self.session.refresh(settings)
        return settings
