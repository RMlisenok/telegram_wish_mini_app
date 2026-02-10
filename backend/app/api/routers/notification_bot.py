from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.db import get_db
from app.services.notification_service_bot import NotificationService
from app.core.bot_setup import bot
from datetime import date, timedelta
from app.models.user import User
from app.models.subscription import Subscription
from app.core.dependencies import get_current_user_id
from sqlalchemy import select

router = APIRouter(tags=["Notifications"])

@router.post("/setup-test-birthday-data")
async def setup_test_data(current_user_id: int = Depends(get_current_user_id), db: AsyncSession = Depends(get_db)):
    test_birthday_user = User(
        name="Тестовый Именинник",
        telegram_id=12345678, # Любое число
        birth_date=date.today() + timedelta(days=7),
        show_sub=True
    )
    db.add(test_birthday_user)
    await db.flush()

    new_sub = Subscription(
        subscriber_id=current_user_id,
        target_user_id=test_birthday_user.id,
        type_sub=True
    )
    db.add(new_sub)

    stmt = select(NotificationSettings).where(NotificationSettings.user_id == current_user_id)
    settings = (await db.execute(stmt)).scalar()
    if settings:
        settings.birt_before = True
    else:
        db.add(NotificationSettings(user_id=current_user_id, birt_before=True))

    await db.commit()
    return {"message": f"User {test_birthday_user.id} created with birthday in 7 days. Subscription added."}



@router.post("/test-birthday-notifications")
async def test_birthdays(db: AsyncSession = Depends(get_db)):
    service = NotificationService(bot)
    await service.check_birthdays_and_notify(db)
    return {"status": "Birthday check completed"}