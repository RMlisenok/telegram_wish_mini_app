import pytest
import os
from unittest.mock import AsyncMock, MagicMock, patch
from datetime import date, timedelta
from app.services.notification_service_bot import NotificationService
from app.models.user import User
from app.models.notification_settings import NotificationSettings
from app.models.subscription import Subscription
from aiogram import types

class TestNotificationServiceBot:
    """Полный набор тестов для NotificationService для достижения высокого покрытия."""

    @pytest.fixture
    def service(self):
        # Патчим bot в модуле, чтобы не было реальных запросов
        with patch("app.services.notification_service_bot.bot", AsyncMock()):
            s = NotificationService()
            # Переопределяем bot внутри сервиса на AsyncMock для проверок
            s.bot = AsyncMock()
            return s

    def mock_user(self, id=1, tg_id=12345, name="Test User"):
        u = MagicMock(spec=User)
        u.id = id
        u.telegram_id = tg_id
        u.name = name
        u.full_name = name
        return u

    def setup_mock_execute(self, mock_db_session, return_value):
        """Хелпер для настройки возвращаемого значения scalar_one_or_none."""
        mock_res = MagicMock()
        mock_res.scalar_one_or_none.return_value = return_value
        mock_db_session.execute.return_value = mock_res
        return mock_res

    
    @pytest.mark.asyncio
    async def test_can_notify_no_settings(self, service, mock_db_session):
        # Если в базе нет записи настроек, должно вернуть True
        self.setup_mock_execute(mock_db_session, None)
        result = await service._can_notify(mock_db_session, 1, "new_followers")
        assert result is True

    @pytest.mark.asyncio
    async def test_can_notify_enabled(self, service, mock_db_session):
        settings = MagicMock(spec=NotificationSettings)
        settings.new_followers = True
        self.setup_mock_execute(mock_db_session, settings)
        
        result = await service._can_notify(mock_db_session, 1, "new_followers")
        assert result is True

    @pytest.mark.asyncio
    async def test_can_notify_disabled(self, service, mock_db_session):
        settings = MagicMock(spec=NotificationSettings)
        settings.new_followers = False
        self.setup_mock_execute(mock_db_session, settings)
        
        result = await service._can_notify(mock_db_session, 1, "new_followers")
        assert result is False


    @pytest.mark.asyncio
    async def test_notify_birthday_success(self, service, mock_db_session):
        user = self.mock_user(1, 123)
        # Мокаем: 1. _can_notify (True), 2. _get_user_info (user)
        service._can_notify = AsyncMock(return_value=True)
        service._get_user_info = AsyncMock(return_value=user)

        await service.notify_birthday(mock_db_session, 1, 2, "Friend", "today")
        service.bot.send_message.assert_called_once()
        assert "Сегодня день рождения" in service.bot.send_message.call_args[0][1]

    @pytest.mark.asyncio
    async def test_notify_birthday_disabled(self, service, mock_db_session):
        service._can_notify = AsyncMock(return_value=False)
        await service.notify_birthday(mock_db_session, 1, 2, "Friend", "tomorrow")
        service.bot.send_message.assert_not_called()

    @pytest.mark.asyncio
    async def test_notify_birthday_no_tg_id(self, service, mock_db_session):
        user = self.mock_user(1, None) # Нет телеграм ID
        service._can_notify = AsyncMock(return_value=True)
        service._get_user_info = AsyncMock(return_value=user)

        await service.notify_birthday(mock_db_session, 1, 2, "Friend", "next_week")
        service.bot.send_message.assert_not_called()


    @pytest.mark.asyncio
    async def test_notify_new_subscriber_success(self, service, mock_db_session):
        owner = self.mock_user(1, 123)
        service._can_notify = AsyncMock(return_value=True)
        service._get_user_info = AsyncMock(return_value=owner)

        await service.notify_new_subscriber(mock_db_session, 1, 2, "<b>New Friend</b>")
        
        service.bot.send_message.assert_called_once()
        # Проверка HTML экранирования (теги <b> внутри имени должны быть экранированы)
        assert "&lt;b&gt;New Friend&lt;/b&gt;" in service.bot.send_message.call_args[0][1]


    @pytest.mark.asyncio
    async def test_notify_post_birthday_success(self, service, mock_db_session):
        user = self.mock_user(1, 123)
        service._can_notify = AsyncMock(return_value=True)
        service._get_user_info = AsyncMock(return_value=user)

        await service.notify_post_birthday(mock_db_session, 1)
        service.bot.send_message.assert_called_once()
        assert "исполненные" in service.bot.send_message.call_args[0][1]


    @pytest.mark.asyncio
    async def test_send_access_request_structure(self, service, mock_db_session):
        owner = self.mock_user(1, 123)
        service._can_notify = AsyncMock(return_value=True)
        service._get_user_info = AsyncMock(return_value=owner)

        await service.send_access_request(mock_db_session, 1, 2, "Alice", "My Wishlist", 777)
        
        args, kwargs = service.bot.send_message.call_args
        assert kwargs["reply_markup"] is not None
        # Проверяем наличие кнопок в markup
        markup = kwargs["reply_markup"]
        buttons_data = [b.callback_data for row in markup.inline_keyboard for b in row]
        assert "approve_777" in buttons_data
        assert "reject_777" in buttons_data


    @pytest.mark.asyncio
    async def test_check_birthdays_and_notify_full_cycle(self, service, mock_db_session):
        b_user = self.mock_user(10, name="Birthday User")
        sub = MagicMock(subscriber_id=5)
        
        res_b_day = MagicMock()
        res_b_day.scalars.return_value.all.return_value = [b_user]
        
        res_subs = MagicMock()
        res_subs.scalars.return_value.all.return_value = [sub]
        
        res_empty = MagicMock()
        res_empty.scalars.return_value.all.return_value = []

        mock_db_session.execute.side_effect = [
            res_b_day, res_subs, # Сегодня
            res_empty,           # Завтра
            res_empty            # Неделя
        ]

        service.notify_birthday = AsyncMock()
        await service.check_birthdays_and_notify(mock_db_session)
        
        assert service.notify_birthday.call_count == 1
        service.notify_birthday.assert_called_with(
            session=mock_db_session,
            user_id=5,
            friend_id=10,
            friend_name="Birthday User",
            msg_type="today"
        )

    @pytest.mark.asyncio
    async def test_get_user_info_none(self, service, mock_db_session):
        self.setup_mock_execute(mock_db_session, None)
        res = await service._get_user_info(mock_db_session, 999)
        assert res is None

    def test_get_link(self, service):
        link = service._get_link(1, "<b>Name</b>")
        assert "&lt;b&gt;Name&lt;/b&gt;" in link
        assert "profile_1" in link
        assert "startapp=profile_1" in link
