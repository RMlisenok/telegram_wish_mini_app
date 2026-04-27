import pytest
from unittest.mock import AsyncMock, MagicMock
from datetime import datetime
from app.services.wish_service import WishService
from app.schemas.wish import WishCreate, WishUpdate


class TestWishService:
    """Test suite for WishService."""
    
    @pytest.fixture
    def wish_service(self, mock_db_session) -> WishService:
        service = WishService(mock_db_session)
        service.rep_wish = AsyncMock()
        service.rep_wish_wishlist = AsyncMock()
        return service

    def create_mock_wish(self, id=1, user_id=1, name="Test Wish"):
        mock = MagicMock()
        mock.id = id
        mock.user_id = user_id
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

    def create_mock_wishlist(self, id=1, name="Test Wishlist"):
        mock = MagicMock()
        mock.id = id
        mock.name = name
        return mock

    @pytest.mark.asyncio
    async def test_get_wish_success(self, wish_service):
        mock_wish = self.create_mock_wish(1, 1, "Test Wish")
        wish_service.rep_wish.get = AsyncMock(return_value=mock_wish)

        result = await wish_service.get_wish(1)

        assert result is not None
        assert result.id == 1
        assert result.name == "Test Wish"

    @pytest.mark.asyncio
    async def test_get_wish_not_found(self, wish_service):
        wish_service.rep_wish.get = AsyncMock(return_value=None)

        result = await wish_service.get_wish(999)

        assert result is None

    @pytest.mark.asyncio
    async def test_get_wish_with_wishlists_info(self, wish_service):
        mock_wish = self.create_mock_wish(1, 1, "Test Wish")
        mock_wishlist = self.create_mock_wishlist(1, "Test Wishlist")

        connection = MagicMock()
        connection.wishlist = mock_wishlist

        wish_service.rep_wish.get = AsyncMock(return_value=mock_wish)
        wish_service.rep_wish_wishlist.get_wish_from_all_wishlist = AsyncMock(return_value=[connection])

        result = await wish_service.get_wish_with_wishlists_info(1)

        assert result is not None
        assert result.id == 1
        assert len(result.wishlists) == 1
        assert result.wishlists[0]["name"] == "Test Wishlist"

    @pytest.mark.asyncio
    async def test_get_wish_with_wishlists_info_no_wish(self, wish_service):
        wish_service.rep_wish.get = AsyncMock(return_value=None)

        result = await wish_service.get_wish_with_wishlists_info(999)

        assert result is None

    @pytest.mark.asyncio
    async def test_create_wish_success(self, wish_service):
        wish_create = WishCreate(
            name="New Wish",
            photo=None,
            url_gift="https://example.com/gift",
            price=100.0,
            currency="RUB",
            description="Description"
        )
        mock_wish = self.create_mock_wish(1, 1, "New Wish")
        wish_service.rep_wish.create = AsyncMock(return_value=mock_wish)

        result = await wish_service.create_wish(1, wish_create)

        assert result is not None
        assert result.name == "New Wish"

    @pytest.mark.asyncio
    async def test_create_wish_with_default_photo(self, wish_service):
        wish_create = WishCreate(
            name="New Wish",
            photo=None,
            url_gift="https://example.com/gift",
            price=100.0,
            currency="RUB",
            description="Description"
        )
        mock_wish = self.create_mock_wish(1, 1, "New Wish")
        mock_wish.photo = "https://e4a6ce86-682d-4bf7-921e-9a1f5c537501.selstorage.ru/d118dd34-8236-4e18-b22e-d7f03c1992c6.png"
        wish_service.rep_wish.create = AsyncMock(return_value=mock_wish)

        result = await wish_service.create_wish(1, wish_create)

        assert result is not None
        assert "selstorage.ru" in result.photo

    @pytest.mark.asyncio
    async def test_create_wish_with_custom_photo(self, wish_service):
        wish_create = WishCreate(
            name="New Wish",
            photo="https://example.com/custom.jpg",
            url_gift="https://example.com/gift",
            price=100.0,
            currency="RUB",
            description="Description"
        )
        mock_wish = self.create_mock_wish(1, 1, "New Wish")
        mock_wish.photo = "https://example.com/custom.jpg"
        wish_service.rep_wish.create = AsyncMock(return_value=mock_wish)

        result = await wish_service.create_wish(1, wish_create)

        assert result is not None
        assert result.photo == "https://example.com/custom.jpg"

    @pytest.mark.asyncio
    async def test_update_wish_success(self, wish_service):
        wish_update = WishUpdate(name="Updated Wish")
        mock_wish = self.create_mock_wish(1, 1, "Updated Wish")
        wish_service.rep_wish.update = AsyncMock(return_value=mock_wish)
        wish_service.get_wish = AsyncMock(return_value=mock_wish)

        result = await wish_service.update_wish(1, wish_update)

        assert result is not None
        assert result.name == "Updated Wish"

    @pytest.mark.asyncio
    async def test_update_wish_with_photo(self, wish_service):
        wish_update = WishUpdate(
            name="Updated Wish",
            photo="https://example.com/new-photo.jpg"
        )
        mock_wish = self.create_mock_wish(1, 1, "Updated Wish")
        mock_wish.photo = "https://example.com/new-photo.jpg"
        wish_service.rep_wish.update = AsyncMock(return_value=mock_wish)
        wish_service.get_wish = AsyncMock(return_value=mock_wish)

        result = await wish_service.update_wish(1, wish_update)

        assert result is not None
        assert result.photo == "https://example.com/new-photo.jpg"

    @pytest.mark.asyncio
    async def test_update_wish_not_found(self, wish_service):
        wish_update = WishUpdate(name="Updated Wish")
        wish_service.rep_wish.update = AsyncMock(return_value=None)

        result = await wish_service.update_wish(999, wish_update)

        assert result is None

    @pytest.mark.asyncio
    async def test_delete_wish_success(self, wish_service):
        wish_service.rep_wish.delete = AsyncMock(return_value=True)

        result = await wish_service.delete_wish(1)

        assert result is True
        wish_service.session.commit.assert_called_once()

    @pytest.mark.asyncio
    async def test_delete_wish_failure(self, wish_service):
        wish_service.rep_wish.delete = AsyncMock(return_value=False)

        result = await wish_service.delete_wish(1)

        assert result is False
        wish_service.session.commit.assert_not_called()

    @pytest.mark.asyncio
    async def test_delete_wish_in_wishlists_success(self, wish_service):
        mock_wish = self.create_mock_wish(1, 1, "Test Wish")
        wish_service.get_wish = AsyncMock(return_value=mock_wish)
        wish_service.rep_wish_wishlist.delete_wish_in_wishlists = AsyncMock(return_value=1)

        result = await wish_service.delete_wish_in_wishlists(1)

        assert result is True

    @pytest.mark.asyncio
    async def test_delete_wish_in_wishlists_wish_not_found(self, wish_service):
        wish_service.get_wish = AsyncMock(return_value=None)

        result = await wish_service.delete_wish_in_wishlists(999)

        assert result is False

    @pytest.mark.asyncio
    async def test_delete_wish_in_wishlists_exception(self, wish_service):
        mock_wish = self.create_mock_wish(1, 1, "Test Wish")
        wish_service.get_wish = AsyncMock(return_value=mock_wish)
        wish_service.rep_wish_wishlist.delete_wish_in_wishlists = AsyncMock(side_effect=Exception("DB error"))

        result = await wish_service.delete_wish_in_wishlists(1)

        assert result is False

    @pytest.mark.asyncio
    async def test_get_user_wish_success(self, wish_service):
        mock_wish = self.create_mock_wish(1, 1, "Test Wish")
        wish_service.rep_wish.get_user_wish = AsyncMock(return_value=[mock_wish])

        result = await wish_service.get_user_wish(1)

        assert len(result) == 1
        assert result[0].name == "Test Wish"

    @pytest.mark.asyncio
    async def test_get_user_wish_empty(self, wish_service):
        wish_service.rep_wish.get_user_wish = AsyncMock(return_value=[])

        result = await wish_service.get_user_wish(1)

        assert result == []

    @pytest.mark.asyncio
    async def test_get_user_wish_with_limit(self, wish_service):
        mock_wish = self.create_mock_wish(1, 1, "Test Wish")
        wish_service.rep_wish.get_user_wish = AsyncMock(return_value=[mock_wish])

        result = await wish_service.get_user_wish(1, is_desc=True, limit=20)

        wish_service.rep_wish.get_user_wish.assert_called_with(1, True, 20)
        assert len(result) == 1

    @pytest.mark.asyncio
    async def test_get_user_wish_sorted_success(self, wish_service):
        mock_wish = self.create_mock_wish(1, 1, "Test Wish")
        wish_service.rep_wish.get_user_wish_sorted = AsyncMock(return_value=[mock_wish])

        result = await wish_service.get_user_wish_sorted(1, is_finish=True)

        assert len(result) == 1

    @pytest.mark.asyncio
    async def test_get_user_wish_sorted_empty(self, wish_service):
        wish_service.rep_wish.get_user_wish_sorted = AsyncMock(return_value=[])

        result = await wish_service.get_user_wish_sorted(1, is_finish=False)

        assert result == []