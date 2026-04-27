from fastapi import FastAPI
from contextlib import asynccontextmanager
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from app.core.data_tags import init_tags
from app.api.routers.auth import router as auth_routers
from app.api.routers.user import router as user_routers
from app.api.routers.wish import router as wish_routers
from app.api.routers.wishlist import router as wishlist_routers
from app.api.routers.reservation import router as reservation_routers
from app.api.routers.subscription import router as subscription_routers
from app.api.routers.notification_settings import router as settings_routers
from app.api.routers.questionnaire import router as questionnaire_router
from app.api.routers.access_requests import router as access_router
from app.api.routers.s3_client import router as s3_router
from app.api.routers.recommendations import router as recommendation_router
from app.core.bot_setup import bot, dp
import asyncio
from app.core.init_gifts import init_gifts
from app.api.routers.notification_bot import router as notification_router
from app.api.routers.bot_router import router as bot_tg_router
import os


from app.services.notification_service_bot import NotificationService
from app.core.db import AsyncSessionLocal


# Функция, которую будет вызывать планировщик
async def scheduled_birthday_check():
    service = NotificationService()
    async with AsyncSessionLocal() as session:
        try:
            await service.check_birthdays_and_notify(session)
            await session.commit()
            print("✅ Плановая проверка завершена успешно")
        except Exception as e:
            print(f"❌ Ошибка в планировщике: {e}")


@asynccontextmanager
async def lifespan(app: FastAPI):
    e2e_mode = os.getenv("E2E_MODE") == "1"
    polling_task = None
    scheduler = None

    if not e2e_mode:
        # Инициализация данных
        await init_tags()
        await init_gifts()

        # Настройка планировщика
        scheduler = AsyncIOScheduler()
        # --- НАСТРОЙКА ВРЕМЕНИ ЗДЕСЬ ---
        # Вариант 1 (Для теста): запускать каждую минуту
        # scheduler.add_job(scheduled_birthday_check, "interval", minutes=1)

        # Вариант 2 (Для продакшена): запускать каждый день в 09:00 утра
        scheduler.add_job(scheduled_birthday_check, "cron", hour=23, minute=0)

        scheduler.start()

        # Настройка бота
        dp.include_router(bot_tg_router)
        polling_task = asyncio.create_task(dp.start_polling(bot))
        print("✅ Backend и Бот запущены")
    else:
        print("✅ Backend запущен в E2E_MODE без Telegram polling и внешних инициализаторов")

    yield

    # Завершение работы
    if scheduler:
        scheduler.shutdown()  # Останавливаем планировщик
    if polling_task:
        polling_task.cancel()
    await bot.session.close()
    print('Stop work and clean completed')


app = FastAPI(lifespan=lifespan)

# Роутеры
app.include_router(auth_routers, prefix='/v1')
app.include_router(user_routers, prefix='/v1')
app.include_router(wish_routers, prefix='/v1')
app.include_router(wishlist_routers, prefix='/v1')
app.include_router(reservation_routers, prefix='/v1')
app.include_router(subscription_routers, prefix='/v1')
app.include_router(settings_routers, prefix='/v1')
app.include_router(questionnaire_router, prefix="/v1")
app.include_router(access_router, prefix="/v1")
app.include_router(s3_router, prefix="/v1")
app.include_router(recommendation_router, prefix='/v1')
app.include_router(notification_router, prefix='/v1')

if os.getenv("E2E_MODE") == "1":
    from app.api.routers.e2e import router as e2e_router
    app.include_router(e2e_router, prefix="/v1")


@app.get('/')
async def root():
    return {'message': 'Backend Telegramm mini app work'}
