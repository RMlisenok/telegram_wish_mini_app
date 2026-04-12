# tests/unit/test_repositories/test_notification_settings_repository.py
import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from datetime import datetime
from app.repositories.notification_settings_repository import NotificationSettingsRepository
from app.models.notification_settings import NotificationSettings
from app.schemas.notification_settings import NotificationSettingsUpdate


class TestNotificationSettingsRepository:
    """Test suite for NotificationSettingsRepository."""

    @pytest.fixture
    def repo(self, mock_db_session):
        return NotificationSettingsRepository(mock_db_session)

    def create_mock_settings(self, user_id=1):
        mock = MagicMock(spec=NotificationSettings)
        mock.id = user_id
        mock.user_id = user_id
        mock.new_followers = True
        mock.access_requests = True
        mock.birt_before = True
        mock.birt_after = False
        mock.created_at = datetime.now()
        mock.updated_at = datetime.now()
        return mock

    # ==================== create_notification_settings ====================
    @pytest.mark.asyncio
    async def test_create_notification_settings_success(self, repo, mock_db_session):
        mock_settings = self.create_mock_settings(1)
        mock_db_session.add = MagicMock()
        mock_db_session.commit = AsyncMock()
        mock_db_session.refresh = AsyncMock()

        with patch('app.repositories.notification_settings_repository.NotificationSettings', return_value=mock_settings):
            result = await repo.create_notification_settings(1)

            assert result == mock_settings
            mock_db_session.add.assert_called_once()
            mock_db_session.commit.assert_called_once()

    # ==================== get_user_settings ====================
    @pytest.mark.asyncio
    async def test_get_user_settings_success(self, repo, mock_db_session):
        mock_settings = self.create_mock_settings(1)
        mock_result = MagicMock()
        mock_result.scalar_one_or_none = MagicMock(return_value=mock_settings)
        mock_db_session.execute = AsyncMock(return_value=mock_result)

        result = await repo.get_user_settings(1)

        assert result == mock_settings

    @pytest.mark.asyncio
    async def test_get_user_settings_not_found(self, repo, mock_db_session):
        mock_result = MagicMock()
        mock_result.scalar_one_or_none = MagicMock(return_value=None)
        mock_db_session.execute = AsyncMock(return_value=mock_result)

        result = await repo.get_user_settings(999)

        assert result is None

    # ==================== update_settings ====================
    @pytest.mark.asyncio
    async def test_update_settings_success(self, repo, mock_db_session):
        update_data = NotificationSettingsUpdate(new_followers=False, birt_before=False)
        mock_settings = self.create_mock_settings(1)
        
        mock_result = MagicMock()
        mock_result.scalar_one_or_none = MagicMock(return_value=mock_settings)
        mock_db_session.execute = AsyncMock(return_value=mock_result)
        mock_db_session.commit = AsyncMock()
        mock_db_session.refresh = AsyncMock()

        result = await repo.update_settings(update_data, 1)

        assert result == mock_settings

    @pytest.mark.asyncio
    async def test_update_settings_no_changes(self, repo, mock_db_session):
        update_data = NotificationSettingsUpdate()
        mock_settings = self.create_mock_settings(1)
        
        repo.get_user_settings = AsyncMock(return_value=mock_settings)

        result = await repo.update_settings(update_data, 1)

        assert result == mock_settings
