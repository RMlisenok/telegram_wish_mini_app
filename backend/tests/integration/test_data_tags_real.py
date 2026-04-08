# tests/integration/test_data_tags_real.py
import pytest
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy import text
from app.core.data_tags import init_tags, INTEREST_TAGS, AVOID_TAGS
from app.models.questionnaire import TagForm


@pytest.mark.asyncio
async def test_init_tags_real_db():
    """Test init_tags with real database."""
    # Используем SQLite в памяти
    engine = create_async_engine("sqlite+aiosqlite:///:memory:")

    # Создаем таблицу с правильной схемой
    async with engine.begin() as conn:
        await conn.execute(text("""
            CREATE TABLE tags_forms (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                tag_value VARCHAR NOT NULL,
                type_tags BOOLEAN NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """))

    # Подменяем engine
    import app.core.data_tags
    original_engine = app.core.data_tags.async_engine
    app.core.data_tags.async_engine = engine

    try:
        # Первый запуск - создаем теги
        await init_tags()

        # Проверяем
        async with AsyncSession(engine) as session:
            result = await session.execute(text("SELECT * FROM tags_forms"))
            tags = result.fetchall()
            assert len(tags) == len(INTEREST_TAGS) + len(AVOID_TAGS)

        # Второй запуск - не должен добавить дубликаты
        await init_tags()

        async with AsyncSession(engine) as session:
            result = await session.execute(text("SELECT * FROM tags_forms"))
            tags_again = result.fetchall()
            assert len(tags_again) == len(tags)

    finally:
        app.core.data_tags.async_engine = original_engine