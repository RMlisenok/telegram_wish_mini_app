# tests/fixtures/access_request_fixtures.py
import pytest
from datetime import datetime
from typing import Dict, Any
from app.models.access_request import AccessRequestStatus


@pytest.fixture
def access_request_data() -> Dict[str, Any]:
    """Access request fixture."""
    return {
        "id": 1,
        "wishlist_id": 1,
        "requester_id": 2,
        "status": AccessRequestStatus.PENDING,
        "created_at": datetime.now(),
        "processed_at": None
    }


@pytest.fixture
def access_request_approved_data() -> Dict[str, Any]:
    """Approved access request fixture."""
    return {
        "id": 2,
        "wishlist_id": 1,
        "requester_id": 3,
        "status": AccessRequestStatus.APPROVED,
        "created_at": datetime.now(),
        "processed_at": datetime.now()
    }


@pytest.fixture
def access_request_create_data() -> Dict[str, Any]:
    """Access request create data fixture."""
    return {"wishlist_id": 1}
