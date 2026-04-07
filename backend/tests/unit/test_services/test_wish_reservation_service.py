# tests/unit/test_services/test_wish_reservation_service.py
import pytest
from unittest.mock import AsyncMock, MagicMock
from datetime import datetime
from app.services.wish_reservation_service import ReservationService
from app.models.wish_reservation import WishReservation
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
    
    @pytest.mark.asyncio
    async def test_get_reservation_success(self, reservation_service, wish_reservation_data):
        """Test successfully getting a reservation."""
        # Arrange
        reservation = WishReservation(**wish_reservation_data)
        reservation_service.rep_reservation.get = AsyncMock(return_value=reservation)
        
        # Act
        result = await reservation_service.get_reservation(1)
        
        # Assert
        assert result is not None
        # Исправлено: используем wish_wishlist_id вместо id
        assert result.wish_wishlist_id == 1
        assert result.reserved_by_id == 2
    
    @pytest.mark.asyncio
    async def test_get_reservation_not_found(self, reservation_service):
        """Test getting non-existent reservation."""
        # Arrange
        reservation_service.rep_reservation.get = AsyncMock(return_value=None)
        
        # Act
        result = await reservation_service.get_reservation(999)
        
        # Assert
        assert result is None
    
    @pytest.mark.asyncio
    async def test_create_reservation_success(self, reservation_service, wish_reservation_data, wish_wishlist_data):
        """Test successfully creating a reservation."""
        # Arrange
        reservation_create = ReservationCreate(wish_wishlist_id=1)
        reservation_service.rep_reservation.check_wish_reservation = AsyncMock(return_value=False)
        
        connection = MagicMock()
        connection.wish_id = 1
        reservation_service.rep_wish_wishlist.get_by_id = AsyncMock(return_value=connection)
        
        reservation = WishReservation(**wish_reservation_data)
        reservation_service.rep_reservation.create = AsyncMock(return_value=reservation)
        reservation_service.rep_wish.update = AsyncMock(return_value=True)
        
        # Act
        result = await reservation_service.create_reservation(2, reservation_create)
        
        # Assert
        assert result is not None
        # Исправлено: используем wish_wishlist_id вместо id
        assert result.wish_wishlist_id == 1
        assert result.reserved_by_id == 2
        reservation_service.rep_wish.update.assert_called_once_with(1, {"is_booked": True})
    
    @pytest.mark.asyncio
    async def test_create_reservation_already_reserved(self, reservation_service):
        """Test creating reservation for already reserved wish."""
        # Arrange
        reservation_create = ReservationCreate(wish_wishlist_id=1)
        reservation_service.rep_reservation.check_wish_reservation = AsyncMock(return_value=True)
        
        # Act
        result = await reservation_service.create_reservation(2, reservation_create)
        
        # Assert
        assert result is None
    
    @pytest.mark.asyncio
    async def test_remove_reservation_success(self, reservation_service, wish_wishlist_data):
        """Test successfully removing a reservation."""
        # Arrange
        reservation_service.rep_reservation.delete_reservation_idx = AsyncMock(return_value=True)
        
        connection = MagicMock()
        connection.wish_id = 1
        reservation_service.rep_wish_wishlist.get_by_id = AsyncMock(return_value=connection)
        reservation_service.rep_wish.update = AsyncMock(return_value=True)
        
        # Act
        result = await reservation_service.remove_reservation(1, 2)
        
        # Assert
        assert result is True
        reservation_service.rep_wish.update.assert_called_once_with(1, {"is_booked": False})
    
    @pytest.mark.asyncio
    async def test_get_user_reservation(self, reservation_service, wish_reservation_data):
        """Test getting user's reservations."""
        # Arrange
        reservation = WishReservation(**wish_reservation_data)
        reservation_service.rep_reservation.get_user_reservations = AsyncMock(return_value=[reservation])
        
        # Act
        result = await reservation_service.get_user_reservation(2)
        
        # Assert
        assert len(result) == 1
        # Исправлено: используем wish_wishlist_id вместо id
        assert result[0].wish_wishlist_id == 1
    
    @pytest.mark.asyncio
    async def test_get_wish_reservation(self, reservation_service, wish_reservation_data):
        """Test getting reservations for a wish."""
        # Arrange
        reservation = WishReservation(**wish_reservation_data)
        reservation_service.rep_reservation.get_reservations_by_wish_wishlist = AsyncMock(return_value=[reservation])
        
        # Act
        result = await reservation_service.get_wish_reservation(1)
        
        # Assert
        assert len(result) == 1
        assert result[0].wish_wishlist_id == 1