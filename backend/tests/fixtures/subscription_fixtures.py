# tests/fixtures/subscription_fixtures.py
import pytest
from datetime import datetime
from typing import Dict, Any


@pytest.fixture
def subscription_user_data() -> Dict[str, Any]:
    """User subscription fixture."""
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
def subscription_wishlist_data() -> Dict[str, Any]:
    """Wishlist subscription fixture."""
    return {
        "id": 2,
        "subscriber_id": 2,
        "type_sub": False,
        "target_user_id": None,
        "target_wishlist_id": 1,
        "created_at": datetime.now(),
        "updated_at": datetime.now()
    }


@pytest.fixture
def subscribe_to_user_request() -> Dict[str, Any]:
    """Subscribe to user request fixture."""
    return {"target_user_id": 1}


@pytest.fixture
def subscribe_to_wishlist_request() -> Dict[str, Any]:
    """Subscribe to wishlist request fixture."""
    return {"target_wishlist_id": 1}
