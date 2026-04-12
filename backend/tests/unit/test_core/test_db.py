# tests/unit/test_core/test_db.py
import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from sqlalchemy.exc import SQLAlchemyError
from fastapi import HTTPException
from app.core.db import get_db, check_connection, init_database, create_tables, drop_tables


class TestDB:
    """Test suite for database functions."""

    @pytest.mark.asyncio
    async def test_get_db_success(self):
        """Test getting database session successfully."""
        with patch("app.core.db.AsyncSessionLocal") as mock_session_local:
            mock_session = AsyncMock()
            mock_session.__aenter__.return_value = mock_session
            mock_session_local.return_value = mock_session

            async for session in get_db():
                assert session == mock_session
                break

    @pytest.mark.asyncio
    async def test_get_db_sqlalchemy_error(self):
        """Test database session with SQLAlchemy error."""
        with patch("app.core.db.AsyncSessionLocal") as mock_session_local:
            mock_session = AsyncMock()
            mock_session.__aenter__.return_value = mock_session
            mock_session.commit = AsyncMock(side_effect=SQLAlchemyError("DB error"))
            mock_session_local.return_value = mock_session

            with pytest.raises(HTTPException) as exc_info:
                async for _ in get_db():
                    pass

            assert exc_info.value.status_code == 500
            assert "Database error" in str(exc_info.value.detail)

    @pytest.mark.asyncio
    async def test_get_db_http_exception(self):
        """Test database session with HTTP exception."""
        with patch("app.core.db.AsyncSessionLocal") as mock_session_local:
            mock_session = AsyncMock()
            mock_session.__aenter__.return_value = mock_session
            mock_session.commit = AsyncMock(side_effect=HTTPException(status_code=400, detail="Bad request"))
            mock_session_local.return_value = mock_session

            with pytest.raises(HTTPException) as exc_info:
                async for _ in get_db():
                    pass

            assert exc_info.value.status_code == 400

    @pytest.mark.asyncio
    async def test_check_connection_success(self):
        """Test database connection successful."""
        with patch("app.core.db.async_engine") as mock_engine:
            mock_conn = AsyncMock()
            mock_result = MagicMock()
            mock_result.scalar.return_value = 1
            mock_conn.execute.return_value = mock_result
            mock_engine.begin.return_value.__aenter__.return_value = mock_conn

            result = await check_connection()

            assert result is True

    @pytest.mark.asyncio
    async def test_check_connection_failure(self):
        """Test database connection failure."""
        with patch("app.core.db.async_engine") as mock_engine:
            mock_engine.begin.side_effect = Exception("Connection failed")

            result = await check_connection()

            assert result is False

    @pytest.mark.asyncio
    async def test_create_tables_already_exist(self):
        """Test creating tables when they already exist."""
        with patch("app.core.db.async_engine") as mock_engine:
            mock_conn = AsyncMock()
            mock_engine.begin.return_value.__aenter__.return_value = mock_conn

            with patch("app.core.db._sync_get_table_names", return_value={"users", "wishes"}):
                result = await create_tables()

                assert result is False

    @pytest.mark.asyncio
    async def test_drop_tables_success(self):
        """Test dropping tables successfully."""
        with patch("app.core.db.async_engine") as mock_engine:
            mock_conn = AsyncMock()
            mock_engine.begin.return_value.__aenter__.return_value = mock_conn

            await drop_tables()

            mock_conn.run_sync.assert_called_once()

    @pytest.mark.asyncio
    async def test_drop_tables_exception(self):
        """Test dropping tables with exception."""
        with patch("app.core.db.async_engine") as mock_engine:
            mock_conn = AsyncMock()
            mock_conn.run_sync.side_effect = Exception("Drop error")
            mock_engine.begin.return_value.__aenter__.return_value = mock_conn

            with pytest.raises(Exception):
                await drop_tables()

    @pytest.mark.asyncio
    async def test_init_database_success(self):
        """Test database initialization successful."""
        with patch("app.core.db.check_connection", AsyncMock(return_value=True)):
            with patch("app.core.db.create_missing_tables", AsyncMock(return_value=True)):
                result = await init_database()

                assert result is True

    @pytest.mark.asyncio
    async def test_init_database_connection_failed(self):
        """Test database initialization with connection failure."""
        with patch("app.core.db.check_connection", AsyncMock(return_value=False)):
            result = await init_database()

            assert result is False