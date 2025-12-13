from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy import text
from typing import AsyncGenerator
from fastapi import HTTPException, status

from app.core.base import Base
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


async def get_db() -> AsyncGenerator:
    async with AsyncSessionLocal() as session:
        try:
            yield session
        except Exception as e:
            await session.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f'Error database: {str(e)}'
            )
        finally:
            await session.close()


async def check_connection():
    try:
        async with async_engine.begin() as conn:
            result = await conn.execute(text('SELECT 1'))
            print(f'Data Base connect: {result.scalar()}')
            return True
    except Exception as e:
        print(f'Data Base not connect: {e}')
        return False


async def create_tables():
    try:
        async with async_engine.begin() as conn:

            table_count = len(Base.metadata.tables)
            print(f"Found: {table_count} tables in metadata")
            await conn.run_sync(Base.metadata.create_all)
            print('All tables created')

    except Exception as e:
        print(f'Error create: {e}')
        raise


async def drop_tables():
    try:
        async with async_engine.begin() as conn:
            await conn.run_sync(Base.metadata.drop_all)
            print('All tables deleted')
    except Exception as e:
        print(f'Error for deleted all tables: {e}')
        raise


async def init_database():
    if not await check_connection():
        return False

    print('START CREATED TABLES')
    await create_tables()
    return True
