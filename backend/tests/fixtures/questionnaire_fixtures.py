# tests/fixtures/questionnaire_fixtures.py
import pytest
from datetime import datetime
from typing import Dict, Any


@pytest.fixture
def tag_form_data() -> Dict[str, Any]:
    """Tag form fixture."""
    return {
        "id": 1,
        "tag_value": "Sport",
        "type_tags": True
    }


@pytest.fixture
def user_form_interest_data() -> Dict[str, Any]:
    """User form interest fixture."""
    return {
        "id": 1,
        "user_id": 1,
        "tag": "Football",
        "detail": "Loves football",
        "type_tag": True,
        "created_at": datetime.now(),
        "updated_at": datetime.now()
    }


@pytest.fixture
def user_form_avoid_data() -> Dict[str, Any]:
    """User form avoid gift fixture."""
    return {
        "id": 2,
        "user_id": 1,
        "tag": "Sweets",
        "detail": "Allergic to chocolate",
        "type_tag": False,
        "created_at": datetime.now(),
        "updated_at": datetime.now()
    }


@pytest.fixture
def questionnaire_create_data() -> Dict[str, Any]:
    """Questionnaire create data fixture."""
    return {
        "interests": [{"tag": "Sport", "details": "Football"}],
        "avoid_gifts": [{"tag": "Sweets", "details": "Chocolate"}]
    }
