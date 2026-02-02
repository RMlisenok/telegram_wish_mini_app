from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy import text, inspect
from typing import AsyncGenerator
from fastapi import HTTPException, status
from sqlalchemy.exc import SQLAlchemyError
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
            await session.commit()
        except SQLAlchemyError as e:
            await session.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f'Database error: {str(e)}'
            )
        except HTTPException:
            await session.rollback()
            raise
        except Exception as e:
            await session.rollback()
            print(f"Exception e: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail='Internal server error'
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


def _sync_get_table_names(conn):
    inspector = inspect(conn)
    return inspector.get_table_names()


async def create_tables():
    try:
        async with async_engine.begin() as conn:
            existing_tables = await conn.run_sync(_sync_get_table_names)

            if existing_tables:
                print(f'Tables are existing: {len(existing_tables)} tables')
                print(f'Existing tables: {", ".join(existing_tables)}')
                return False

            await conn.run_sync(Base.metadata.create_all)
            print('All tables created')
            return True
    except Exception as e:
        print(f'Error create tables: {e}')
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
    await create_tables()
    return True
