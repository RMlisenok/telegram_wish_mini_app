from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.core.db import get_db
from app.core.dependencies import get_current_user_id
from app.models.settings import NotificationSettings
from app.schemas.settings import NotificationSettingsResponse, NotificationSettingsUpdate

router = APIRouter(prefix="/settings", tags=["Settings"])


@router.get("/notifications", response_model=NotificationSettingsResponse)
async def get_my_settings(
        db: AsyncSession = Depends(get_db),
        user_id: int = Depends(get_current_user_id)
):
    result = await db.execute(
        select(NotificationSettings).where(NotificationSettings.user_id == user_id)
    )
    settings = result.scalar_one_or_none()

    if not settings:
        # Если настроек нет (например, старый юзер), создаем их
        settings = NotificationSettings(user_id=user_id)
        db.add(settings)
        await db.commit()
        await db.refresh(settings)

    return settings


@router.patch("/notifications", response_model=NotificationSettingsResponse)
async def update_settings(
        data: NotificationSettingsUpdate,
        db: AsyncSession = Depends(get_db),
        user_id: int = Depends(get_current_user_id)
):
    result = await db.execute(
        select(NotificationSettings).where(NotificationSettings.user_id == user_id)
    )
    settings = result.scalar_one_or_none()

    if not settings:
        raise HTTPException(status_code=404, detail="Settings not found")

    # Обновляем только те поля, которые прислал фронтенд
    update_data = data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(settings, key, value)

    await db.commit()
    await db.refresh(settings)
    return settings