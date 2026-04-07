# tests/fixtures/wish_fixtures.py
import pytest
from datetime import datetime
from typing import Dict, Any
from app.models.wish import CurrencyEnum


@pytest.fixture
def wish_data_1() -> Dict[str, Any]:
    """Wish 1 fixture."""
    return {
        "id": 1,
        "user_id": 1,
        "name": "iPhone 15",
        "photo": "https://example.com/iphone.jpg",
        "url_gift": "https://store.com/iphone",
        "price": 999.99,
        "currency": CurrencyEnum.USD,
        "description": "New iPhone",
        "is_booked": False,
        "status_is_finished": False,
        "created_at": datetime.now(),
        "updated_at": datetime.now()
    }


@pytest.fixture
def wish_data_2() -> Dict[str, Any]:
    """Wish 2 fixture."""
    return {
        "id": 2,
        "user_id": 1,
        "name": "Book",
        "photo": "https://example.com/book.jpg",
        "url_gift": "https://store.com/book",
        "price": 29.99,
        "currency": CurrencyEnum.USD,
        "description": "Interesting book",
        "is_booked": True,
        "status_is_finished": False,
        "created_at": datetime.now(),
        "updated_at": datetime.now()
    }


@pytest.fixture
def wish_create_data() -> Dict[str, Any]:
    """Wish create data fixture."""
    return {
        "name": "New Wish",
        "photo": None,
        "url_gift": "https://example.com/gift",
        "price": 100.0,
        "currency": CurrencyEnum.RUB,
        "description": "Description"
    }


@pytest.fixture
def wish_wishlist_data() -> Dict[str, Any]:
    """Wish-Wishlist association fixture."""
    return {
        "id": 1,
        "wish_id": 1,
        "wishlist_id": 1,
        "is_pinned": False,
        "order_position": 0,
        "created_at": datetime.now(),
        "updated_at": datetime.now()
    }


@pytest.fixture
def wish_reservation_data() -> Dict[str, Any]:
    """Wish reservation fixture."""
    return {
        "id": 1,
        "wish_wishlist_id": 1,
        "reserved_by_id": 2,
        "created_at": datetime.now()
    }
