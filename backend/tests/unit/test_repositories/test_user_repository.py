# tests/unit/test_repositories/test_user_repository.py
import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from datetime import date, datetime
from app.repositories.user_repository import UserRepository
from app.models.user import User
from app.schemas.user import UserCreate, UserUpdate, ThemeEnum, TextSizeEnum


class TestUserRepository:
    """Test suite for UserRepository."""

    @pytest.fixture
    def repo(self, mock_db_session):
        return UserRepository(mock_db_session)

    def create_mock_user(self, id=1, telegram_id=123456789, name="Test User"):
        mock = MagicMock(spec=User)
        mock.id = id
        mock.telegram_id = telegram_id
        mock.name = name
        mock.birth_date = date(1990, 1, 1)
        mock.photo = "https://example.com/photo.jpg"
        mock.theme = ThemeEnum.light
        mock.text_size = TextSizeEnum.medium
        mock.show_sub = True
        mock.created_at = datetime.now()
        mock.updated_at = datetime.now()
        return mock

    # ==================== get_user_by_id ====================
    @pytest.mark.asyncio
    async def test_get_user_by_id_success(self, repo, mock_db_session):
        mock_user = self.create_mock_user(1)
        mock_result = MagicMock()
        mock_result.scalar_one_or_none = MagicMock(return_value=mock_user)
        mock_db_session.execute = AsyncMock(return_value=mock_result)

        result = await repo.get_user_by_id(1)

        assert result == mock_user
        mock_db_session.execute.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_user_by_id_not_found(self, repo, mock_db_session):
        mock_result = MagicMock()
        mock_result.scalar_one_or_none = MagicMock(return_value=None)
        mock_db_session.execute = AsyncMock(return_value=mock_result)

        result = await repo.get_user_by_id(999)

        assert result is None

    # ==================== get_user_by_tg_id ====================
    @pytest.mark.asyncio
    async def test_get_user_by_tg_id_success(self, repo, mock_db_session):
        mock_user = self.create_mock_user(1, 123456789)
        mock_result = MagicMock()
        mock_result.scalar_one_or_none = MagicMock(return_value=mock_user)
        mock_db_session.execute = AsyncMock(return_value=mock_result)

        result = await repo.get_user_by_tg_id(123456789)

        assert result == mock_user

    @pytest.mark.asyncio
    async def test_get_user_by_tg_id_not_found(self, repo, mock_db_session):
        mock_result = MagicMock()
        mock_result.scalar_one_or_none = MagicMock(return_value=None)
        mock_db_session.execute = AsyncMock(return_value=mock_result)

        result = await repo.get_user_by_tg_id(999)

        assert result is None

    # ==================== get_all_users ====================
    @pytest.mark.asyncio
    async def test_get_all_users_success(self, repo, mock_db_session):
        mock_users = [self.create_mock_user(1), self.create_mock_user(2)]
        mock_result = MagicMock()
        mock_result.scalars.return_value.all = MagicMock(return_value=mock_users)
        mock_db_session.execute = AsyncMock(return_value=mock_result)

        result = await repo.get_all_users(limit=10)

        assert len(result) == 2
        assert result == mock_users

    @pytest.mark.asyncio
    async def test_get_all_users_empty(self, repo, mock_db_session):
        mock_result = MagicMock()
        mock_result.scalars.return_value.all = MagicMock(return_value=[])
        mock_db_session.execute = AsyncMock(return_value=mock_result)

        result = await repo.get_all_users(limit=10)

        assert result == []

    # ==================== create ====================
    @pytest.mark.asyncio
    async def test_create_user_success(self, repo, mock_db_session):
        user_data = UserCreate(
            telegram_id=123456789,
            name="New User",
            birth_date=date(1990, 1, 1)
        )
        mock_user = self.create_mock_user(1, 123456789, "New User")
        mock_db_session.add = MagicMock()
        mock_db_session.commit = AsyncMock()
        mock_db_session.refresh = AsyncMock()

        # Мокаем создание пользователя
        with patch('app.repositories.user_repository.User', return_value=mock_user):
            result = await repo.create(user_data)

            assert result == mock_user
            mock_db_session.add.assert_called_once()
            mock_db_session.commit.assert_called_once()

    # ==================== update ====================
    @pytest.mark.asyncio
    async def test_update_user_success(self, repo, mock_db_session):
        user_update = UserUpdate(name="Updated Name")
        mock_user = self.create_mock_user(1, 123456789, "Updated Name")
        
        mock_result = MagicMock()
        mock_result.scalar_one_or_none = MagicMock(return_value=mock_user)
        mock_db_session.execute = AsyncMock(return_value=mock_result)
        mock_db_session.commit = AsyncMock()
        mock_db_session.refresh = AsyncMock()

        result = await repo.update(1, user_update)

        assert result == mock_user

    @pytest.mark.asyncio
    async def test_update_user_no_changes(self, repo, mock_db_session):
        user_update = UserUpdate()
        mock_user = self.create_mock_user(1)
        
        repo.get_user_by_id = AsyncMock(return_value=mock_user)

        result = await repo.update(1, user_update)

        assert result == mock_user
