import pytest
from unittest.mock import AsyncMock, MagicMock
from datetime import date, datetime
from typing import Dict, Any

from app.services.user_service import UserService
from app.models.user import User
from app.schemas.user import UserCreate, UserUpdate, ThemeEnum, TextSizeEnum
from app.schemas.block import BlockCreate
from app.schemas.block import UpdateBlock, BlockResponse


class TestUserService:
    """Test suite for UserService."""
    
    @pytest.fixture
    def user_service(self, mock_db_session) -> UserService:
        """Create UserService instance with mocked dependencies."""
        service = UserService(mock_db_session)
        
        service.rep_user = AsyncMock()
        service.rep_block = AsyncMock()
        service.rep_wishlist = AsyncMock()
        service.rep_wish = AsyncMock()
        service.rep_subs = AsyncMock()
        service.rep_wish_wishlist = AsyncMock()
        service.serv_subs = AsyncMock()
        service.serv_wishlist = AsyncMock()
        
        return service
    
    @pytest.mark.asyncio
    async def test_get_user_success(self, user_service, sample_user_data):
        """Test successfully getting a user by ID."""
        expected_user = User(**sample_user_data)
        user_service.rep_user.get_user_by_id = AsyncMock(return_value=expected_user)
        
        result = await user_service.get_user(1)
        
        assert result is not None
        assert result.id == expected_user.id
        assert result.name == expected_user.name
        assert result.telegram_id == expected_user.telegram_id
        user_service.rep_user.get_user_by_id.assert_called_once_with(1)
    
    @pytest.mark.asyncio
    async def test_get_user_not_found(self, user_service):
        """Test getting a non-existent user."""
        user_service.rep_user.get_user_by_id = AsyncMock(return_value=None)
        
        result = await user_service.get_user(999)
        
        assert result is None
        user_service.rep_user.get_user_by_id.assert_called_once_with(999)
    
    @pytest.mark.asyncio
    async def test_get_user_by_telegram_id_success(self, user_service, sample_user_data):
        """Test successfully getting a user by Telegram ID."""
        expected_user = User(**sample_user_data)
        user_service.rep_user.get_user_by_tg_id = AsyncMock(return_value=expected_user)
        
        result = await user_service.get_user_by_telegram_id(123456789)
        
        assert result is not None
        assert result.telegram_id == 123456789
        assert result.name == expected_user.name
        user_service.rep_user.get_user_by_tg_id.assert_called_once_with(123456789)
    
    @pytest.mark.asyncio
    async def test_get_all_users(self, user_service, sample_user_data):
        """Test getting all users."""
        users = [User(**sample_user_data)]
        user_service.rep_user.get_all_users = AsyncMock(return_value=users)
        
        result = await user_service.get_all_users(limit=10)
        
        assert len(result) == 1
        assert result[0].name == sample_user_data["name"]
        user_service.rep_user.get_all_users.assert_called_once_with(10)
    
    @pytest.mark.asyncio
    async def test_create_user_success(self, user_service, sample_user_data):
        """Test successfully creating a user."""
        user_create = UserCreate(
            telegram_id=123456789,
            name="New User",
            birth_date=date(1990, 1, 1)
        )
        expected_user = User(**sample_user_data)
        user_service.rep_user.create = AsyncMock(return_value=expected_user)
        
        result = await user_service.create_user(user_create)
        
        assert result is not None
        assert result.name == expected_user.name
        user_service.rep_user.create.assert_called_once_with(user_create)
    
    @pytest.mark.asyncio
    async def test_update_user_success(self, user_service, sample_user_data):
        """Test successfully updating a user."""
        user_update = UserUpdate(name="Updated Name")
        updated_user = User(**sample_user_data)
        updated_user.name = "Updated Name"
        user_service.rep_user.update = AsyncMock(return_value=updated_user)
        
        result = await user_service.update_user(1, user_update)
        
        assert result is not None
        assert result.name == "Updated Name"
        user_service.rep_user.update.assert_called_once_with(1, user_update)
    
    @pytest.mark.asyncio
    async def test_block_user_success(self, user_service):
        """Test successfully blocking a user."""
        block_data = BlockCreate(
            blocked_id=2,
            block_profile=True,
            block_wishlists=False
        )
        block = MagicMock()
        user_service.rep_block.block_user = AsyncMock(return_value=block)
        
        result = await user_service.block_user(1, block_data)
        
        assert result is not None
        user_service.rep_block.block_user.assert_called_once_with(1, block_data)
    
    @pytest.mark.asyncio
    async def test_unblock_user_success(self, user_service):
        """Test successfully unblocking a user."""
        user_service.rep_block.unblock_user = AsyncMock(return_value=True)
        
        result = await user_service.unblock_user(1, 2)
        
        assert result is True
        user_service.rep_block.unblock_user.assert_called_once_with(1, 2)

    @pytest.mark.asyncio
    async def test_check_block_status(self, user_service):
        """Test checking if user is blocked."""
        user_service.rep_block.is_user_blocked = AsyncMock(return_value=True)
        
        result = await user_service.check_block_status(1, 2)
        
        assert result is True
        user_service.rep_block.is_user_blocked.assert_called_once_with(1, 2)
    
    @pytest.mark.asyncio
    async def test_get_user_block_list(self, user_service, sample_user_data):
        """Test getting user's block list."""
        blocked_user = User(**sample_user_data)
        blocked_user.id = 2
        blocked_user.name = "Blocked User"
        
        blocked_record = MagicMock()
        blocked_record.blocked = blocked_user
        blocked_record.block_profile = True
        blocked_record.block_wishlists = False
        blocked_record.created_at = datetime.now()
        
        user_service.rep_block.get_user_block = AsyncMock(return_value=[blocked_record])
        
        result = await user_service.get_user_block(1)
        
        assert result.total == 1
        assert len(result.blocked_users) == 1
        user_service.rep_block.get_user_block.assert_called_once_with(1)

    @pytest.mark.asyncio
    async def test_update_block_success(self, user_service, sample_block_data):
            """Test successfully updating a block record."""
            
            blocker_id = 1
            blocked_id = 2
            update_data = UpdateBlock(
                block_profile=False,
                block_wishlists=True
            )
            
            # Создаем имитацию объекта из БД
            mock_updated_block = MagicMock()
            mock_updated_block.blocker_id = blocker_id
            mock_updated_block.blocked_id = blocked_id
            mock_updated_block.block_profile = update_data.block_profile
            mock_updated_block.block_wishlists = update_data.block_wishlists
            mock_updated_block.created_at = datetime.now()
            mock_updated_block.updated_at = datetime.now()
            
            # Настраиваем мок репозитория
            user_service.rep_block.update_block = AsyncMock(return_value=mock_updated_block)
            
            result = await user_service.update_block(blocker_id, blocked_id, update_data)
            
            assert result is not None
            assert isinstance(result, BlockResponse)
            assert result.block_profile is False
            assert result.block_wishlists is True
            user_service.rep_block.update_block.assert_called_once_with(
                blocker_id, blocked_id, update_data
            )

    @pytest.mark.asyncio
    async def test_update_block_not_found(self, user_service):
        """Test updating a block record that doesn't exist."""
        from app.schemas.block import UpdateBlock
        
        update_data = UpdateBlock(block_profile=True)
        user_service.rep_block.update_block = AsyncMock(return_value=None)
        
        result = await user_service.update_block(1, 999, update_data)
        
        assert result is None
        user_service.rep_block.update_block.assert_called_once_with(
            1, 999, update_data
        )