import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from telegram_wish_mini_app.backend.app.core.db import init_database, drop_tables
from telegram_wish_mini_app.backend.app.api.routers.auth import router as auth_routers
from telegram_wish_mini_app.backend.app.api.routers.user import router as user_routers
from telegram_wish_mini_app.backend.app.api.routers.questionnaire import router as questionnaire_routers


# Настройка логов
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_database()
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