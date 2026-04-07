# tests/unit/test_repositories/test_wish_repository.py
import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from datetime import datetime
from app.repositories.wish_repository import WishRepository
from app.models.wish import Wish, CurrencyEnum
from app.schemas.wish import WishCreate


class TestWishRepository:
    """Test suite for WishRepository."""

    @pytest.fixture
    def repo(self, mock_db_session):
        return WishRepository(mock_db_session)

    def create_mock_wish(self, id=1, user_id=1, name="Test Wish"):
        mock = MagicMock(spec=Wish)
        mock.id = id
        mock.user_id = user_id
        mock.name = name
        mock.photo = "https://example.com/photo.jpg"
        mock.url_gift = "https://example.com/gift"
        mock.price = 100.0
        mock.currency = CurrencyEnum.RUB
        mock.description = "Test description"
        mock.is_booked = False
        mock.status_is_finished = False
        mock.created_at = datetime.now()
        mock.updated_at = datetime.now()
        return mock

    # ==================== create ====================
    @pytest.mark.asyncio
    async def test_create_wish_success(self, repo, mock_db_session):
        wish_data = WishCreate(
            name="New Wish",
            photo=None,
            url_gift="https://example.com/gift",
            price=100.0,
            currency="RUB",
            description="Description"
        )
        mock_wish = self.create_mock_wish(1, 1, "New Wish")
        mock_db_session.add = MagicMock()
        mock_db_session.commit = AsyncMock()
        mock_db_session.refresh = AsyncMock()

        with patch('app.repositories.wish_repository.Wish', return_value=mock_wish):
            result = await repo.create(wish_data)

            assert result == mock_wish
            mock_db_session.add.assert_called_once()
            mock_db_session.commit.assert_called_once()

    # ==================== get ====================
    @pytest.mark.asyncio
    async def test_get_wish_success(self, repo, mock_db_session):
        mock_wish = self.create_mock_wish(1)
        mock_result = MagicMock()
        mock_result.scalar_one_or_none = MagicMock(return_value=mock_wish)
        mock_db_session.execute = AsyncMock(return_value=mock_result)

        result = await repo.get(1)

        assert result == mock_wish

    @pytest.mark.asyncio
    async def test_get_wish_not_found(self, repo, mock_db_session):
        mock_result = MagicMock()
        mock_result.scalar_one_or_none = MagicMock(return_value=None)
        mock_db_session.execute = AsyncMock(return_value=mock_result)

        result = await repo.get(999)

        assert result is None

    # ==================== update ====================
    @pytest.mark.asyncio
    async def test_update_wish_success(self, repo, mock_db_session):
        update_data = {"name": "Updated Wish"}
        mock_wish = self.create_mock_wish(1, 1, "Updated Wish")
        
        mock_result = MagicMock()
        mock_result.scalar_one_or_none = MagicMock(return_value=mock_wish)
        mock_db_session.execute = AsyncMock(return_value=mock_result)
        mock_db_session.refresh = AsyncMock()

        result = await repo.update(1, update_data)

        assert result == mock_wish

    @pytest.mark.asyncio
    async def test_update_wish_no_data(self, repo, mock_db_session):
        update_data = {}
        mock_wish = self.create_mock_wish(1)
        
        repo.get = AsyncMock(return_value=mock_wish)

        result = await repo.update(1, update_data)

        assert result == mock_wish

    # ==================== get_user_wish ====================
    @pytest.mark.asyncio
    async def test_get_user_wish_desc(self, repo, mock_db_session):
        mock_wishes = [self.create_mock_wish(1), self.create_mock_wish(2)]
        mock_result = MagicMock()
        mock_result.scalars.return_value.all = MagicMock(return_value=mock_wishes)
        mock_db_session.execute = AsyncMock(return_value=mock_result)

        result = await repo.get_user_wish(1, is_desc=True, limit=20)

        assert len(result) == 2

    @pytest.mark.asyncio
    async def test_get_user_wish_asc(self, repo, mock_db_session):
        mock_wishes = [self.create_mock_wish(1), self.create_mock_wish(2)]
        mock_result = MagicMock()
        mock_result.scalars.return_value.all = MagicMock(return_value=mock_wishes)
        mock_db_session.execute = AsyncMock(return_value=mock_result)

        result = await repo.get_user_wish(1, is_desc=False, limit=20)

        assert len(result) == 2

    @pytest.mark.asyncio
    async def test_get_user_wish_empty(self, repo, mock_db_session):
        mock_result = MagicMock()
        mock_result.scalars.return_value.all = MagicMock(return_value=[])
        mock_db_session.execute = AsyncMock(return_value=mock_result)

        result = await repo.get_user_wish(1)

        assert result == []

    # ==================== get_user_wish_sorted ====================
    @pytest.mark.asyncio
    async def test_get_user_wish_sorted_finished(self, repo, mock_db_session):
        mock_wishes = [self.create_mock_wish(1)]
        mock_result = MagicMock()
        mock_result.scalars.return_value.all = MagicMock(return_value=mock_wishes)
        mock_db_session.execute = AsyncMock(return_value=mock_result)

        result = await repo.get_user_wish_sorted(1, is_finish=True, limit=20)

        assert len(result) == 1

    @pytest.mark.asyncio
    async def test_get_user_wish_sorted_not_finished(self, repo, mock_db_session):
        mock_wishes = [self.create_mock_wish(1)]
        mock_result = MagicMock()
        mock_result.scalars.return_value.all = MagicMock(return_value=mock_wishes)
        mock_db_session.execute = AsyncMock(return_value=mock_result)

        result = await repo.get_user_wish_sorted(1, is_finish=False, limit=20)

        assert len(result) == 1

    # ==================== get_count_user_wish ====================
    @pytest.mark.asyncio
    async def test_get_count_user_wish_success(self, repo, mock_db_session):
        mock_result = MagicMock()
        mock_result.scalar = MagicMock(return_value=5)
        mock_db_session.execute = AsyncMock(return_value=mock_result)

        result = await repo.get_count_user_wish(1)

        assert result == 5

    # ==================== delete ====================
    @pytest.mark.asyncio
    async def test_delete_wish_success(self, repo, mock_db_session):
        mock_wish = self.create_mock_wish(1)
        repo.get = AsyncMock(return_value=mock_wish)
        mock_db_session.delete = AsyncMock()

        result = await repo.delete(1)

        assert result is True
        mock_db_session.delete.assert_called_once()

    @pytest.mark.asyncio
    async def test_delete_wish_not_found(self, repo, mock_db_session):
        repo.get = AsyncMock(return_value=None)

        result = await repo.delete(999)

        assert result is False

    @pytest.mark.asyncio
    async def test_delete_wish_exception(self, repo, mock_db_session):
        mock_wish = self.create_mock_wish(1)
        repo.get = AsyncMock(return_value=mock_wish)
        mock_db_session.delete = AsyncMock(side_effect=Exception("DB error"))
        mock_db_session.rollback = AsyncMock()

        result = await repo.delete(1)

        assert result is False
        mock_db_session.rollback.assert_called_once()