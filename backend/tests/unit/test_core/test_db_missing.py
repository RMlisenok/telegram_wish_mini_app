import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from sqlalchemy.exc import SQLAlchemyError
from app.core.db import (
    create_missing_tables, create_tables,
    drop_tables, init_database, check_connection
)


class TestDBMissing:
    """Tests for missing database coverage."""

    @pytest.mark.asyncio
    async def test_create_missing_tables_with_missing(self):
        """Test creating missing tables."""
        with patch("app.core.db.async_engine") as mock_engine:
            mock_conn = AsyncMock()
            mock_engine.begin.return_value.__aenter__.return_value = mock_conn

            # Первый вызов run_sync - existing_tables
            # Второй вызов - expected_tables
            mock_conn.run_sync.side_effect = [
                {"users", "wishes"},  # existing
                {"users", "wishes", "tag_forms", "gifts"}  # expected
            ]

            with patch("app.core.db.Base.metadata.tables", {
                "tag_forms": MagicMock(),
                "gifts": MagicMock()
            }):
                with patch.object(mock_conn, "run_sync") as mock_run_sync:
                    # Настраиваем для create table
                    mock_run_sync.side_effect = [
                        {"users", "wishes"},  # первый вызов
                        {"users", "wishes", "tag_forms", "gifts"},  # второй вызов
                        None,  # create table
                        None  # create table
                    ]

                    result = await create_missing_tables()
                    assert result is True

    @pytest.mark.asyncio
    async def test_create_missing_tables_exception(self):
        """Test exception when creating missing tables."""
        with patch("app.core.db.async_engine") as mock_engine:
            mock_engine.begin.side_effect = Exception("DB error")

            result = await create_missing_tables()
            assert result is None  # функция возвращает None при ошибке

    @pytest.mark.asyncio
    async def test_create_tables_exception(self):
        """Test exception in create_tables."""
        with patch("app.core.db.async_engine") as mock_engine:
            mock_engine.begin.side_effect = Exception("Create error")

            with pytest.raises(Exception):
                await create_tables()

    @pytest.mark.asyncio
    async def test_drop_tables_exception_handling(self):
        """Test drop tables exception handling."""
        with patch("app.core.db.async_engine") as mock_engine:
            mock_engine.begin.side_effect = Exception("Drop error")

            with pytest.raises(Exception):
                await drop_tables()

    @pytest.mark.asyncio
    async def test_init_database_creates_tables(self):
        """Test init_database creates missing tables."""
        with patch("app.core.db.check_connection", AsyncMock(return_value=True)):
            with patch("app.core.db.create_missing_tables", AsyncMock(return_value=True)):
                result = await init_database()
                assert result is True

    @pytest.mark.asyncio
    async def test_get_db_rollback_on_general_exception(self):
        """Test get_db rollback on general exception."""
        from app.core.db import get_db

        with patch("app.core.db.AsyncSessionLocal") as mock_session_local:
            mock_session = AsyncMock()
            mock_session.__aenter__.return_value = mock_session
            mock_session.commit = AsyncMock(side_effect=Exception("General error"))
            mock_session_local.return_value = mock_session

            with pytest.raises(Exception) as exc_info:
                async for _ in get_db():
                    pass

            mock_session.rollback.assert_called_once()