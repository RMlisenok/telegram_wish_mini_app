from fastapi import FastAPI
from contextlib import asynccontextmanager
from app.core.db import init_database, drop_tables
from app.api.routers.auth import router as auth_routers


@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_database()
    yield
    print('Stop work and clean tables')
    await drop_tables()
    print('clean completed')


app = FastAPI(lifespan=lifespan)

app.include_router(auth_routers)


@app.get('/')
async def root():
    return {'message': 'Backend Telegram mini app work'}
