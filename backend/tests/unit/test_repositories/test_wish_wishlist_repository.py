import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from datetime import datetime
from app.repositories.wish_wishlist_repository import WishWishlistRepository


class TestWishWishlistRepository:
    """Test suite for WishWishlistRepository."""

    @pytest.fixture
    def repo(self, mock_db_session):
        return WishWishlistRepository(mock_db_session)

    def create_mock_connection(self, id=1, wish_id=1, wishlist_id=1):
        mock = MagicMock()
        mock.id = id
        mock.wish_id = wish_id
        mock.wishlist_id = wishlist_id
        mock.is_pinned = False
        mock.order_position = 0
        mock.created_at = datetime.now()
        mock.updated_at = datetime.now()
        return mock

    def create_mock_wish(self, id=1):
        mock = MagicMock()
        mock.id = id
        return mock

    def create_mock_wishlist(self, id=1):
        mock = MagicMock()
        mock.id = id
        return mock

    @pytest.mark.asyncio
    async def test_get_connection_success(self, repo, mock_db_session):
        mock_connection = self.create_mock_connection(1, 1, 1)
        mock_result = MagicMock()
        mock_result.scalar_one_or_none = MagicMock(return_value=mock_connection)
        mock_db_session.execute = AsyncMock(return_value=mock_result)

        result = await repo.get(1, 1)

        assert result == mock_connection

    @pytest.mark.asyncio
    async def test_get_connection_not_found(self, repo, mock_db_session):
        mock_result = MagicMock()
        mock_result.scalar_one_or_none = MagicMock(return_value=None)
        mock_db_session.execute = AsyncMock(return_value=mock_result)

        result = await repo.get(999, 999)

        assert result is None

    @pytest.mark.asyncio
    async def test_get_by_id_success(self, repo, mock_db_session):
        mock_connection = self.create_mock_connection(1)
        mock_result = MagicMock()
        mock_result.scalar_one_or_none = MagicMock(return_value=mock_connection)
        mock_db_session.execute = AsyncMock(return_value=mock_result)

        result = await repo.get_by_id(1)

        assert result == mock_connection

    @pytest.mark.asyncio
    async def test_get_wishes_from_wishlist_success(self, repo, mock_db_session):
        mock_connections = [self.create_mock_connection(1), self.create_mock_connection(2)]
        mock_result = MagicMock()
        mock_result.unique.return_value.scalars.return_value.all = MagicMock(return_value=mock_connections)
        mock_db_session.execute = AsyncMock(return_value=mock_result)

        # Мокаем joinedload, чтобы избежать ошибок с моделями
        with patch('sqlalchemy.orm.joinedload', return_value=MagicMock()):
            result = await repo.get_wishes_from_wishlist(1, limit=10)

            assert len(result) == 2

    @pytest.mark.asyncio
    async def test_get_wishes_from_wishlist_empty(self, repo, mock_db_session):
        mock_result = MagicMock()
        mock_result.unique.return_value.scalars.return_value.all = MagicMock(return_value=[])
        mock_db_session.execute = AsyncMock(return_value=mock_result)

        with patch('sqlalchemy.orm.joinedload', return_value=MagicMock()):
            result = await repo.get_wishes_from_wishlist(1)

            assert result == []

    @pytest.mark.asyncio
    async def test_create_wish_to_wishlist_success(self, repo, mock_db_session):
        repo.get = AsyncMock(return_value=None)
        
        mock_wish_result = MagicMock()
        mock_wish_result.scalar_one_or_none = MagicMock(return_value=self.create_mock_wish(1))
        mock_wishlist_result = MagicMock()
        mock_wishlist_result.scalar_one_or_none = MagicMock(return_value=self.create_mock_wishlist(1))
        
        mock_db_session.execute = AsyncMock()
        mock_db_session.execute.side_effect = [mock_wish_result, mock_wishlist_result]
        
        repo.count_wishes_in_wishlist = AsyncMock(return_value=0)
        
        mock_connection = self.create_mock_connection(1, 1, 1)
        mock_db_session.add = MagicMock()
        mock_db_session.commit = AsyncMock()
        mock_db_session.refresh = AsyncMock()

        with patch('app.repositories.wish_wishlist_repository.WishWishlist', return_value=mock_connection):
            result = await repo.create_wish_to_wishlist(1, 1, False)

            assert result == mock_connection

    @pytest.mark.asyncio
    async def test_create_wish_to_wishlist_already_exists(self, repo, mock_db_session):
        mock_connection = self.create_mock_connection(1)
        repo.get = AsyncMock(return_value=mock_connection)

        result = await repo.create_wish_to_wishlist(1, 1, False)

        assert result is None

    @pytest.mark.asyncio
    async def test_create_wish_to_wishlist_wish_not_found(self, repo, mock_db_session):
        repo.get = AsyncMock(return_value=None)
        
        mock_wish_result = MagicMock()
        mock_wish_result.scalar_one_or_none = MagicMock(return_value=None)
        mock_db_session.execute = AsyncMock(return_value=mock_wish_result)

        result = await repo.create_wish_to_wishlist(999, 1, False)

        assert result is None

    @pytest.mark.asyncio
    async def test_update_connection_success(self, repo, mock_db_session):
        mock_connection = self.create_mock_connection(1)
        repo.get_by_id = AsyncMock(return_value=mock_connection)
        mock_db_session.commit = AsyncMock()
        mock_db_session.refresh = AsyncMock()

        result = await repo.update_connection(1, {"is_pinned": True})

        assert result == mock_connection

    @pytest.mark.asyncio
    async def test_update_connection_not_found(self, repo, mock_db_session):
        repo.get_by_id = AsyncMock(return_value=None)

        result = await repo.update_connection(999, {"is_pinned": True})

        assert result is None

    @pytest.mark.asyncio
    async def test_remove_wish_from_wishlist_success(self, repo, mock_db_session):
        mock_connection = self.create_mock_connection(1)
        repo.get = AsyncMock(return_value=mock_connection)
        mock_db_session.delete = AsyncMock()
        mock_db_session.commit = AsyncMock()

        result = await repo.remove_wish_from_wishlist(1, 1)

        assert result is True
        mock_db_session.delete.assert_called_once()

    @pytest.mark.asyncio
    async def test_remove_wish_from_wishlist_not_found(self, repo, mock_db_session):
        repo.get = AsyncMock(return_value=None)

        result = await repo.remove_wish_from_wishlist(999, 999)

        assert result is False

    @pytest.mark.asyncio
    async def test_get_wish_from_all_wishlist_success(self, repo, mock_db_session):
        mock_connections = [self.create_mock_connection(1), self.create_mock_connection(2)]
        mock_result = MagicMock()
        mock_result.scalars.return_value.all = MagicMock(return_value=mock_connections)
        mock_db_session.execute = AsyncMock(return_value=mock_result)

        with patch('sqlalchemy.orm.joinedload', return_value=MagicMock()):
            result = await repo.get_wish_from_all_wishlist(1, limit=50)

            assert len(result) == 2

    @pytest.mark.asyncio
    async def test_get_wishlist_from_all_wishes_success(self, repo, mock_db_session):
        mock_connections = [self.create_mock_connection(1), self.create_mock_connection(2)]
        mock_result = MagicMock()
        mock_result.scalars.return_value.all = MagicMock(return_value=mock_connections)
        mock_db_session.execute = AsyncMock(return_value=mock_result)

        result = await repo.get_wishlist_from_all_wishes(1, limit=10)

        assert len(result) == 2

    @pytest.mark.asyncio
    async def test_count_wishes_in_wishlist_success(self, repo, mock_db_session):
        mock_result = MagicMock()
        mock_result.scalar_one_or_none = MagicMock(return_value=5)
        mock_db_session.execute = AsyncMock(return_value=mock_result)

        result = await repo.count_wishes_in_wishlist(1)

        assert result == 5

    @pytest.mark.asyncio
    async def test_count_wishes_in_wishlist_none(self, repo, mock_db_session):
        mock_result = MagicMock()
        mock_result.scalar_one_or_none = MagicMock(return_value=None)
        mock_db_session.execute = AsyncMock(return_value=mock_result)

        result = await repo.count_wishes_in_wishlist(1)

        assert result == 0

    @pytest.mark.asyncio
    async def test_delete_wish_in_wishlists_success(self, repo, mock_db_session):
        mock_connections = [self.create_mock_connection(1), self.create_mock_connection(2)]
        mock_result = MagicMock()
        mock_result.scalars.return_value.all = MagicMock(return_value=mock_connections)
        mock_db_session.execute = AsyncMock(return_value=mock_result)
        mock_db_session.delete = AsyncMock()
        mock_db_session.commit = AsyncMock()

        result = await repo.delete_wish_in_wishlists(1)

        assert result == 2
        assert mock_db_session.delete.call_count == 2

    @pytest.mark.asyncio
    async def test_delete_wish_in_wishlists_no_connections(self, repo, mock_db_session):
        mock_result = MagicMock()
        mock_result.scalars.return_value.all = MagicMock(return_value=[])
        mock_db_session.execute = AsyncMock(return_value=mock_result)

        result = await repo.delete_wish_in_wishlists(999)

        assert result == 0