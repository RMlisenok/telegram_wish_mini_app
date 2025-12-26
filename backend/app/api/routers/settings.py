from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.core.db import get_db
from app.core.dependencies import get_current_user_id
from app.models.settings import NotificationSettings
from app.schemas.settings import NotificationSettingsResponse, NotificationSettingsUpdate

router = APIRouter(prefix="/settings", tags=["Настройки"])


@router.get("/notifications", response_model=NotificationSettingsResponse)
async def get_settings(
        db: AsyncSession = Depends(get_db),
        user_id: int = Depends(get_current_user_id)
):
    result = await db.execute(
        select(NotificationSettings).where(NotificationSettings.user_id == user_id)
    )
    settings = result.scalar_one_or_none()

    if not settings:
        settings = NotificationSettings(user_id=user_id)
        db.add(settings)
        await db.commit()
        await db.refresh(settings)

    return settings


@router.patch("/notifications", response_model=NotificationSettingsResponse)
async def update_settings(
        payload: NotificationSettingsUpdate,
        db: AsyncSession = Depends(get_db),
        user_id: int = Depends(get_current_user_id)
):
    result = await db.execute(
        select(NotificationSettings).where(NotificationSettings.user_id == user_id)
    )
    settings = result.scalar_one_or_none()

    if not settings:
        raise HTTPException(status_code=404, detail="Настройки не найдены")

    for key, value in payload.model_dump(exclude_unset=True).items():
        setattr(settings, key, value)

    await db.commit()
    await db.refresh(settings)
    return settings