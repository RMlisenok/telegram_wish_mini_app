# tests/unit/test_services/test_wish_reservation_service.py
import pytest
from unittest.mock import AsyncMock, MagicMock
from datetime import datetime
from app.services.wish_reservation_service import ReservationService
from app.schemas.wish_reservation import ReservationCreate


class TestWishReservationService:
    """Test suite for ReservationService."""
    
    @pytest.fixture
    def reservation_service(self, mock_db_session) -> ReservationService:
        """Create ReservationService instance with mocked dependencies."""
        service = ReservationService(mock_db_session)
        service.rep_reservation = AsyncMock()
        service.rep_wish = AsyncMock()
        service.rep_wishlist = AsyncMock()
        service.rep_wish_wishlist = AsyncMock()
        return service

    def create_mock_reservation(self, id=1, wish_wishlist_id=1, reserved_by_id=2):
        """Create a mock reservation."""
        mock = MagicMock()
        mock.id = id
        mock.wish_wishlist_id = wish_wishlist_id
        mock.reserved_by_id = reserved_by_id
        mock.created_at = datetime.now()
        return mock

    def create_mock_connection(self, wish_id=1):
        """Create a mock wish-wishlist connection."""
        mock = MagicMock()
        mock.wish_id = wish_id
        return mock

    # ==================== get_reservation ====================
    @pytest.mark.asyncio
    async def test_get_reservation_success(self, reservation_service):
        """Test successfully getting a reservation."""
        mock_reservation = self.create_mock_reservation(1, 1, 2)
        reservation_service.rep_reservation.get = AsyncMock(return_value=mock_reservation)
        
        result = await reservation_service.get_reservation(1)
        
        assert result is not None
        assert result.wish_wishlist_id == 1
        assert result.reserved_by_id == 2
    
    @pytest.mark.asyncio
    async def test_get_reservation_not_found(self, reservation_service):
        """Test getting non-existent reservation."""
        reservation_service.rep_reservation.get = AsyncMock(return_value=None)
        
        result = await reservation_service.get_reservation(999)
        
        assert result is None

    # ==================== create_reservation ====================
    @pytest.mark.asyncio
    async def test_create_reservation_success(self, reservation_service):
        """Test successfully creating a reservation."""
        reservation_create = ReservationCreate(wish_wishlist_id=1)
        reservation_service.rep_reservation.check_wish_reservation = AsyncMock(return_value=False)
        
        mock_connection = self.create_mock_connection(1)
        reservation_service.rep_wish_wishlist.get_by_id = AsyncMock(return_value=mock_connection)
        
        mock_reservation = self.create_mock_reservation(1, 1, 2)
        reservation_service.rep_reservation.create = AsyncMock(return_value=mock_reservation)
        reservation_service.rep_wish.update = AsyncMock(return_value=True)
        
        result = await reservation_service.create_reservation(2, reservation_create)
        
        assert result is not None
        assert result.wish_wishlist_id == 1
        assert result.reserved_by_id == 2
        reservation_service.rep_wish.update.assert_called_once_with(1, {"is_booked": True})
    
    @pytest.mark.asyncio
    async def test_create_reservation_already_reserved(self, reservation_service):
        """Test creating reservation for already reserved wish."""
        reservation_create = ReservationCreate(wish_wishlist_id=1)
        reservation_service.rep_reservation.check_wish_reservation = AsyncMock(return_value=True)
        
        result = await reservation_service.create_reservation(2, reservation_create)
        
        assert result is None
    
    @pytest.mark.asyncio
    async def test_create_reservation_connection_not_found(self, reservation_service):
        """Test creating reservation when wish-wishlist connection not found."""
        reservation_create = ReservationCreate(wish_wishlist_id=1)
        reservation_service.rep_reservation.check_wish_reservation = AsyncMock(return_value=False)
        reservation_service.rep_wish_wishlist.get_by_id = AsyncMock(return_value=None)
        
        result = await reservation_service.create_reservation(2, reservation_create)
        
        assert result is None

    # ==================== remove_reservation ====================
    @pytest.mark.asyncio
    async def test_remove_reservation_success(self, reservation_service):
        """Test successfully removing a reservation."""
        reservation_service.rep_reservation.delete_reservation_idx = AsyncMock(return_value=True)
        
        mock_connection = self.create_mock_connection(1)
        reservation_service.rep_wish_wishlist.get_by_id = AsyncMock(return_value=mock_connection)
        reservation_service.rep_wish.update = AsyncMock(return_value=True)
        
        result = await reservation_service.remove_reservation(1, 2)
        
        assert result is True
        reservation_service.rep_wish.update.assert_called_once_with(1, {"is_booked": False})
    
    @pytest.mark.asyncio
    async def test_remove_reservation_not_found(self, reservation_service):
        """Test removing non-existent reservation."""
        reservation_service.rep_reservation.delete_reservation_idx = AsyncMock(return_value=False)
        
        result = await reservation_service.remove_reservation(1, 2)
        
        assert result is False
    
    @pytest.mark.asyncio
    async def test_remove_reservation_connection_not_found(self, reservation_service):
        """Test removing reservation when connection not found."""
        reservation_service.rep_reservation.delete_reservation_idx = AsyncMock(return_value=True)
        reservation_service.rep_wish_wishlist.get_by_id = AsyncMock(return_value=None)
        
        result = await reservation_service.remove_reservation(1, 2)
        
        assert result is True
        reservation_service.rep_wish.update.assert_not_called()
    
    @pytest.mark.asyncio
    async def test_remove_reservation_exception(self, reservation_service):
        """Test exception handling when removing reservation."""
        reservation_service.rep_reservation.delete_reservation_idx = AsyncMock(side_effect=Exception("DB error"))
        
        result = await reservation_service.remove_reservation(1, 2)
        
        assert result is False
        reservation_service.session.rollback.assert_called_once()

    # ==================== get_user_reservation ====================
    @pytest.mark.asyncio
    async def test_get_user_reservation_success(self, reservation_service):
        """Test getting user's reservations."""
        mock_reservation = self.create_mock_reservation(1, 1, 2)
        reservation_service.rep_reservation.get_user_reservations = AsyncMock(return_value=[mock_reservation])
        
        result = await reservation_service.get_user_reservation(2)
        
        assert len(result) == 1
        assert result[0].wish_wishlist_id == 1
    
    @pytest.mark.asyncio
    async def test_get_user_reservation_empty(self, reservation_service):
        """Test getting empty user reservations."""
        reservation_service.rep_reservation.get_user_reservations = AsyncMock(return_value=[])
        
        result = await reservation_service.get_user_reservation(2)
        
        assert result == []
    
    @pytest.mark.asyncio
    async def test_get_user_reservation_with_limit(self, reservation_service):
        """Test getting user's reservations with limit."""
        mock_reservation = self.create_mock_reservation(1, 1, 2)
        reservation_service.rep_reservation.get_user_reservations = AsyncMock(return_value=[mock_reservation])
        
        result = await reservation_service.get_user_reservation(2, limit=20)
        
        reservation_service.rep_reservation.get_user_reservations.assert_called_with(user_id=2, limit=20)
        assert len(result) == 1

    # ==================== get_wish_reservation ====================
    @pytest.mark.asyncio
    async def test_get_wish_reservation_success(self, reservation_service):
        """Test getting reservations for a wish."""
        mock_reservation = self.create_mock_reservation(1, 1, 2)
        reservation_service.rep_reservation.get_reservations_by_wish_wishlist = AsyncMock(return_value=[mock_reservation])
        
        result = await reservation_service.get_wish_reservation(1)
        
        assert len(result) == 1
        assert result[0].wish_wishlist_id == 1
    
    @pytest.mark.asyncio
    async def test_get_wish_reservation_empty(self, reservation_service):
        """Test getting empty wish reservations."""
        reservation_service.rep_reservation.get_reservations_by_wish_wishlist = AsyncMock(return_value=[])
        
        result = await reservation_service.get_wish_reservation(1)
        
        assert result == []
    
    @pytest.mark.asyncio
    async def test_get_wish_reservation_with_limit(self, reservation_service):
        """Test getting wish reservations with limit."""
        mock_reservation = self.create_mock_reservation(1, 1, 2)
        reservation_service.rep_reservation.get_reservations_by_wish_wishlist = AsyncMock(return_value=[mock_reservation])
        
        result = await reservation_service.get_wish_reservation(1, limit=20)
        
        reservation_service.rep_reservation.get_reservations_by_wish_wishlist.assert_called_with(
            wish_wishlist_id=1, limit=20
        )
        assert len(result) == 1