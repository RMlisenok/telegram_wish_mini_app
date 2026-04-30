import pytest
from unittest.mock import AsyncMock, MagicMock
from datetime import datetime
from app.services.wishlist_service import WishlistService
from app.schemas.wishlist import WishlistCreate, WishlistUpdate


class TestWishlistService:
    """Test suite for WishlistService."""
    
    @pytest.fixture
    def wishlist_service(self, mock_db_session) -> WishlistService:
        service = WishlistService(mock_db_session)
        service.rep_wishlist = AsyncMock()
        service.rep_wish_wishlist = AsyncMock()
        return service

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

    def create_mock_wish(self, id=1, name="Test Wish"):
        mock = MagicMock()
        mock.id = id
        mock.name = name
        mock.photo = "https://example.com/wish.jpg"
        mock.url_gift = "https://example.com/gift"
        mock.price = 100.0
        mock.currency = "RUB"
        mock.description = "Description"
        mock.is_booked = False
        mock.status_is_finished = False
        mock.created_at = datetime.now()
        mock.updated_at = datetime.now()
        return mock

    def create_mock_connection(self, id=1, wish_id=1, wishlist_id=1):
        mock = MagicMock()
        mock.id = id
        mock.wish_id = wish_id
        mock.wishlist_id = wishlist_id
        mock.is_pinned = False
        mock.order_position = 0
        mock.created_at = datetime.now()
        mock.updated_at = datetime.now()
        mock.wish = self.create_mock_wish(wish_id)
        mock.wishlist = self.create_mock_wishlist(wishlist_id)
        return mock

    @pytest.mark.asyncio
    async def test_get_wishlist_success(self, wishlist_service):
        mock_wishlist = self.create_mock_wishlist(1)
        wishlist_service.rep_wishlist.get = AsyncMock(return_value=mock_wishlist)
        wishlist_service.rep_wish_wishlist.count_wishes_in_wishlist = AsyncMock(return_value=5)

        result = await wishlist_service.get_wishlist(1)

        assert result is not None
        assert result.id == 1
        assert result.name == "Test Wishlist"
        assert result.wishes_count == 5

    @pytest.mark.asyncio
    async def test_get_wishlist_not_found(self, wishlist_service):
        wishlist_service.rep_wishlist.get = AsyncMock(return_value=None)

        result = await wishlist_service.get_wishlist(999)

        assert result is None

    @pytest.mark.asyncio
    async def test_create_wishlist_success(self, wishlist_service):
        wishlist_create = WishlistCreate(
            name="New Wishlist",
            description="Description",
            photo=None,
            typeprivacy="public"
        )
        mock_wishlist = self.create_mock_wishlist(1, 1, "New Wishlist")
        wishlist_service.rep_wishlist.create = AsyncMock(return_value=mock_wishlist)

        result = await wishlist_service.create_wishlist(1, wishlist_create)

        assert result is not None
        assert result.name == "New Wishlist"
        assert result.wishes_count == 0

    @pytest.mark.asyncio
    async def test_create_wishlist_with_default_photo(self, wishlist_service):
        wishlist_create = WishlistCreate(
            name="New Wishlist",
            description="Description",
            photo=None,
            typeprivacy="public"
        )
        mock_wishlist = self.create_mock_wishlist(1, 1, "New Wishlist")
        mock_wishlist.photo = "https://e4a6ce86-682d-4bf7-921e-9a1f5c537501.selstorage.ru/9bcb1b11-c7cd-4787-ad2d-60c6b49ce9ca.svg"
        wishlist_service.rep_wishlist.create = AsyncMock(return_value=mock_wishlist)

        result = await wishlist_service.create_wishlist(1, wishlist_create)

        assert result is not None
        assert "selstorage.ru" in result.photo

    @pytest.mark.asyncio
    async def test_create_wishlist_with_custom_photo(self, wishlist_service):
        wishlist_create = WishlistCreate(
            name="Custom Wishlist",
            description="Description",
            photo="https://example.com/custom.jpg",
            typeprivacy="private"
        )
        mock_wishlist = self.create_mock_wishlist(1, 1, "Custom Wishlist")
        mock_wishlist.photo = "https://example.com/custom.jpg"
        wishlist_service.rep_wishlist.create = AsyncMock(return_value=mock_wishlist)

        result = await wishlist_service.create_wishlist(1, wishlist_create)

        assert result is not None
        assert result.photo == "https://example.com/custom.jpg"

    @pytest.mark.asyncio
    async def test_update_wishlist_success(self, wishlist_service):
        wishlist_update = WishlistUpdate(
            name="Updated Name",
            description="Updated description"
        )
        mock_wishlist = self.create_mock_wishlist(1, 1, "Updated Name")
        wishlist_service.rep_wishlist.update = AsyncMock(return_value=mock_wishlist)
        wishlist_service.get_wishlist = AsyncMock(return_value=mock_wishlist)

        result = await wishlist_service.update_wishlist(1, wishlist_update)

        assert result is not None
        assert result.name == "Updated Name"

    @pytest.mark.asyncio
    async def test_update_wishlist_without_photo(self, wishlist_service):
        wishlist_update = WishlistUpdate(
            name="Updated Name",
            description="Updated description",
            photo=None
        )
        mock_wishlist = self.create_mock_wishlist(1, 1, "Updated Name")
        mock_wishlist.photo = "https://e4a6ce86-682d-4bf7-921e-9a1f5c537501.selstorage.ru/9bcb1b11-c7cd-4787-ad2d-60c6b49ce9ca.svg"
        wishlist_service.rep_wishlist.update = AsyncMock(return_value=mock_wishlist)
        wishlist_service.get_wishlist = AsyncMock(return_value=mock_wishlist)

        result = await wishlist_service.update_wishlist(1, wishlist_update)

        assert result is not None
        assert "selstorage.ru" in result.photo

    @pytest.mark.asyncio
    async def test_update_wishlist_with_custom_photo(self, wishlist_service):
        wishlist_update = WishlistUpdate(
            name="Updated Name",
            description="Updated description",
            photo="https://example.com/new-photo.jpg"
        )
        mock_wishlist = self.create_mock_wishlist(1, 1, "Updated Name")
        mock_wishlist.photo = "https://example.com/new-photo.jpg"
        wishlist_service.rep_wishlist.update = AsyncMock(return_value=mock_wishlist)
        wishlist_service.get_wishlist = AsyncMock(return_value=mock_wishlist)

        result = await wishlist_service.update_wishlist(1, wishlist_update)

        assert result is not None
        assert result.photo == "https://example.com/new-photo.jpg"

    @pytest.mark.asyncio
    async def test_update_wishlist_not_found(self, wishlist_service):
        wishlist_update = WishlistUpdate(name="Updated Name", description="Desc")
        wishlist_service.rep_wishlist.update = AsyncMock(return_value=None)

        result = await wishlist_service.update_wishlist(999, wishlist_update)

        assert result is None

    @pytest.mark.asyncio
    async def test_delete_wishlist_success(self, wishlist_service):
        wishlist_service.rep_wishlist.delete = AsyncMock(return_value=True)

        result = await wishlist_service.delete(1)

        assert result is True
        wishlist_service.session.commit.assert_called_once()

    @pytest.mark.asyncio
    async def test_delete_wishlist_failure(self, wishlist_service):
        wishlist_service.rep_wishlist.delete = AsyncMock(return_value=False)

        result = await wishlist_service.delete(1)

        assert result is False
        wishlist_service.session.commit.assert_not_called()

    @pytest.mark.asyncio
    async def test_get_user_wishlist_empty(self, wishlist_service):
        wishlist_service.rep_wishlist.get_user_wishlist = AsyncMock(
            return_value=[]
        )

        result = await wishlist_service.get_user_wishlist(1)

        assert result == []

    @pytest.mark.asyncio
    async def test_get_user_wishlist_with_data(self, wishlist_service):
        mock_wishlist = self.create_mock_wishlist(1)
        wishlist_service.rep_wishlist.get_user_wishlist = AsyncMock(return_value=[mock_wishlist])
        wishlist_service.rep_wish_wishlist.count_wishes_in_wishlist = AsyncMock(return_value=3)

        result = await wishlist_service.get_user_wishlist(1)

        assert len(result) == 1
        assert result[0].wishes_count == 3

    @pytest.mark.asyncio
    async def test_get_user_wishlist_desc_order(self, wishlist_service):
        mock_wishlist = self.create_mock_wishlist(1)
        wishlist_service.rep_wishlist.get_user_wishlist = AsyncMock(return_value=[mock_wishlist])
        wishlist_service.rep_wish_wishlist.count_wishes_in_wishlist = AsyncMock(return_value=3)

        result = await wishlist_service.get_user_wishlist(1, is_desc=True, limit=5)

        wishlist_service.rep_wishlist.get_user_wishlist.assert_called_with(1, True, 5)
        assert len(result) == 1

    @pytest.mark.asyncio
    async def test_get_wishes_from_wishlist_with_data(self, wishlist_service):
        connection = self.create_mock_connection(1, 1, 1)
        wishlist_service.rep_wish_wishlist.get_wishes_from_wishlist = AsyncMock(return_value=[connection])

        result = await wishlist_service.get_wishes_from_wishlist(1)

        assert len(result) == 1
        assert result[0].name == "Test Wish"

    @pytest.mark.asyncio
    async def test_get_wishes_from_wishlist_empty(self, wishlist_service):
        wishlist_service.rep_wish_wishlist.get_wishes_from_wishlist = AsyncMock(return_value=[])

        result = await wishlist_service.get_wishes_from_wishlist(1)

        assert result == []

    @pytest.mark.asyncio
    async def test_get_wishes_from_wishlist_with_limit(self, wishlist_service):
        connection = self.create_mock_connection(1, 1, 1)
        wishlist_service.rep_wish_wishlist.get_wishes_from_wishlist = AsyncMock(return_value=[connection])

        result = await wishlist_service.get_wishes_from_wishlist(1, limit=20)

        wishlist_service.rep_wish_wishlist.get_wishes_from_wishlist.assert_called_with(1, 20)
        assert len(result) == 1

    @pytest.mark.asyncio
    async def test_get_wishes_from_wishlist_with_price_none(self, wishlist_service):
        connection = self.create_mock_connection(1, 1, 1)
        connection.wish.price = None
        wishlist_service.rep_wish_wishlist.get_wishes_from_wishlist = AsyncMock(return_value=[connection])

        result = await wishlist_service.get_wishes_from_wishlist(1)

        assert result[0].price is None

    @pytest.mark.asyncio
    async def test_add_wish_to_wishlist_success(self, wishlist_service):
        connection = self.create_mock_connection(1, 1, 1)
        wishlist_service.rep_wish_wishlist.create_wish_to_wishlist = AsyncMock(return_value=connection)

        result = await wishlist_service.add_wish_to_wishlist(
            MagicMock(wish_id=1, wishlist_id=1, is_pinned=False, order_position=0)
        )

        assert result is not None
        assert result.id == 1

    @pytest.mark.asyncio
    async def test_add_wish_to_wishlist_failure(self, wishlist_service):
        wishlist_service.rep_wish_wishlist.create_wish_to_wishlist = AsyncMock(return_value=None)

        result = await wishlist_service.add_wish_to_wishlist(
            MagicMock(wish_id=1, wishlist_id=1, is_pinned=False, order_position=0)
        )

        assert result is None

    @pytest.mark.asyncio
    async def test_add_wish_to_wishlist_with_pinned_true(self, wishlist_service):
        connection = self.create_mock_connection(1, 1, 1)
        connection.is_pinned = True
        wishlist_service.rep_wish_wishlist.create_wish_to_wishlist = AsyncMock(return_value=connection)

        result = await wishlist_service.add_wish_to_wishlist(
            MagicMock(wish_id=1, wishlist_id=1, is_pinned=True, order_position=1)
        )

        assert result is not None
        assert result.is_pinned is True

    @pytest.mark.asyncio
    async def test_update_wish_in_wishlist_success(self, wishlist_service):
        connection = self.create_mock_connection(1, 1, 1)
        wishlist_service.rep_wish_wishlist.update_connection = AsyncMock(return_value=connection)

        result = await wishlist_service.update_wihs_in_wishlits(
            1, MagicMock(is_pinned=True, order_position=5)
        )

        assert result is not None
        assert result.id == 1

    @pytest.mark.asyncio
    async def test_update_wish_in_wishlist_failure(self, wishlist_service):
        wishlist_service.rep_wish_wishlist.update_connection = AsyncMock(return_value=None)

        result = await wishlist_service.update_wihs_in_wishlits(
            1, MagicMock(is_pinned=True, order_position=5)
        )

        assert result is None

    @pytest.mark.asyncio
    async def test_update_wish_in_wishlist_only_pinned(self, wishlist_service):
        connection = self.create_mock_connection(1, 1, 1)
        connection.is_pinned = True
        wishlist_service.rep_wish_wishlist.update_connection = AsyncMock(return_value=connection)

        result = await wishlist_service.update_wihs_in_wishlits(
            1, MagicMock(is_pinned=True)
        )

        assert result is not None
        assert result.is_pinned is True

    @pytest.mark.asyncio
    async def test_remove_wish_from_wishlist_success(self, wishlist_service):
        wishlist_service.rep_wish_wishlist.remove_wish_from_wishlist = AsyncMock(return_value=True)

        result = await wishlist_service.remove_wish_from_wishlist(1, 1)

        assert result is True

    @pytest.mark.asyncio
    async def test_remove_wish_from_wishlist_failure(self, wishlist_service):
        wishlist_service.rep_wish_wishlist.remove_wish_from_wishlist = AsyncMock(return_value=False)

        result = await wishlist_service.remove_wish_from_wishlist(1, 1)

        assert result is False

    @pytest.mark.asyncio
    async def test_get_wishlist_connection_success(self, wishlist_service):
        connection = self.create_mock_connection(1, 1, 1)
        wishlist_service.rep_wish_wishlist.get_wishlist_from_all_wishes = AsyncMock(return_value=[connection])

        result = await wishlist_service.get_wishlist_connection(1, 10)

        assert result is not None
        assert len(result) == 1
        assert result[0].id == 1

    @pytest.mark.asyncio
    async def test_get_wishlist_connection_empty(self, wishlist_service):
        wishlist_service.rep_wish_wishlist.get_wishlist_from_all_wishes = AsyncMock(return_value=[])

        result = await wishlist_service.get_wishlist_connection(1, 10)

        assert result is None

    @pytest.mark.asyncio
    async def test_get_wishlist_connection_with_limit(self, wishlist_service):
        connection = self.create_mock_connection(1, 1, 1)
        wishlist_service.rep_wish_wishlist.get_wishlist_from_all_wishes = AsyncMock(return_value=[connection])

        result = await wishlist_service.get_wishlist_connection(1, 5)

        wishlist_service.rep_wish_wishlist.get_wishlist_from_all_wishes.assert_called_with(1, 5)
        assert len(result) == 1