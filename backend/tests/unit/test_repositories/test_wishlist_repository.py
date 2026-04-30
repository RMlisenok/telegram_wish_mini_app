import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from datetime import datetime
from app.repositories.wishlist_repository import WishlistRepository
from app.schemas.wishlist import WishlistCreate, WishlistUpdate


class TestWishlistRepository:
    """Test suite for WishlistRepository."""

    @pytest.fixture
    def repo(self, mock_db_session):
        return WishlistRepository(mock_db_session)

    def create_mock_wishlist(self, id=1, user_id=1, name="Test Wishlist"):
        mock = MagicMock()
        mock.id = id
        mock.user_id = user_id
        mock.name = name
        mock.description = "Test description"
        mock.photo = "https://example.com/photo.jpg"
        mock.typeprivacy = "public"
        mock.created_at = datetime.now()
        mock.updated_at = datetime.now()
        return mock

    @pytest.mark.asyncio
    async def test_create_wishlist_success(self, repo, mock_db_session):
        wishlist_data = WishlistCreate(
            name="New Wishlist",
            description="Description",
            photo=None,
            typeprivacy="public"
        )
        mock_wishlist = self.create_mock_wishlist(1, 1, "New Wishlist")
        mock_db_session.add = MagicMock()
        mock_db_session.commit = AsyncMock()
        mock_db_session.refresh = AsyncMock()

        with patch('app.repositories.wishlist_repository.Wishlist', return_value=mock_wishlist):
            result = await repo.create(wishlist_data)

            assert result == mock_wishlist
            mock_db_session.add.assert_called_once()
            mock_db_session.commit.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_wishlist_success(self, repo, mock_db_session):
        mock_wishlist = self.create_mock_wishlist(1)
        mock_result = MagicMock()
        mock_result.scalar_one_or_none = MagicMock(return_value=mock_wishlist)
        mock_db_session.execute = AsyncMock(return_value=mock_result)

        result = await repo.get(1)

        assert result == mock_wishlist

    @pytest.mark.asyncio
    async def test_get_wishlist_not_found(self, repo, mock_db_session):
        mock_result = MagicMock()
        mock_result.scalar_one_or_none = MagicMock(return_value=None)
        mock_db_session.execute = AsyncMock(return_value=mock_result)

        result = await repo.get(999)

        assert result is None

    @pytest.mark.asyncio
    async def test_get_user_wishlist_asc(self, repo, mock_db_session):
        mock_wishlists = [self.create_mock_wishlist(1), self.create_mock_wishlist(2)]
        mock_result = MagicMock()
        mock_result.scalars.return_value.all = MagicMock(return_value=mock_wishlists)
        mock_db_session.execute = AsyncMock(return_value=mock_result)

        result = await repo.get_user_wishlist(1, is_desc=False, limit=10)

        assert len(result) == 2

    @pytest.mark.asyncio
    async def test_get_user_wishlist_desc(self, repo, mock_db_session):
        mock_wishlists = [self.create_mock_wishlist(2), self.create_mock_wishlist(1)]
        mock_result = MagicMock()
        mock_result.scalars.return_value.all = MagicMock(return_value=mock_wishlists)
        mock_db_session.execute = AsyncMock(return_value=mock_result)

        result = await repo.get_user_wishlist(1, is_desc=True, limit=10)

        assert len(result) == 2

    @pytest.mark.asyncio
    async def test_get_user_wishlist_empty(self, repo, mock_db_session):
        mock_result = MagicMock()
        mock_result.scalars.return_value.all = MagicMock(return_value=[])
        mock_db_session.execute = AsyncMock(return_value=mock_result)

        result = await repo.get_user_wishlist(1)

        assert result == []

    @pytest.mark.asyncio
    async def test_get_count_user_wishlist_success(self, repo, mock_db_session):
        mock_result = MagicMock()
        mock_result.scalar = MagicMock(return_value=5)
        mock_db_session.execute = AsyncMock(return_value=mock_result)

        result = await repo.get_count_user_wishlist(1)

        assert result == 5

    @pytest.mark.asyncio
    async def test_get_count_user_wishlist_zero(self, repo, mock_db_session):
        mock_result = MagicMock()
        mock_result.scalar = MagicMock(return_value=0)
        mock_db_session.execute = AsyncMock(return_value=mock_result)

        result = await repo.get_count_user_wishlist(1)

        assert result == 0

    @pytest.mark.asyncio
    async def test_update_wishlist_success(self, repo, mock_db_session):
        # Используем словарь вместо объекта WishlistUpdate
        update_data = {"name": "Updated Name", "description": "Updated desc"}
        mock_wishlist = self.create_mock_wishlist(1, 1, "Updated Name")
        
        mock_result = MagicMock()
        mock_result.scalar_one_or_none = MagicMock(return_value=mock_wishlist)
        mock_db_session.execute = AsyncMock(return_value=mock_result)
        mock_db_session.commit = AsyncMock()
        mock_db_session.refresh = AsyncMock()

        # Мокаем update напрямую
        with patch('sqlalchemy.update') as mock_update:
            mock_update_stmt = MagicMock()
            mock_update.return_value.where.return_value.values.return_value.returning = mock_update_stmt
            mock_db_session.execute.return_value = mock_result
            
            # Вызываем метод с правильными параметрами
            result = await repo.update(1, update_data)

            assert result == mock_wishlist

    @pytest.mark.asyncio
    async def test_delete_wishlist_success(self, repo, mock_db_session):
        mock_wishlist = self.create_mock_wishlist(1)
        repo.get = AsyncMock(return_value=mock_wishlist)
        mock_db_session.delete = AsyncMock()

        result = await repo.delete(1)

        assert result is True
        mock_db_session.delete.assert_called_once()

    @pytest.mark.asyncio
    async def test_delete_wishlist_not_found(self, repo, mock_db_session):
        repo.get = AsyncMock(return_value=None)

        result = await repo.delete(999)

        assert result is False

    @pytest.mark.asyncio
    async def test_delete_wishlist_exception(self, repo, mock_db_session):
        mock_wishlist = self.create_mock_wishlist(1)
        repo.get = AsyncMock(return_value=mock_wishlist)
        mock_db_session.delete = AsyncMock(side_effect=Exception("DB error"))

        result = await repo.delete(1)

        assert result is False