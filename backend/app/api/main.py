from fastapi import FastAPI
from contextlib import asynccontextmanager
# from app.core.db import init_database, drop_tables, AsyncSessionLocal
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


@asynccontextmanager
async def lifespan(app: FastAPI):
    # await init_database()
    await init_tags()
    await init_gifts()

    polling_task = asyncio.create_task(dp.start_polling(bot))
    print("✅ Backend и Бот запущены")
    yield
    polling_task.cancel()
    await bot.session.close()
    print('Stop work and clean tables')
    # await drop_tables()
    print('clean completed')


app = FastAPI(lifespan=lifespan)
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


@app.get('/')
async def root():
    return {'message': 'Backend Telegramm mini app work'}
