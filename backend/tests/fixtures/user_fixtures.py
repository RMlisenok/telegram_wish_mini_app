# tests/fixtures/user_fixtures.py
import pytest
from datetime import date, datetime
from typing import Dict, Any
from app.models.user import ThemeEnum, TextSizeEnum


@pytest.fixture
def user_data_1() -> Dict[str, Any]:
    """User 1 fixture."""
    return {
        "id": 1,
        "telegram_id": 123456789,
        "name": "Test User 1",
        "birth_date": date(1990, 1, 15),
        "photo": "https://example.com/photo1.jpg",
        "theme": ThemeEnum.light,
        "text_size": TextSizeEnum.medium,
        "show_sub": True,
        "created_at": datetime.now(),
        "updated_at": datetime.now()
    }


@pytest.fixture
def user_data_2() -> Dict[str, Any]:
    """User 2 fixture."""
    return {
        "id": 2,
        "telegram_id": 987654321,
        "name": "Test User 2",
        "birth_date": date(1995, 5, 20),
        "photo": "https://example.com/photo2.jpg",
        "theme": ThemeEnum.dark,
        "text_size": TextSizeEnum.large,
        "show_sub": False,
        "created_at": datetime.now(),
        "updated_at": datetime.now()
    }


@pytest.fixture
def user_create_data() -> Dict[str, Any]:
    """User create data fixture."""
    return {
        "telegram_id": 555555555,
        "name": "New User",
        "birth_date": date(2000, 1, 1),
        "photo": None,
        "theme": ThemeEnum.light,
        "text_size": TextSizeEnum.medium,
        "show_sub": False
    }


@pytest.fixture
def user_update_data() -> Dict[str, Any]:
    """User update data fixture."""
    return {
        "name": "Updated Name",
        "theme": ThemeEnum.dark,
        "show_sub": True
    }
