# tests/fixtures/wishlist_fixtures.py
import pytest
from datetime import datetime
from typing import Dict, Any
from app.models.wishlist import TypePrivacyEnum


@pytest.fixture
def wishlist_data_1() -> Dict[str, Any]:
    """Wishlist 1 fixture."""
    return {
        "id": 1,
        "user_id": 1,
        "name": "My Birthday Wishes",
        "description": "Things I want for birthday",
        "photo": "https://example.com/wishlist1.jpg",
        "typeprivacy": TypePrivacyEnum.public,
        "created_at": datetime.now(),
        "updated_at": datetime.now()
    }


@pytest.fixture
def wishlist_data_2() -> Dict[str, Any]:
    """Wishlist 2 fixture."""
    return {
        "id": 2,
        "user_id": 2,
        "name": "Christmas List",
        "description": "Christmas wishes",
        "photo": "https://example.com/wishlist2.jpg",
        "typeprivacy": TypePrivacyEnum.private,
        "created_at": datetime.now(),
        "updated_at": datetime.now()
    }


@pytest.fixture
def wishlist_create_data() -> Dict[str, Any]:
    """Wishlist create data fixture."""
    return {
        "name": "New Wishlist",
        "description": "Description",
        "photo": None,
        "typeprivacy": TypePrivacyEnum.public
    }


@pytest.fixture
def wishlist_update_data() -> Dict[str, Any]:
    """Wishlist update data fixture."""
    return {
        "name": "Updated Wishlist",
        "description": "Updated description"
    }
