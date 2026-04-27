import pytest
from unittest.mock import AsyncMock
from app.services.notification_settings_service import NotificationSettingsService
from app.models.notification_settings import NotificationSettings
from app.schemas.notification_settings import NotificationSettingsUpdate


class TestNotificationSettingsService:
    """Test suite for NotificationSettingsService."""
    
    @pytest.fixture
    def settings_service(self, mock_db_session) -> NotificationSettingsService:
        """Create NotificationSettingsService instance."""
        service = NotificationSettingsService(mock_db_session)
        service.rep_settings = AsyncMock()
        return service
    
    @pytest.mark.asyncio
    async def test_get_user_notification_existing(self, settings_service, sample_notification_settings_data):
        """Test getting existing notification settings."""
        settings = NotificationSettings(**sample_notification_settings_data)
        settings_service.rep_settings.get_user_settings = AsyncMock(return_value=settings)
        
        result = await settings_service.get_user_notification(1)
        
        assert result is not None
        assert result.user_id == 1
        assert result.new_followers is True
        assert result.birt_before is True
        settings_service.rep_settings.get_user_settings.assert_called_once_with(1)
    
    @pytest.mark.asyncio
    async def test_get_user_notification_create_new(self, settings_service, sample_notification_settings_data):
        """Test creating new notification settings when not exists."""
        settings_service.rep_settings.get_user_settings = AsyncMock(return_value=None)
        created_settings = NotificationSettings(**sample_notification_settings_data)
        settings_service.rep_settings.create_notification_settings = AsyncMock(return_value=created_settings)
        
        result = await settings_service.get_user_notification(1)
        
        assert result is not None
        assert result.user_id == 1
        settings_service.rep_settings.create_notification_settings.assert_called_once_with(1)
    
    @pytest.mark.asyncio
    async def test_update_notification_success(self, settings_service, sample_notification_settings_data):
        """Test successfully updating notification settings."""
        update_data = NotificationSettingsUpdate(new_followers=False, birt_before=False)
        updated_settings = NotificationSettings(**sample_notification_settings_data)
        updated_settings.new_followers = False
        updated_settings.birt_before = False
        
        settings_service.rep_settings.update_settings = AsyncMock(return_value=updated_settings)
        
        result = await settings_service.update_notification(update_data, 1)
        
        assert result is not None
        assert result.new_followers is False
        assert result.birt_before is False
        settings_service.rep_settings.update_settings.assert_called_once_with(update_data, 1)
    
    @pytest.mark.asyncio
    async def test_update_notification_no_changes(self, settings_service):
        """Test update with no changes."""
        update_data = NotificationSettingsUpdate()
        settings_service.rep_settings.update_settings = AsyncMock(return_value=None)
        
        result = await settings_service.update_notification(update_data, 1)
        
        assert result is None