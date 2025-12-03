from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy import text
from typing import AsyncGenerator

from app.core.base import Base
from app.models.user import User
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
        except Exception:
            await session.rollback()
        finally:
            await session.close()


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


async def check_connection():
    try:
        async with async_engine.begin() as conn:
            result = await conn.execute(text('SELECT 1'))
            print(f'Data Base connect: {result.scalar()}')
            return True
    except Exception as e:
        print(f'Data Base not connect: {e}')
        return False


async def check_tables_exist():
    try:
        async with async_engine.begin() as conn:
            tables_to_check = ['users']

            for table in tables_to_check:
                query = text(
                    "SELECT EXISTS ("
                    "SELECT FROM information_schema.tables "
                    "WHERE table_name = :table_name"
                    ")"
                )
                result = await conn.execute(
                    query,
                    {"table_name": table}
                )
                exists = result.scalar()
                if not exists:
                    print(f'Table not exists: {table}')
                    return False
                return True
    except Exception as e:
        print(f'Error: {e}')
        return False


async def init_database():
    if not await check_connection():
        return False

    print('START CREATED TABLES')
    # if not await check_tables_exist():
    #     await create_tables()
    await create_tables()
    return True
