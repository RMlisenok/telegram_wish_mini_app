# tests/unit/test_services/test_wish_service.py
import pytest
from unittest.mock import AsyncMock, MagicMock
from datetime import datetime
from app.services.wish_service import WishService
from app.models.wish import Wish
from app.schemas.wish import WishCreate, WishUpdate


class TestWishService:
    """Test suite for WishService."""
    
    @pytest.fixture
    def wish_service(self, mock_db_session) -> WishService:
        """Create WishService instance with mocked dependencies."""
        service = WishService(mock_db_session)
        service.rep_wish = AsyncMock()
        service.rep_wish_wishlist = AsyncMock()
        return service
    
    @pytest.mark.asyncio
    async def test_get_wish_success(self, wish_service, wish_data_1):
        """Test successfully getting a wish."""
        # Arrange
        wish = Wish(**wish_data_1)
        wish_service.rep_wish.get = AsyncMock(return_value=wish)
        
        # Act
        result = await wish_service.get_wish(1)
        
        # Assert
        assert result is not None
        assert result.id == 1
        assert result.name == wish_data_1["name"]
    
    @pytest.mark.asyncio
    async def test_get_wish_not_found(self, wish_service):
        """Test getting non-existent wish."""
        # Arrange
        wish_service.rep_wish.get = AsyncMock(return_value=None)
        
        # Act
        result = await wish_service.get_wish(999)
        
        # Assert
        assert result is None
    
    @pytest.mark.asyncio
    async def test_get_wish_with_wishlists_info(self, wish_service, wish_data_1, wishlist_data_1):
        """Test getting wish with wishlist information."""
        # Arrange
        from app.models.wish import Wish
        from app.models.wishlist import Wishlist
        from app.models.wish_wishlist import WishWishlist
        
        wish = Wish(**wish_data_1)
        wishlist = Wishlist(**wishlist_data_1)
        connection = MagicMock()
        connection.wishlist = wishlist
        
        wish_service.rep_wish.get = AsyncMock(return_value=wish)
        wish_service.rep_wish_wishlist.get_wish_from_all_wishlist = AsyncMock(return_value=[connection])
        
        # Act
        result = await wish_service.get_wish_with_wishlists_info(1)
        
        # Assert
        assert result is not None
        assert result.id == 1
        assert len(result.wishlists) == 1
    
    @pytest.mark.asyncio
    async def test_create_wish_success(self, wish_service, wish_data_1):
        """Test successfully creating a wish."""
        # Arrange
        wish_create = WishCreate(
            name="New Wish",
            photo=None,
            url_gift="https://example.com/gift",
            price=100.0,
            currency="RUB",
            description="Description"
        )
        created_wish = Wish(**wish_data_1)
        wish_service.rep_wish.create = AsyncMock(return_value=created_wish)
        
        # Act
        result = await wish_service.create_wish(1, wish_create)
        
        # Assert
        assert result is not None
        assert result.name == wish_data_1["name"]
    
    @pytest.mark.asyncio
    async def test_update_wish_success(self, wish_service, wish_data_1):
        """Test successfully updating a wish."""
        # Arrange
        wish_update = WishUpdate(name="Updated Wish")
        updated_wish = Wish(**wish_data_1)
        updated_wish.name = "Updated Wish"
        wish_service.rep_wish.update = AsyncMock(return_value=updated_wish)
        wish_service.get_wish = AsyncMock(return_value=updated_wish)
        
        # Act
        result = await wish_service.update_wish(1, wish_update)
        
        # Assert
        assert result is not None
        assert result.name == "Updated Wish"
    
    @pytest.mark.asyncio
    async def test_delete_wish_success(self, wish_service):
        """Test successfully deleting a wish."""
        # Arrange
        wish_service.rep_wish.delete = AsyncMock(return_value=True)
        
        # Act
        result = await wish_service.delete_wish(1)
        
        # Assert
        assert result is True
        wish_service.session.commit.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_delete_wish_in_wishlists_success(self, wish_service, wish_data_1):
        """Test successfully deleting wish from all wishlists."""
        # Arrange
        wish = Wish(**wish_data_1)
        wish_service.get_wish = AsyncMock(return_value=wish)
        wish_service.rep_wish_wishlist.delete_wish_in_wishlists = AsyncMock(return_value=1)
        
        # Act
        result = await wish_service.delete_wish_in_wishlists(1)
        
        # Assert
        assert result is True
    
    @pytest.mark.asyncio
    async def test_get_user_wish(self, wish_service, wish_data_1):
        """Test getting user's wishes."""
        # Arrange
        wish = Wish(**wish_data_1)
        wish_service.rep_wish.get_user_wish = AsyncMock(return_value=[wish])
        
        # Act
        result = await wish_service.get_user_wish(1)
        
        # Assert
        assert len(result) == 1
        assert result[0].name == wish_data_1["name"]
    
    @pytest.mark.asyncio
    async def test_get_user_wish_sorted(self, wish_service, wish_data_1):
        """Test getting user's wishes sorted by status."""
        # Arrange
        wish = Wish(**wish_data_1)
        wish_service.rep_wish.get_user_wish_sorted = AsyncMock(return_value=[wish])
        
        # Act
        result = await wish_service.get_user_wish_sorted(1, is_finish=True)
        
        # Assert
        assert len(result) == 1