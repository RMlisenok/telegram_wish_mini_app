from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from app.services.notification_service import NotificationService
from app.core.db import AsyncSessionLocal


def setup_scheduler(bot):
    scheduler = AsyncIOScheduler()
    notification_service = NotificationService(bot)

    scheduler.add_job(
        run_daily_notifications,
        CronTrigger(hour=10, minute=0),
        args=[notification_service],
        id="daily_birthday_check"
    )

    scheduler.start()


async def run_daily_notifications(service: NotificationService):
    async with AsyncSessionLocal() as session:
        try:
            await service.check_birthdays_and_notify(session)
            await session.commit()
        except Exception as e:
            await session.rollback()
            print(f"Ошибка в планировщике: {e}")
        finally:
            await session.close()