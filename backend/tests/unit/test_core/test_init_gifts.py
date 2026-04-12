# tests/unit/test_core/test_init_gifts.py
import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from app.core.init_gifts import init_gifts, GIFT_DATA


class TestInitGifts:
    """Test suite for init_gifts module."""

    @pytest.mark.asyncio
    async def test_init_gifts_already_exists(self):
        """Test initializing gifts when they already exist."""
        with patch("app.core.init_gifts.AsyncSession") as mock_session:
            mock_session_instance = AsyncMock()
            mock_session.return_value.__aenter__.return_value = mock_session_instance

            mock_result = MagicMock()
            mock_result.scalars.return_value.first = MagicMock(return_value=True)
            mock_session_instance.execute = AsyncMock(return_value=mock_result)

            await init_gifts()

            # Should not add any gifts
            mock_session_instance.add.assert_not_called()

    @pytest.mark.asyncio
    async def test_init_gifts_create_new(self):
        """Test initializing gifts when none exist."""
        with patch("app.core.init_gifts.AsyncSession") as mock_session:
            mock_session_instance = AsyncMock()
            mock_session.return_value.__aenter__.return_value = mock_session_instance

            mock_result = MagicMock()
            mock_result.scalars.return_value.first = MagicMock(return_value=None)
            mock_session_instance.execute = AsyncMock(return_value=mock_result)

            await init_gifts()

            # Should add gifts for each item
            assert mock_session_instance.add.call_count == len(GIFT_DATA)
            mock_session_instance.commit.assert_called_once()

    @pytest.mark.asyncio
    async def test_init_gifts_exception(self):
        """Test initializing gifts with exception."""
        with patch("app.core.init_gifts.AsyncSession") as mock_session:
            mock_session_instance = AsyncMock()
            mock_session.return_value.__aenter__.return_value = mock_session_instance
            mock_session_instance.commit = AsyncMock(side_effect=Exception("DB error"))

            mock_result = MagicMock()
            mock_result.scalars.return_value.first = MagicMock(return_value=None)
            mock_session_instance.execute = AsyncMock(return_value=mock_result)

            with pytest.raises(Exception):
                await init_gifts()