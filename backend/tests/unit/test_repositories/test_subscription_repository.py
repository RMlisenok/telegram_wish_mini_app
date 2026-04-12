# tests/unit/test_repositories/test_subscription_repository.py
import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from datetime import datetime
from app.repositories.subscription_repository import SubscriptionRepository
from app.models.subscription import Subscription
from app.schemas.subscription import SubscribersVisitUpdate


class TestSubscriptionRepository:
    """Test suite for SubscriptionRepository."""

    @pytest.fixture
    def repo(self, mock_db_session):
        return SubscriptionRepository(mock_db_session)

    def create_mock_subscription(self, id=1, subscriber_id=2, target_user_id=1, type_sub=True):
        mock = MagicMock(spec=Subscription)
        mock.id = id
        mock.subscriber_id = subscriber_id
        mock.type_sub = type_sub
        mock.target_user_id = target_user_id if type_sub else None
        mock.target_wishlist_id = None if type_sub else 1
        mock.created_at = datetime.now()
        mock.updated_at = datetime.now()
        return mock

    # ==================== create ====================
    @pytest.mark.asyncio
    async def test_create_subscription_success(self, repo, mock_db_session):
        subscription_data = {"subscriber_id": 2, "type_sub": True, "target_user_id": 1}
        mock_subscription = self.create_mock_subscription(1, 2, 1, True)
        mock_db_session.add = MagicMock()
        mock_db_session.commit = AsyncMock()
        mock_db_session.refresh = AsyncMock()

        with patch('app.repositories.subscription_repository.Subscription', return_value=mock_subscription):
            result = await repo.create(subscription_data)

            assert result == mock_subscription
            mock_db_session.add.assert_called_once()
            mock_db_session.commit.assert_called_once()

    @pytest.mark.asyncio
    async def test_create_subscription_exception(self, repo, mock_db_session):
        subscription_data = {"subscriber_id": 2, "type_sub": True, "target_user_id": 1}
        mock_db_session.commit = AsyncMock(side_effect=Exception("DB error"))
        mock_db_session.rollback = AsyncMock()

        result = await repo.create(subscription_data)

        assert result is None
        mock_db_session.rollback.assert_called_once()

    # ==================== get_subscription ====================
    @pytest.mark.asyncio
    async def test_get_subscription_user_type_success(self, repo, mock_db_session):
        mock_subscription = self.create_mock_subscription(1, 2, 1, True)
        mock_result = MagicMock()
        mock_result.scalar_one_or_none = MagicMock(return_value=mock_subscription)
        mock_db_session.execute = AsyncMock(return_value=mock_result)

        result = await repo.get_subscription(2, True, target_user_id=1)

        assert result == mock_subscription

    @pytest.mark.asyncio
    async def test_get_subscription_wishlist_type_success(self, repo, mock_db_session):
        mock_subscription = self.create_mock_subscription(1, 2, None, False)
        mock_subscription.target_wishlist_id = 1
        mock_result = MagicMock()
        mock_result.scalar_one_or_none = MagicMock(return_value=mock_subscription)
        mock_db_session.execute = AsyncMock(return_value=mock_result)

        result = await repo.get_subscription(2, False, target_wishlist_id=1)

        assert result == mock_subscription

    @pytest.mark.asyncio
    async def test_get_subscription_user_type_missing_target(self, repo):
        result = await repo.get_subscription(2, True, target_user_id=None)

        assert result is None

    @pytest.mark.asyncio
    async def test_get_subscription_wishlist_type_missing_target(self, repo):
        result = await repo.get_subscription(2, False, target_wishlist_id=None)

        assert result is None

    @pytest.mark.asyncio
    async def test_get_subscription_not_found(self, repo, mock_db_session):
        mock_result = MagicMock()
        mock_result.scalar_one_or_none = MagicMock(return_value=None)
        mock_db_session.execute = AsyncMock(return_value=mock_result)

        result = await repo.get_subscription(2, True, target_user_id=999)

        assert result is None

    # ==================== delete_by_target ====================
    @pytest.mark.asyncio
    async def test_delete_by_target_success(self, repo, mock_db_session):
        mock_subscription = self.create_mock_subscription(1, 2, 1, True)
        repo.get_subscription = AsyncMock(return_value=mock_subscription)
        mock_db_session.delete = AsyncMock()

        result = await repo.delete_by_target(2, True, target_user_id=1)

        assert result is True
        mock_db_session.delete.assert_called_once()

    @pytest.mark.asyncio
    async def test_delete_by_target_not_found(self, repo, mock_db_session):
        repo.get_subscription = AsyncMock(return_value=None)

        result = await repo.delete_by_target(2, True, target_user_id=999)

        assert result is False

    @pytest.mark.asyncio
    async def test_delete_by_target_exception(self, repo, mock_db_session):
        mock_subscription = self.create_mock_subscription(1, 2, 1, True)
        repo.get_subscription = AsyncMock(return_value=mock_subscription)
        mock_db_session.delete = AsyncMock(side_effect=Exception("DB error"))

        result = await repo.delete_by_target(2, True, target_user_id=1)

        assert result is False

    # ==================== get_user_subscription ====================
    @pytest.mark.asyncio
    async def test_get_user_subscription_all(self, repo, mock_db_session):
        mock_subscriptions = [self.create_mock_subscription(1), self.create_mock_subscription(2)]
        mock_result = MagicMock()
        mock_result.scalars.return_value.all = MagicMock(return_value=mock_subscriptions)
        mock_db_session.execute = AsyncMock(return_value=mock_result)

        result = await repo.get_user_subscription(1)

        assert len(result) == 2

    @pytest.mark.asyncio
    async def test_get_user_subscription_only_users(self, repo, mock_db_session):
        mock_subscriptions = [self.create_mock_subscription(1, 2, 1, True)]
        mock_result = MagicMock()
        mock_result.scalars.return_value.all = MagicMock(return_value=mock_subscriptions)
        mock_db_session.execute = AsyncMock(return_value=mock_result)

        result = await repo.get_user_subscription(1, only_users=True)

        assert len(result) == 1

    @pytest.mark.asyncio
    async def test_get_user_subscription_only_wishlists(self, repo, mock_db_session):
        mock_subscription = self.create_mock_subscription(1, 2, None, False)
        mock_subscription.target_wishlist_id = 1
        mock_result = MagicMock()
        mock_result.scalars.return_value.all = MagicMock(return_value=[mock_subscription])
        mock_db_session.execute = AsyncMock(return_value=mock_result)

        result = await repo.get_user_subscription(1, only_wishlists=True)

        assert len(result) == 1

    @pytest.mark.asyncio
    async def test_get_user_subscription_desc_order(self, repo, mock_db_session):
        mock_subscriptions = [self.create_mock_subscription(2), self.create_mock_subscription(1)]
        mock_result = MagicMock()
        mock_result.scalars.return_value.all = MagicMock(return_value=mock_subscriptions)
        mock_db_session.execute = AsyncMock(return_value=mock_result)

        result = await repo.get_user_subscription(1, is_desc=True)

        assert len(result) == 2

    # ==================== get_user_subscribers ====================
    @pytest.mark.asyncio
    async def test_get_user_subscribers_success(self, repo, mock_db_session):
        mock_subscriptions = [self.create_mock_subscription(1, 2, 1, True)]
        mock_result = MagicMock()
        mock_result.scalars.return_value.all = MagicMock(return_value=mock_subscriptions)
        mock_db_session.execute = AsyncMock(return_value=mock_result)

        result = await repo.get_user_subscribers(1, is_desc=True)

        assert len(result) == 1

    @pytest.mark.asyncio
    async def test_get_user_subscribers_empty(self, repo, mock_db_session):
        mock_result = MagicMock()
        mock_result.scalars.return_value.all = MagicMock(return_value=[])
        mock_db_session.execute = AsyncMock(return_value=mock_result)

        result = await repo.get_user_subscribers(1, is_desc=False)

        assert result == []

    # ==================== update ====================
    @pytest.mark.asyncio
    async def test_update_success(self, repo, mock_db_session):
        updated_time = datetime.now()
        mock_result = MagicMock()
        mock_result.scalar_one_or_none = MagicMock(return_value=updated_time)
        mock_db_session.execute = AsyncMock(return_value=mock_result)
        mock_db_session.commit = AsyncMock()

        result = await repo.update(1)

        assert result is not None
        assert result.status is True
        assert result.updated_at == updated_time

    @pytest.mark.asyncio
    async def test_update_no_result(self, repo, mock_db_session):
        mock_result = MagicMock()
        mock_result.scalar_one_or_none = MagicMock(return_value=None)
        mock_db_session.execute = AsyncMock(return_value=mock_result)
        mock_db_session.commit = AsyncMock()

        result = await repo.update(1)

        assert result is None

    # ==================== count_user_subscribers ====================
    @pytest.mark.asyncio
    async def test_count_user_subscribers_success(self, repo, mock_db_session):
        mock_result = MagicMock()
        mock_result.scalar = MagicMock(return_value=5)
        mock_db_session.execute = AsyncMock(return_value=mock_result)

        result = await repo.count_user_subscribers(1)

        assert result == 5

    # ==================== count_user_subscriptions ====================
    @pytest.mark.asyncio
    async def test_count_user_subscriptions_all(self, repo, mock_db_session):
        mock_result = MagicMock()
        mock_result.scalar_one = MagicMock(return_value=3)
        mock_db_session.execute = AsyncMock(return_value=mock_result)

        result = await repo.count_user_subscriptions(1)

        assert result == 3

    @pytest.mark.asyncio
    async def test_count_user_subscriptions_only_users(self, repo, mock_db_session):
        mock_result = MagicMock()
        mock_result.scalar_one = MagicMock(return_value=2)
        mock_db_session.execute = AsyncMock(return_value=mock_result)

        result = await repo.count_user_subscriptions(1, only_users=True)

        assert result == 2

    @pytest.mark.asyncio
    async def test_count_user_subscriptions_only_wishlists(self, repo, mock_db_session):
        mock_result = MagicMock()
        mock_result.scalar_one = MagicMock(return_value=1)
        mock_db_session.execute = AsyncMock(return_value=mock_result)

        result = await repo.count_user_subscriptions(1, only_wishlists=True)

        assert result == 1