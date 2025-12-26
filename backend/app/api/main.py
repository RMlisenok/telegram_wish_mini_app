import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from app.core.db import init_database, drop_tables
from app.api.routers.auth import router as auth_routers
from app.api.routers.user import router as user_routers
from app.api.routers.questionnaire import router as questionnaire_routers
from app.core.init_data import init_tags
from app.api.routers.settings import router as settings_routers
from app.api.routers.recommendations import router as recommendation_routers
from app.api.routers.access import router as access_routers
from app.api.handlers.access_handlers import router as access_handlers
from app.core.db import AsyncSessionLocal
from app.core.init_gifts import init_gifts

# Настройка логов
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_database()
    async with AsyncSessionLocal() as session:
        await init_tags(session)
        await init_gifts(session)
    # bot = Bot(token="ТОКЕН")
    # setup_scheduler(bot)
    yield
    print('Stop work and clean tables')
    await drop_tables()
    print('clean completed')

app = FastAPI(
    title="Подари мне API",
    description="API для Telegram Mini-App управления вишлистами и подарками",
    version="1.0.0"
)

app = FastAPI(lifespan=lifespan)
app.include_router(auth_routers, prefix='/api/v1')
app.include_router(user_routers, prefix='/api/v1')
app.include_router(questionnaire_routers, prefix='/api/v1')
app.include_router(settings_routers, prefix='/api/v1')
app.include_router(recommendation_routers, prefix='/api/v1')
app.include_router(access_routers, prefix='/api/v1')
app.include_router(access_handlers, prefix='/api/v1')
app.add_middleware(
    CORSMiddleware,
    allow_origins=['*'],
    allow_credentials=True,
    allow_methods=['*'],
    allow_headers=['*']
)

@app.get("/")
async def root():
    return {'message': 'Backend Telegramm mini app work'}