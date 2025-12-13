from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy import text
from typing import AsyncGenerator
from fastapi import HTTPException, status

from app.core.config import settings

async_engine = create_async_engine(
    url=settings.DATABASE_URL_asyncpg,
    echo=True
)

AsyncSessionLocal = sessionmaker(
    async_engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autoflush=False,
    autocommit=False,
)

async def check_connection():
    try:
        async with async_engine.begin() as conn:
            result = await conn.execute(text('SELECT 1'))
            print(f'Data Base connect: {result.scalar()}')
            return True
    except Exception as e:
        print(f'Data Base not connect: {e}')
        return False