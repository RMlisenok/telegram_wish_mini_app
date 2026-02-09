from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy import text, inspect
from typing import AsyncGenerator, Set
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


def _sync_get_table_names(conn) -> Set[str]:
    inspector = inspect(conn)
    tables_name = inspector.get_table_names()

    return set(tables_name)


def _sync_get_expected_tables(conn) -> Set[str]:
    metadata = Base.metadata
    return {table.name for table in metadata.tables.values()}


async def create_missing_tables():
    try:
        async with async_engine.begin() as conn:
            existing_tables = await conn.run_sync(_sync_get_table_names)

            expected_tables = await conn.run_sync(_sync_get_expected_tables)

            missing_tables = expected_tables - existing_tables
            if not missing_tables:
                print(f'All tables existing: {len(existing_tables)} tables')
                print(f'Exists tables: {", ".join(sorted(existing_tables))}')
                return False

            print(f'Find missiong tables: {", ".join(sorted(missing_tables))}')

            metadata = Base.metadata
            for table_name in missing_tables:
                table = metadata.tables[table_name]
                print(f'Create table: {table_name}')
                await conn.run_sync(table.create)

            print(f'Create {len(missing_tables)} missing tables')
            return True
    except Exception as e:
        print(f"Error create tables: {e}")


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
    # await create_tables()
    await create_missing_tables()
    return True
