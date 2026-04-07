# tests/fixtures/notification_fixtures.py
import pytest
from datetime import datetime
from typing import Dict, Any


@pytest.fixture
def notification_settings_data() -> Dict[str, Any]:
    """Notification settings fixture."""
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
def notification_settings_update_data() -> Dict[str, Any]:
    """Notification settings update data fixture."""
    return {
        "new_followers": False,
        "birt_before": False,
        "birt_after": True
    }
