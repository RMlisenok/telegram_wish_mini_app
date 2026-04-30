# tests/unit/test_repositories/test_access_request_repository.py
import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from datetime import datetime
from app.repositories.access_request_repository import AccessRequestRepository
from app.models.access_request import AccessRequestStatus


class TestAccessRequestRepository:
    """Test suite for AccessRequestRepository."""

    @pytest.fixture
    def repo(self, mock_db_session):
        return AccessRequestRepository(mock_db_session)

    def create_mock_request(self, id=1, wishlist_id=1, requester_id=2, status=AccessRequestStatus.PENDING):
        mock = MagicMock()
        mock.id = id
        mock.wishlist_id = wishlist_id
        mock.requester_id = requester_id
        mock.status = status
        mock.created_at = datetime.now()
        mock.processed_at = None
        return mock

    @pytest.mark.asyncio
    async def test_create_request_success(self, repo, mock_db_session):
        repo.get_request = AsyncMock(return_value=None)
        mock_request = self.create_mock_request(1, 1, 2)
        mock_db_session.add = MagicMock()
        mock_db_session.commit = AsyncMock()
        mock_db_session.refresh = AsyncMock()

        with patch('app.repositories.access_request_repository.AccessRequest', return_value=mock_request):
            result = await repo.create(1, 2)

            assert result == mock_request
            mock_db_session.add.assert_called_once()
            mock_db_session.commit.assert_called_once()

    @pytest.mark.asyncio
    async def test_create_request_already_exists(self, repo, mock_db_session):
        mock_request = self.create_mock_request(1, 1, 2)
        repo.get_request = AsyncMock(return_value=mock_request)

        result = await repo.create(1, 2)

        assert result is None

    @pytest.mark.asyncio
    async def test_create_request_exception(self, repo, mock_db_session):
        repo.get_request = AsyncMock(return_value=None)
        mock_db_session.commit = AsyncMock(side_effect=Exception("DB error"))
        mock_db_session.rollback = AsyncMock()

        with patch('app.repositories.access_request_repository.AccessRequest', return_value=MagicMock()):
            result = await repo.create(1, 2)

            assert result is None
            mock_db_session.rollback.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_request_id_success(self, repo, mock_db_session):
        mock_request = self.create_mock_request(1)
        mock_result = MagicMock()
        mock_result.scalar_one_or_none = MagicMock(return_value=mock_request)
        mock_db_session.execute = AsyncMock(return_value=mock_result)

        result = await repo.get_request_id(1)

        assert result == mock_request

    @pytest.mark.asyncio
    async def test_get_request_id_not_found(self, repo, mock_db_session):
        mock_result = MagicMock()
        mock_result.scalar_one_or_none = MagicMock(return_value=None)
        mock_db_session.execute = AsyncMock(return_value=mock_result)

        result = await repo.get_request_id(999)

        assert result is None

    @pytest.mark.asyncio
    async def test_update_status_to_approved(self, repo, mock_db_session):
        mock_request = self.create_mock_request(1)
        mock_result = MagicMock()
        mock_result.scalar_one_or_none = MagicMock(return_value=mock_request)
        mock_db_session.execute = AsyncMock(return_value=mock_result)
        mock_db_session.commit = AsyncMock()
        mock_db_session.refresh = AsyncMock()

        result = await repo.update_status(1, AccessRequestStatus.APPROVED)

        assert result is True

    @pytest.mark.asyncio
    async def test_update_status_to_rejected(self, repo, mock_db_session):
        mock_request = self.create_mock_request(1)
        mock_result = MagicMock()
        mock_result.scalar_one_or_none = MagicMock(return_value=mock_request)
        mock_db_session.execute = AsyncMock(return_value=mock_result)
        mock_db_session.commit = AsyncMock()
        mock_db_session.refresh = AsyncMock()

        result = await repo.update_status(1, AccessRequestStatus.REJECTED)

        assert result is True

    @pytest.mark.asyncio
    async def test_update_status_exception(self, repo, mock_db_session):
        mock_db_session.execute = AsyncMock(side_effect=Exception("DB error"))
        mock_db_session.rollback = AsyncMock()

        result = await repo.update_status(1, AccessRequestStatus.APPROVED)

        assert result is False
        mock_db_session.rollback.assert_called_once()

    @pytest.mark.asyncio
    async def test_delete_request_success(self, repo, mock_db_session):
        mock_request = self.create_mock_request(1)
        repo.get_request_id = AsyncMock(return_value=mock_request)
        mock_db_session.delete = AsyncMock()
        mock_db_session.commit = AsyncMock()

        result = await repo.delete(1)

        assert result is True
        mock_db_session.delete.assert_called_once()

    @pytest.mark.asyncio
    async def test_delete_request_not_found(self, repo, mock_db_session):
        repo.get_request_id = AsyncMock(return_value=None)

        result = await repo.delete(999)

        assert result is False

    @pytest.mark.asyncio
    async def test_delete_request_exception(self, repo, mock_db_session):
        mock_request = self.create_mock_request(1)
        repo.get_request_id = AsyncMock(return_value=mock_request)
        mock_db_session.delete = AsyncMock(side_effect=Exception("DB error"))
        mock_db_session.rollback = AsyncMock()

        result = await repo.delete(1)

        assert result is False
        mock_db_session.rollback.assert_called_once()

    @pytest.mark.asyncio
    async def test_has_access_true(self, repo, mock_db_session):
        mock_request = self.create_mock_request(1, 1, 2, AccessRequestStatus.APPROVED)
        mock_result = MagicMock()
        mock_result.scalar_one_or_none = MagicMock(return_value=mock_request)
        mock_db_session.execute = AsyncMock(return_value=mock_result)

        result = await repo.has_access(1, 2)

        assert result is True

    @pytest.mark.asyncio
    async def test_has_access_false(self, repo, mock_db_session):
        mock_result = MagicMock()
        mock_result.scalar_one_or_none = MagicMock(return_value=None)
        mock_db_session.execute = AsyncMock(return_value=mock_result)

        result = await repo.has_access(1, 2)

        assert result is False

    @pytest.mark.asyncio
    async def test_get_for_wishlist_all(self, repo, mock_db_session):
        mock_requests = [self.create_mock_request(1), self.create_mock_request(2)]
        mock_result = MagicMock()
        mock_result.scalars.return_value.all = MagicMock(return_value=mock_requests)
        mock_db_session.execute = AsyncMock(return_value=mock_result)

        result = await repo.get_for_wishlist(1)

        assert len(result) == 2

    @pytest.mark.asyncio
    async def test_get_for_wishlist_with_status(self, repo, mock_db_session):
        mock_requests = [self.create_mock_request(1)]
        mock_result = MagicMock()
        mock_result.scalars.return_value.all = MagicMock(return_value=mock_requests)
        mock_db_session.execute = AsyncMock(return_value=mock_result)

        result = await repo.get_for_wishlist(1, status=AccessRequestStatus.PENDING)

        assert len(result) == 1

    @pytest.mark.asyncio
    async def test_get_for_wishlist_empty(self, repo, mock_db_session):
        mock_result = MagicMock()
        mock_result.scalars.return_value.all = MagicMock(return_value=[])
        mock_db_session.execute = AsyncMock(return_value=mock_result)

        result = await repo.get_for_wishlist(1)

        assert result == []

    @pytest.mark.asyncio
    async def test_get_for_requester_all(self, repo, mock_db_session):
        mock_requests = [self.create_mock_request(1), self.create_mock_request(2)]
        mock_result = MagicMock()
        mock_result.scalars.return_value.all = MagicMock(return_value=mock_requests)
        mock_db_session.execute = AsyncMock(return_value=mock_result)

        result = await repo.get_for_requester(2)

        assert len(result) == 2

    @pytest.mark.asyncio
    async def test_get_for_requester_with_status(self, repo, mock_db_session):
        mock_requests = [self.create_mock_request(1)]
        mock_result = MagicMock()
        mock_result.scalars.return_value.all = MagicMock(return_value=mock_requests)
        mock_db_session.execute = AsyncMock(return_value=mock_result)

        result = await repo.get_for_requester(2, status=AccessRequestStatus.PENDING)

        assert len(result) == 1

    @pytest.mark.asyncio
    async def test_get_for_wishlist_owner_all(self, repo, mock_db_session):
        mock_requests = [self.create_mock_request(1), self.create_mock_request(2)]
        mock_result = MagicMock()
        mock_result.scalars.return_value.all = MagicMock(return_value=mock_requests)
        mock_db_session.execute = AsyncMock(return_value=mock_result)

        result = await repo.get_for_wishlist_owner(1)

        assert len(result) == 2

    @pytest.mark.asyncio
    async def test_get_for_wishlist_owner_with_status(self, repo, mock_db_session):
        mock_requests = [self.create_mock_request(1)]
        mock_result = MagicMock()
        mock_result.scalars.return_value.all = MagicMock(return_value=mock_requests)
        mock_db_session.execute = AsyncMock(return_value=mock_result)

        result = await repo.get_for_wishlist_owner(1, status=AccessRequestStatus.PENDING)

        assert len(result) == 1

    @pytest.mark.asyncio
    async def test_get_request_success(self, repo, mock_db_session):
        mock_request = self.create_mock_request(1, 1, 2)
        mock_result = MagicMock()
        mock_result.scalar_one_or_none = MagicMock(return_value=mock_request)
        mock_db_session.execute = AsyncMock(return_value=mock_result)

        result = await repo.get_request(1, 2)

        assert result == mock_request

    @pytest.mark.asyncio
    async def test_get_request_not_found(self, repo, mock_db_session):
        mock_result = MagicMock()
        mock_result.scalar_one_or_none = MagicMock(return_value=None)
        mock_db_session.execute = AsyncMock(return_value=mock_result)

        result = await repo.get_request(1, 999)

        assert result is None

    @pytest.mark.asyncio
    async def test_get_with_details_success(self, repo, mock_db_session):
        mock_request = self.create_mock_request(1)
        mock_result = MagicMock()
        mock_result.scalar_one_or_none = MagicMock(return_value=mock_request)
        mock_db_session.execute = AsyncMock(return_value=mock_result)

        result = await repo.get_with_details(1)

        assert result == mock_request

    @pytest.mark.asyncio
    async def test_get_for_requester_with_details_success(self, repo, mock_db_session):
        mock_requests = [self.create_mock_request(1), self.create_mock_request(2)]
        mock_result = MagicMock()
        mock_result.scalars.return_value.all = MagicMock(return_value=mock_requests)
        mock_db_session.execute = AsyncMock(return_value=mock_result)

        result = await repo.get_for_requester_with_details(2)

        assert len(result) == 2

    @pytest.mark.asyncio
    async def test_get_for_wishlist_owner_with_details_success(self, repo, mock_db_session):
        mock_requests = [self.create_mock_request(1), self.create_mock_request(2)]
        mock_result = MagicMock()
        mock_result.scalars.return_value.all = MagicMock(return_value=mock_requests)
        mock_db_session.execute = AsyncMock(return_value=mock_result)

        result = await repo.get_for_wishlist_owner_with_details(1)

        assert len(result) == 2