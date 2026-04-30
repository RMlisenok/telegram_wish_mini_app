import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from datetime import datetime
from app.repositories.block_repository import BlockRepository
from app.models.block import BlockedUser
from app.schemas.block import BlockCreate, UpdateBlock


class TestBlockRepository:
    """Test suite for BlockRepository."""

    @pytest.fixture
    def repo(self, mock_db_session):
        return BlockRepository(mock_db_session)

    def create_mock_block(self, blocker_id=1, blocked_id=2):
        mock = MagicMock(spec=BlockedUser)
        mock.id = 1
        mock.blocker_id = blocker_id
        mock.blocked_id = blocked_id
        mock.block_profile = True
        mock.block_wishlists = False
        mock.created_at = datetime.now()
        mock.updated_at = datetime.now()
        return mock

    @pytest.mark.asyncio
    async def test_get_block_success(self, repo, mock_db_session):
        mock_block = self.create_mock_block(1, 2)
        mock_result = MagicMock()
        mock_result.scalar_one_or_none = MagicMock(return_value=mock_block)
        mock_db_session.execute = AsyncMock(return_value=mock_result)

        result = await repo.get_block(1, 2)

        assert result == mock_block

    @pytest.mark.asyncio
    async def test_get_block_not_found(self, repo, mock_db_session):
        mock_result = MagicMock()
        mock_result.scalar_one_or_none = MagicMock(return_value=None)
        mock_db_session.execute = AsyncMock(return_value=mock_result)

        result = await repo.get_block(1, 999)

        assert result is None

    @pytest.mark.asyncio
    async def test_block_user_new(self, repo, mock_db_session):
        block_data = BlockCreate(blocked_id=2, block_profile=True, block_wishlists=False)
        mock_block = self.create_mock_block(1, 2)
        
        repo.get_block = AsyncMock(return_value=None)
        mock_db_session.add = MagicMock()
        mock_db_session.commit = AsyncMock()
        mock_db_session.refresh = AsyncMock()

        with patch('app.repositories.block_repository.BlockedUser', return_value=mock_block):
            result = await repo.block_user(1, block_data)

            assert result == mock_block

    @pytest.mark.asyncio
    async def test_block_user_already_exists(self, repo, mock_db_session):
        block_data = BlockCreate(blocked_id=2, block_profile=True, block_wishlists=False)
        mock_block = self.create_mock_block(1, 2)
        
        repo.get_block = AsyncMock(return_value=mock_block)

        result = await repo.block_user(1, block_data)

        assert result == mock_block

    @pytest.mark.asyncio
    async def test_update_block_success(self, repo, mock_db_session):
        update_data = UpdateBlock(block_profile=False, block_wishlists=True)
        mock_block = self.create_mock_block(1, 2)
        
        repo.get_block = AsyncMock(return_value=mock_block)
        mock_result = MagicMock()
        mock_result.scalar_one_or_none = MagicMock(return_value=mock_block)
        mock_db_session.execute = AsyncMock(return_value=mock_result)
        mock_db_session.commit = AsyncMock()
        mock_db_session.refresh = AsyncMock()

        result = await repo.update_block(1, 2, update_data)

        assert result == mock_block

    @pytest.mark.asyncio
    async def test_update_block_not_found(self, repo, mock_db_session):
        update_data = UpdateBlock(block_profile=False, block_wishlists=True)
        
        repo.get_block = AsyncMock(return_value=None)

        result = await repo.update_block(1, 999, update_data)

        assert result is None

    @pytest.mark.asyncio
    async def test_unblock_user_success(self, repo, mock_db_session):
        mock_block = self.create_mock_block(1, 2)
        
        repo.get_block = AsyncMock(return_value=mock_block)
        mock_db_session.delete = AsyncMock()

        result = await repo.unblock_user(1, 2)

        assert result is True
        mock_db_session.delete.assert_called_once()

    @pytest.mark.asyncio
    async def test_unblock_user_not_found(self, repo, mock_db_session):
        repo.get_block = AsyncMock(return_value=None)

        result = await repo.unblock_user(1, 999)

        assert result is False

    @pytest.mark.asyncio
    async def test_is_user_blocked_true(self, repo, mock_db_session):
        mock_block = self.create_mock_block(1, 2)
        repo.get_block = AsyncMock(return_value=mock_block)

        result = await repo.is_user_blocked(1, 2)

        assert result is True

    @pytest.mark.asyncio
    async def test_is_user_blocked_false(self, repo, mock_db_session):
        repo.get_block = AsyncMock(return_value=None)

        result = await repo.is_user_blocked(1, 999)

        assert result is False

    @pytest.mark.asyncio
    async def test_get_user_block_success(self, repo, mock_db_session):
        mock_blocks = [self.create_mock_block(1, 2), self.create_mock_block(1, 3)]
        mock_result = MagicMock()
        mock_result.scalars.return_value.all = MagicMock(return_value=mock_blocks)
        mock_db_session.execute = AsyncMock(return_value=mock_result)

        result = await repo.get_user_block(1)

        assert len(result) == 2