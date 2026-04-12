# tests/unit/test_repositories/test_wish_reservation_repository.py
import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from datetime import datetime
from app.repositories.wish_reservation_repository import WishReservationRepository


class TestWishReservationRepository:
    """Test suite for WishReservationRepository."""

    @pytest.fixture
    def repo(self, mock_db_session):
        return WishReservationRepository(mock_db_session)

    def create_mock_reservation(self, id=1, wish_wishlist_id=1, reserved_by_id=2):
        mock = MagicMock()
        mock.id = id
        mock.wish_wishlist_id = wish_wishlist_id
        mock.reserved_by_id = reserved_by_id
        mock.created_at = datetime.now()
        return mock

    # ==================== get ====================
    @pytest.mark.asyncio
    async def test_get_reservation_success(self, repo, mock_db_session):
        mock_reservation = self.create_mock_reservation(1, 1, 2)
        mock_result = MagicMock()
        mock_result.scalar_one_or_none = MagicMock(return_value=mock_reservation)
        mock_db_session.execute = AsyncMock(return_value=mock_result)

        result = await repo.get(1)

        assert result == mock_reservation

    @pytest.mark.asyncio
    async def test_get_reservation_not_found(self, repo, mock_db_session):
        mock_result = MagicMock()
        mock_result.scalar_one_or_none = MagicMock(return_value=None)
        mock_db_session.execute = AsyncMock(return_value=mock_result)

        result = await repo.get(999)

        assert result is None

    # ==================== get_reservations_by_wish_wishlist ====================
    @pytest.mark.asyncio
    async def test_get_reservations_by_wish_wishlist_success(self, repo, mock_db_session):
        mock_reservations = [self.create_mock_reservation(1), self.create_mock_reservation(2)]
        mock_result = MagicMock()
        mock_result.scalars.return_value.all = MagicMock(return_value=mock_reservations)
        mock_db_session.execute = AsyncMock(return_value=mock_result)

        result = await repo.get_reservations_by_wish_wishlist(1)

        assert len(result) == 2

    @pytest.mark.asyncio
    async def test_get_reservations_by_wish_wishlist_empty(self, repo, mock_db_session):
        mock_result = MagicMock()
        mock_result.scalars.return_value.all = MagicMock(return_value=[])
        mock_db_session.execute = AsyncMock(return_value=mock_result)

        result = await repo.get_reservations_by_wish_wishlist(1)

        assert result == []

    @pytest.mark.asyncio
    async def test_get_reservations_by_wish_wishlist_with_limit(self, repo, mock_db_session):
        mock_reservations = [self.create_mock_reservation(1)]
        mock_result = MagicMock()
        mock_result.scalars.return_value.all = MagicMock(return_value=mock_reservations)
        mock_db_session.execute = AsyncMock(return_value=mock_result)

        result = await repo.get_reservations_by_wish_wishlist(1, limit=5)

        assert len(result) == 1

    # ==================== get_user_reservations ====================
    @pytest.mark.asyncio
    async def test_get_user_reservations_success(self, repo, mock_db_session):
        mock_reservations = [self.create_mock_reservation(1, 1, 2), self.create_mock_reservation(2, 2, 2)]
        mock_result = MagicMock()
        mock_result.scalars.return_value.all = MagicMock(return_value=mock_reservations)
        mock_db_session.execute = AsyncMock(return_value=mock_result)

        result = await repo.get_user_reservations(2)

        assert len(result) == 2

    @pytest.mark.asyncio
    async def test_get_user_reservations_empty(self, repo, mock_db_session):
        mock_result = MagicMock()
        mock_result.scalars.return_value.all = MagicMock(return_value=[])
        mock_db_session.execute = AsyncMock(return_value=mock_result)

        result = await repo.get_user_reservations(2)

        assert result == []

    @pytest.mark.asyncio
    async def test_get_user_reservations_with_limit(self, repo, mock_db_session):
        mock_reservations = [self.create_mock_reservation(1, 1, 2)]
        mock_result = MagicMock()
        mock_result.scalars.return_value.all = MagicMock(return_value=mock_reservations)
        mock_db_session.execute = AsyncMock(return_value=mock_result)

        result = await repo.get_user_reservations(2, limit=5)

        assert len(result) == 1

    # ==================== check_wish_reservation ====================
    @pytest.mark.asyncio
    async def test_check_wish_reservation_true(self, repo, mock_db_session):
        mock_reservation = self.create_mock_reservation(1, 1, 2)
        mock_result = MagicMock()
        mock_result.scalar_one_or_none = MagicMock(return_value=mock_reservation)
        mock_db_session.execute = AsyncMock(return_value=mock_result)

        result = await repo.check_wish_reservation(1)

        assert result is True

    @pytest.mark.asyncio
    async def test_check_wish_reservation_false(self, repo, mock_db_session):
        mock_result = MagicMock()
        mock_result.scalar_one_or_none = MagicMock(return_value=None)
        mock_db_session.execute = AsyncMock(return_value=mock_result)

        result = await repo.check_wish_reservation(1)

        assert result is False

    # ==================== create ====================
    @pytest.mark.asyncio
    async def test_create_reservation_success(self, repo, mock_db_session):
        repo.check_wish_reservation = AsyncMock(return_value=False)
        mock_reservation = self.create_mock_reservation(1, 1, 2)
        mock_db_session.add = MagicMock()
        mock_db_session.commit = AsyncMock()
        mock_db_session.refresh = AsyncMock()

        with patch('app.repositories.wish_reservation_repository.WishReservation', return_value=mock_reservation):
            result = await repo.create(1, 2)

            assert result == mock_reservation
            mock_db_session.add.assert_called_once()
            mock_db_session.commit.assert_called_once()

    @pytest.mark.asyncio
    async def test_create_reservation_already_exists(self, repo, mock_db_session):
        repo.check_wish_reservation = AsyncMock(return_value=True)

        result = await repo.create(1, 2)

        assert result is None

    @pytest.mark.asyncio
    async def test_create_reservation_exception(self, repo, mock_db_session):
        repo.check_wish_reservation = AsyncMock(return_value=False)
        mock_db_session.commit = AsyncMock(side_effect=Exception("DB error"))
        mock_db_session.rollback = AsyncMock()

        with patch('app.repositories.wish_reservation_repository.WishReservation', return_value=MagicMock()):
            result = await repo.create(1, 2)

            assert result is None
            mock_db_session.rollback.assert_called_once()

    # ==================== delete_reservation_idx ====================
    @pytest.mark.asyncio
    async def test_delete_reservation_idx_success(self, repo, mock_db_session):
        mock_reservation = self.create_mock_reservation(1, 1, 2)
        mock_result = MagicMock()
        mock_result.scalar_one_or_none = MagicMock(return_value=mock_reservation)
        mock_db_session.execute = AsyncMock(return_value=mock_result)
        mock_db_session.delete = AsyncMock()

        result = await repo.delete_reservation_idx(1, 2)

        assert result is True
        mock_db_session.delete.assert_called_once()

    @pytest.mark.asyncio
    async def test_delete_reservation_idx_not_found(self, repo, mock_db_session):
        mock_result = MagicMock()
        mock_result.scalar_one_or_none = MagicMock(return_value=None)
        mock_db_session.execute = AsyncMock(return_value=mock_result)

        result = await repo.delete_reservation_idx(1, 2)

        assert result is False