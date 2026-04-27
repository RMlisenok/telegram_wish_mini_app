import pytest
from unittest.mock import patch, MagicMock
from datetime import datetime, timedelta
import jwt
from freezegun import freeze_time  # Нужно установить: pip install freezegun
from app.core.security import verify_tg_init_data, create_jwt_token, verify_jwt_token
from app.core.config import settings


class TestSecurity:
    """Test suite for security functions."""

    def test_create_jwt_token_success(self):
        """Test creating JWT token."""
        data = {"sub": "1", "username": "test"}
        token = create_jwt_token(data)

        assert token is not None
        assert isinstance(token, str)
        assert len(token) > 0

    def test_create_jwt_token_with_expiry(self):
        """Test JWT token has expiry."""
        data = {"sub": "1"}
        token = create_jwt_token(data)

        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        assert "exp" in payload
        assert payload["sub"] == "1"

    def test_verify_jwt_token_success(self):
        """Test verifying valid JWT token."""
        data = {"sub": "1", "username": "test"}
        token = create_jwt_token(data)

        payload = verify_jwt_token(token)

        assert payload is not None
        assert payload["sub"] == "1"
        assert payload["username"] == "test"

    def test_verify_jwt_token_invalid(self):
        """Test verifying invalid JWT token."""
        payload = verify_jwt_token("invalid_token")

        assert payload is None

    def test_verify_jwt_token_expired(self):
        """Test verifying expired JWT token."""
        # Используем freeze_time для управления временем
        with freeze_time("2024-01-01 00:00:00"):
            data = {"sub": "1"}
            token = create_jwt_token(data)

        # Перемещаемся в будущее, когда токен должен истечь
        with freeze_time("2024-02-01 00:00:00"):  # Через месяц после создания
            payload = verify_jwt_token(token)
            assert payload is None

    def test_verify_tg_init_data_valid(self):
        """Test verifying valid Telegram init data."""
        result = verify_tg_init_data("")
        assert result is False

    def test_verify_tg_init_data_empty(self):
        """Test with empty init data."""
        result = verify_tg_init_data("")
        assert result is False

    def test_verify_tg_init_data_no_hash(self):
        """Test init data without hash."""
        result = verify_tg_init_data("user=123&auth_date=1234567890")
        assert result is False

    def test_verify_tg_init_data_exception(self):
        """Test exception handling."""
        result = verify_tg_init_data(None)
        assert result is False