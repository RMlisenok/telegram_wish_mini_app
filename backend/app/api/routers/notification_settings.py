from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.core.db import get_db
from app.core.dependencies import get_current_user_id
from app.models.notification_settings import NotificationSettings
from app.schemas.notification_settings import (
    NotificationSettingsResponse,
    NotificationSettingsUpdate
)
from app.services.notification_settings_service import (
    NotificationSettingsService
)

router = APIRouter(prefix="/settings", tags=["Settings"])


@router.get("/notifications", response_model=NotificationSettingsResponse)
async def get_settings(
    db: AsyncSession = Depends(get_db),
    user_id: int = Depends(get_current_user_id)
):

    settings_service = NotificationSettingsService(db)
    settings = await settings_service.get_user_notification(user_id)
    return settings


@router.patch("/notifications")
async def update_notifications(
    data: NotificationSettingsUpdate,
    db: AsyncSession = Depends(get_db),
    user_id: int = Depends(get_current_user_id)
):
    settings_service = NotificationSettingsService(db)
    settings = await settings_service.get_user_notification(user_id)

    if not settings:
        raise HTTPException(status_code=404, detail="Settings not found")

    update_settings = await settings_service.update_notification(
        data,
        user_id
    )
    return {
        "status": "success",
        "update_data": update_settings
    }

    # settings.new_followers = data.get("new_followers", settings.new_followers)
    # settings.access_requests = data.get("access_requests", settings.access_requests)
    # settings.birt_after = data.get("birt_after", settings.birt_after)
    # settings.birt_before = data.get("birt_before", settings.birt_before)

    # await db.commit()
    # return {"status": "success"}