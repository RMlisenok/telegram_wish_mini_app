# tests/fixtures/recommendations_fixtures.py
import pytest
from datetime import datetime
from typing import Dict, Any


@pytest.fixture
def gift_suggestion_data() -> Dict[str, Any]:
    """Gift suggestion fixture."""
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
    """Recommendation log fixture."""
    return {
        "id": 1,
        "user_id": 1,
        "created_at": datetime.now()
    }
