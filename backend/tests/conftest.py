# tests/conftest.py
import sys
from pathlib import Path
import pytest
from unittest.mock import AsyncMock, MagicMock
from datetime import date, datetime
from typing import Generator, Dict, Any
import asyncio

# Добавляем корневую директорию в PYTHONPATH
root_dir = Path(__file__).parent.parent
sys.path.insert(0, str(root_dir))

# Импортируем настройки из вашего config.py
from app.core.config import settings
from sqlalchemy.ext.asyncio import AsyncSession

# Импортируем все фикстуры из fixtures модуля
from tests.fixtures.user_fixtures import *
from tests.fixtures.subscription_fixtures import *
from tests.fixtures.wishlist_fixtures import *
from tests.fixtures.notification_fixtures import *
from tests.fixtures.wish_fixtures import *
from tests.fixtures.access_request_fixtures import *
from tests.fixtures.questionnaire_fixtures import *
from tests.fixtures.recommendations_fixtures import *


@pytest.fixture(scope="session")
def event_loop() -> Generator:
    """Create event loop for async tests."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
def mock_db_session() -> AsyncMock:
    """Mock database session fixture."""
    session = AsyncMock(spec=AsyncSession)
    session.execute = AsyncMock()
    session.commit = AsyncMock()
    session.rollback = AsyncMock()
    session.add = MagicMock()
    session.delete = AsyncMock()
    session.refresh = AsyncMock()
    session.flush = AsyncMock()
    return session


@pytest.fixture
def mock_bot() -> AsyncMock:
    """Mock Telegram bot fixture."""
    bot = AsyncMock()
    bot.send_message = AsyncMock()
    bot.send_photo = AsyncMock()
    bot.edit_message_reply_markup = AsyncMock()
    return bot


# Базовые фикстуры для обратной совместимости
@pytest.fixture
def sample_user_data() -> Dict[str, Any]:
    """Sample user data for tests."""
    from app.models.user import ThemeEnum, TextSizeEnum
    return {
        "id": 1,
        "telegram_id": 123456789,
        "name": "Test User",
        "birth_date": date(1990, 1, 1),
        "photo": "https://example.com/photo.jpg",
        "theme": ThemeEnum.light,
        "text_size": TextSizeEnum.medium,
        "show_sub": True,
        "created_at": datetime.now(),
        "updated_at": datetime.now()
    }


@pytest.fixture
def sample_wishlist_data() -> Dict[str, Any]:
    """Sample wishlist data for tests."""
    from app.models.wishlist import TypePrivacyEnum
    return {
        "id": 1,
        "user_id": 1,
        "name": "Test Wishlist",
        "description": "Test description",
        "photo": "https://example.com/wishlist.jpg",
        "typeprivacy": TypePrivacyEnum.public,
        "created_at": datetime.now(),
        "updated_at": datetime.now()
    }


@pytest.fixture
def sample_wish_data() -> Dict[str, Any]:
    """Sample wish data for tests."""
    from app.models.wish import CurrencyEnum
    return {
        "id": 1,
        "user_id": 1,
        "name": "Test Wish",
        "photo": "https://example.com/wish.jpg",
        "url_gift": "https://example.com/gift",
        "price": 100.0,
        "currency": CurrencyEnum.RUB,
        "description": "Test description",
        "is_booked": False,
        "status_is_finished": False,
        "created_at": datetime.now(),
        "updated_at": datetime.now()
    }


@pytest.fixture
def sample_subscription_data() -> Dict[str, Any]:
    """Sample subscription data for tests."""
    return {
        "id": 1,
        "subscriber_id": 2,
        "type_sub": True,
        "target_user_id": 1,
        "target_wishlist_id": None,
        "created_at": datetime.now(),
        "updated_at": datetime.now()
    }


@pytest.fixture
def sample_notification_settings_data() -> Dict[str, Any]:
    """Sample notification settings data for tests."""
    return {
        "id": 1,
        "user_id": 1,
        "new_followers": True,
        "access_requests": True,
        "birt_before": True,
        "birt_after": False,
        "created_at": datetime.now(),
        "updated_at": datetime.now()
    }


@pytest.fixture
def sample_access_request_data() -> Dict[str, Any]:
    """Sample access request data for tests."""
    from app.models.access_request import AccessRequestStatus
    return {
        "id": 1,
        "wishlist_id": 1,
        "requester_id": 2,
        "status": AccessRequestStatus.PENDING,
        "created_at": datetime.now(),
        "processed_at": None
    }


@pytest.fixture
def sample_block_data() -> Dict[str, Any]:
    """Sample block data for tests."""
    return {
        "id": 1,
        "blocker_id": 1,
        "blocked_id": 2,
        "block_profile": True,
        "block_wishlists": False,
        "created_at": datetime.now(),
        "updated_at": datetime.now()
    }


@pytest.fixture
def sample_questionnaire_data() -> Dict[str, Any]:
    """Sample questionnaire data for tests."""
    return {
        "id": 1,
        "user_id": 1,
        "tag": "Sport",
        "detail": "Football",
        "type_tag": True,
        "created_at": datetime.now(),
        "updated_at": datetime.now()
    }


@pytest.fixture
def sample_gift_suggestion_data() -> Dict[str, Any]:
    """Sample gift suggestion data for tests."""
    return {
        "id": 1,
        "title": "Gift Suggestion",
        "description": "Great gift idea",
        "url": "https://example.com/gift",
        "tag_value": "Sport",
        "category": "Sports"
    }


@pytest.fixture
def sample_recommendation_log_data() -> Dict[str, Any]:
    """Sample recommendation log data for tests."""
    return {
        "id": 1,
        "user_id": 1,
        "created_at": datetime.now()
    }


@pytest.fixture
def user_form_interest_data() -> Dict[str, Any]:
    """User form interest data fixture."""
    return {
        "id": 1,
        "user_id": 1,
        "tag": "Sport",
        "detail": "Football",
        "type_tag": True,
        "created_at": datetime.now(),
        "updated_at": datetime.now()
    }


@pytest.fixture
def user_form_avoid_data() -> Dict[str, Any]:
    """User form avoid data fixture."""
    return {
        "id": 2,
        "user_id": 1,
        "tag": "Sweets",
        "detail": "Chocolate",
        "type_tag": False,
        "created_at": datetime.now(),
        "updated_at": datetime.now()
    }


@pytest.fixture
def gift_suggestion_data() -> Dict[str, Any]:
    """Gift suggestion data fixture."""
    return {
        "id": 1,
        "title": "Football Ball",
        "description": "Professional football ball",
        "url": "https://store.com/ball",
        "tag_value": "Sport",
        "category": "Sports"
    }


@pytest.fixture
def recommendation_log_data() -> Dict[str, Any]:
    """Recommendation log data fixture."""
    return {
        "id": 1,
        "user_id": 1,
        "created_at": datetime.now()
    }