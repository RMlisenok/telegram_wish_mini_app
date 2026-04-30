import pytest
from unittest.mock import AsyncMock, MagicMock
from datetime import datetime
from app.services.subscription_service import SubscriptionService
from app.models.user import User
from app.models.wishlist import Wishlist, TypePrivacyEnum
from app.models.subscription import Subscription


class TestSubscriptionService:
    """Test suite for SubscriptionService."""
    
    @pytest.fixture
    def subscription_service(self, mock_db_session) -> SubscriptionService:
        """Create SubscriptionService instance."""
        service = SubscriptionService(mock_db_session)
        service.rep_subs = AsyncMock()
        service.rep_user = AsyncMock()
        service.rep_wishlist = AsyncMock()
        service.rep_wish_wishlist = AsyncMock()
        return service
    
    @pytest.fixture
    def sample_user(self):
        """Create sample user."""
        user = MagicMock(spec=User)
        user.id = 1
        user.name = "Test User"
        user.telegram_id = 123456789
        user.birth_date = datetime.now().date()
        user.photo = "https://example.com/photo.jpg"
        return user
    
    @pytest.fixture
    def sample_wishlist(self):
        """Create sample wishlist."""
        wishlist = MagicMock(spec=Wishlist)
        wishlist.id = 1
        wishlist.name = "Test Wishlist"
        wishlist.user_id = 1
        wishlist.typeprivacy = TypePrivacyEnum.public
        return wishlist
    
    
    @pytest.mark.asyncio
    async def test_subscribe_to_user_success(self, subscription_service, sample_user):
        """Test successfully subscribing to a user."""
        subscription_service.rep_user.get_user_by_id = AsyncMock(return_value=sample_user)
        subscription_service.rep_subs.get_subscription = AsyncMock(return_value=None)
        subscription_service.rep_subs.create = AsyncMock(return_value=MagicMock())
        
        result = await subscription_service.subscribe_to_user(2, 1)
        
        assert result is True
        subscription_service.rep_subs.create.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_subscribe_to_user_self(self, subscription_service):
        """Test subscribing to yourself."""
        result = await subscription_service.subscribe_to_user(1, 1)
        
        assert result is False
        subscription_service.rep_subs.create.assert_not_called()
    
    @pytest.mark.asyncio
    async def test_subscribe_to_user_not_found(self, subscription_service):
        """Test subscribing to non-existent user."""
        subscription_service.rep_user.get_user_by_id = AsyncMock(return_value=None)
        
        result = await subscription_service.subscribe_to_user(2, 999)
        
        assert result is False
    
    @pytest.mark.asyncio
    async def test_subscribe_to_user_already_subscribed(self, subscription_service, sample_user):
        """Test subscribing to already subscribed user."""
        subscription_service.rep_user.get_user_by_id = AsyncMock(return_value=sample_user)
        subscription_service.rep_subs.get_subscription = AsyncMock(return_value=MagicMock())
        
        result = await subscription_service.subscribe_to_user(2, 1)
        
        assert result is False
    
    
    @pytest.mark.asyncio
    async def test_subscribe_to_wishlist_success(self, subscription_service, sample_wishlist):
        """Test successfully subscribing to a wishlist."""
        subscription_service.rep_wishlist.get = AsyncMock(return_value=sample_wishlist)
        subscription_service.rep_subs.get_subscription = AsyncMock(return_value=None)
        subscription_service.rep_subs.create = AsyncMock(return_value=MagicMock())
        
        result = await subscription_service.subscribe_to_wishlist(2, 1)
        
        assert result is True
    
    @pytest.mark.asyncio
    async def test_subscribe_to_wishlist_not_found(self, subscription_service):
        """Test subscribing to non-existent wishlist."""
        subscription_service.rep_wishlist.get = AsyncMock(return_value=None)
        
        result = await subscription_service.subscribe_to_wishlist(2, 999)
        
        assert result is False
    
    @pytest.mark.asyncio
    async def test_subscribe_to_own_wishlist(self, subscription_service, sample_wishlist):
        """Test subscribing to own wishlist."""
        sample_wishlist.user_id = 2
        subscription_service.rep_wishlist.get = AsyncMock(return_value=sample_wishlist)
        
        result = await subscription_service.subscribe_to_wishlist(2, 1)
        
        assert result is False
    
    @pytest.mark.asyncio
    async def test_subscribe_to_wishlist_already_subscribed(self, subscription_service, sample_wishlist):
        """Test subscribing to already subscribed wishlist."""
        subscription_service.rep_wishlist.get = AsyncMock(return_value=sample_wishlist)
        subscription_service.rep_subs.get_subscription = AsyncMock(return_value=MagicMock())
        
        result = await subscription_service.subscribe_to_wishlist(2, 1)
        
        assert result is False
    
    
    @pytest.mark.asyncio
    async def test_unsubscribe_from_user_success(self, subscription_service):
        """Test successfully unsubscribing from a user."""
        subscription_service.rep_subs.delete_by_target = AsyncMock(return_value=True)
        
        result = await subscription_service.unsubscribe_from_user(2, 1)
        
        assert result is True
        subscription_service.rep_subs.delete_by_target.assert_called_once_with(
            subscriber_id=2, type_sub=True, target_user_id=1
        )
    
    @pytest.mark.asyncio
    async def test_unsubscribe_from_wishlist_success(self, subscription_service):
        """Test successfully unsubscribing from a wishlist."""
        subscription_service.rep_subs.delete_by_target = AsyncMock(return_value=True)
        
        result = await subscription_service.unsubscribe_from_wishlist(2, 1)
        
        assert result is True
    
    
    @pytest.mark.asyncio
    async def test_get_my_subscription_with_users_and_wishlists(self, subscription_service, sample_user, sample_wishlist):
        """Test getting subscriptions with both users and wishlists."""
        mock_sub_user = MagicMock()
        mock_sub_user.type_sub = True
        mock_sub_user.target_user = sample_user
        mock_sub_user.created_at = datetime.now()
        mock_sub_user.updated_at = datetime.now()
        
        mock_sub_wishlist = MagicMock()
        mock_sub_wishlist.type_sub = False
        mock_sub_wishlist.target_wishlist = sample_wishlist
        mock_sub_wishlist.created_at = datetime.now()
        mock_sub_wishlist.updated_at = datetime.now()
        
        subscription_service.rep_subs.get_user_subscription = AsyncMock(return_value=[mock_sub_user, mock_sub_wishlist])
        subscription_service.rep_subs.count_user_subscriptions = AsyncMock(return_value=2)
        subscription_service.rep_wish_wishlist.count_wishes_in_wishlist = AsyncMock(return_value=5)
        
        result = await subscription_service.get_my_subscription(1)
        
        assert result.total == 2
        assert len(result.subscriptions) == 2
    
    @pytest.mark.asyncio
    async def test_get_my_subscription_empty(self, subscription_service):
        """Test getting empty subscriptions."""
        subscription_service.rep_subs.get_user_subscription = AsyncMock(return_value=[])
        subscription_service.rep_subs.count_user_subscriptions = AsyncMock(return_value=0)
        
        result = await subscription_service.get_my_subscription(1)
        
        assert result.total == 0
        assert len(result.subscriptions) == 0
    
    @pytest.mark.asyncio
    async def test_get_my_user_subscriptions_only(self, subscription_service, sample_user):
        """Test getting only user subscriptions."""
        mock_sub = MagicMock()
        mock_sub.type_sub = True
        mock_sub.target_user = sample_user
        mock_sub.created_at = datetime.now()
        mock_sub.updated_at = datetime.now()
        
        subscription_service.rep_subs.get_user_subscription = AsyncMock(return_value=[mock_sub])
        subscription_service.rep_subs.count_user_subscriptions = AsyncMock(return_value=1)
        
        result = await subscription_service.get_my_user_subscriptions(1)
        
        assert result.total == 1
        assert result.subscriptions[0]["type"] == "user"
    
    @pytest.mark.asyncio
    async def test_get_my_wishlist_subscriptions_only(self, subscription_service, sample_wishlist):
        """Test getting only wishlist subscriptions."""
        mock_sub = MagicMock()
        mock_sub.type_sub = False
        mock_sub.target_wishlist = sample_wishlist
        mock_sub.created_at = datetime.now()
        mock_sub.updated_at = datetime.now()
        
        subscription_service.rep_subs.get_user_subscription = AsyncMock(return_value=[mock_sub])
        subscription_service.rep_subs.count_user_subscriptions = AsyncMock(return_value=1)
        subscription_service.rep_wish_wishlist.count_wishes_in_wishlist = AsyncMock(return_value=5)
        
        result = await subscription_service.get_my_wishlist_subscriptions(1)
        
        assert result.total == 1
        assert result.subscriptions[0]["type"] == "wishlist"
    
    
    @pytest.mark.asyncio
    async def test_get_user_subscribers_success(self, subscription_service, sample_user):
        """Test getting user's subscribers."""
        mock_sub = MagicMock()
        mock_sub.subscriber = sample_user
        mock_sub.created_at = datetime.now()
        mock_sub.updated_at = datetime.now()
        
        subscription_service.rep_subs.get_user_subscribers = AsyncMock(return_value=[mock_sub])
        
        result = await subscription_service.get_user_subscribers(1)
        
        assert result.total == 1
        assert len(result.subscribers) == 1
    
    @pytest.mark.asyncio
    async def test_get_user_subscribers_empty(self, subscription_service):
        """Test getting empty subscribers."""
        subscription_service.rep_subs.get_user_subscribers = AsyncMock(return_value=[])
        
        result = await subscription_service.get_user_subscribers(1)
        
        assert result.total == 0
        assert len(result.subscribers) == 0
    
    
    @pytest.mark.asyncio
    async def test_check_user_subscription_true(self, subscription_service):
        """Test checking existing user subscription."""
        subscription_service.rep_subs.get_subscription = AsyncMock(return_value=MagicMock())
        
        result = await subscription_service.check_user_subscription(2, 1)
        
        assert result is True
    
    @pytest.mark.asyncio
    async def test_check_user_subscription_false(self, subscription_service):
        """Test checking non-existent user subscription."""
        subscription_service.rep_subs.get_subscription = AsyncMock(return_value=None)
        
        result = await subscription_service.check_user_subscription(2, 1)
        
        assert result is False
    
    @pytest.mark.asyncio
    async def test_check_wishlist_subscription_true(self, subscription_service):
        """Test checking existing wishlist subscription."""
        subscription_service.rep_subs.get_subscription = AsyncMock(return_value=MagicMock())
        
        result = await subscription_service.check_wishlist_subscription(2, 1)
        
        assert result is True
    
    @pytest.mark.asyncio
    async def test_check_wishlist_subscription_false(self, subscription_service):
        """Test checking non-existent wishlist subscription."""
        subscription_service.rep_subs.get_subscription = AsyncMock(return_value=None)
        
        result = await subscription_service.check_wishlist_subscription(2, 1)
        
        assert result is False
    
    
    @pytest.mark.asyncio
    async def test_update_visit_success(self, subscription_service):
        """Test successfully updating visit timestamp."""
        from app.schemas.subscription import SubscribersVisitUpdate
        from datetime import datetime
        
        mock_update = SubscribersVisitUpdate(
            status=True,
            updated_at=datetime.now()
        )
        subscription_service.rep_subs.update = AsyncMock(return_value=mock_update)
        
        result = await subscription_service.update_visit(1, 1)
        
        assert result is not None
        assert result.status is True
    
    
    @pytest.mark.asyncio
    async def test_get_user_subscriptions_private(self, subscription_service, sample_user):
        """Test getting subscriptions when user has private subscriptions."""
        sample_user.show_sub = False
        subscription_service.rep_user.get_user_by_id = AsyncMock(return_value=sample_user)
        
        with pytest.raises(ValueError, match="User's subscriptions are private"):
            await subscription_service.get_user_subscriptions(1, 999)
    
    @pytest.mark.asyncio
    async def test_get_user_subscriptions_own_profile(self, subscription_service, sample_user):
        """Test getting subscriptions for own profile."""
        sample_user.show_sub = False
        subscription_service.rep_user.get_user_by_id = AsyncMock(return_value=sample_user)
        subscription_service.rep_subs.get_user_subscription = AsyncMock(return_value=[])
        subscription_service.rep_subs.count_user_subscriptions = AsyncMock(return_value=0)
        
        result = await subscription_service.get_user_subscriptions(1, 1)
        
        assert result.total == 0
    
    @pytest.mark.asyncio
    async def test_get_user_subscriptions_user_not_found(self, subscription_service):
        """Test getting subscriptions for non-existent user."""
        subscription_service.rep_user.get_user_by_id = AsyncMock(return_value=None)
        
        with pytest.raises(ValueError, match="User not found"):
            await subscription_service.get_user_subscriptions(999, 1)