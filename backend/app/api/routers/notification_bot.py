from fastapi import APIRouter, Depends, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.db import get_db
from app.services.notification_service_bot import NotificationService

router = APIRouter(prefix="/notifications", tags=["Notifications"])
service = NotificationService()

@router.post("/test-birthday-check")
async def trigger_birthday_check(db: AsyncSession = Depends(get_db)):
    """Ручной триггер для проверки всех ДР (обычно вызывается планировщиком)"""
    # Тут должен быть вызов метода обхода базы, который мы писали ранее
    await service.check_birthdays_and_notify(db)
    return {"status": "ok"}

@router.post("/post-birthday/{user_id}")
async def send_post_birthday(user_id: int, db: AsyncSession = Depends(get_db)):
    """Триггер для FS-10.1.3 (после дня рождения)"""
    await service.notify_post_birthday(db, user_id)
    return {"status": "notification_sent"}

@router.post("/new-subscriber")
async def new_sub_event(owner_id: int, subscriber_id: int, subscriber_name: str, db: AsyncSession = Depends(get_db)):
    """Вызывается из роутера подписок, когда кто-то подписался"""
    await service.notify_new_subscriber(db, owner_id, subscriber_id, subscriber_name)
    return {"status": "sent"}