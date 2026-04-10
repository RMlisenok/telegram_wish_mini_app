# tests/unit/test_core/test_security_missing.py
import pytest
from unittest.mock import patch, MagicMock
from app.core.security import verify_tg_init_data


class TestSecurityMissing:
    """Additional security tests for missing coverage."""

    def test_verify_tg_init_data_with_real_hash(self):
        """Test with properly formatted but invalid hash."""
        # Создаем валидный init_data без подписи
        init_data = "user=123&auth_date=1234567890&hash=invalidhash"

        with patch("app.core.security.settings") as mock_settings:
            mock_settings.TELEGRAM_BOT_TOKEN = "test_token"
            result = verify_tg_init_data(init_data)
            assert result is False

    def test_verify_tg_init_data_with_special_chars(self):
        """Test with URL encoded special characters."""
        init_data = "user%3D123%26auth_date%3D1234567890%26hash%3Dtest"
        result = verify_tg_init_data(init_data)
        assert result is False

    def test_verify_tg_init_data_missing_token(self):
        """Test when bot token is missing."""
        with patch("app.core.security.settings") as mock_settings:
            mock_settings.TELEGRAM_BOT_TOKEN = None
            result = verify_tg_init_data("test=data&hash=123")
            assert result is False

    def test_verify_tg_init_data_decode_error(self):
        """Test with malformed URL encoded data."""
        result = verify_tg_init_data("%invalid%encoding%")
        assert result is False

    def test_verify_tg_init_data_no_auth_date(self):
        """Test init data without auth_date."""
        init_data = "user=123&hash=testhash"
        result = verify_tg_init_data(init_data)
        assert result is False

    def test_verify_jwt_token_with_expired_handling(self):
        """Test expired token handling."""
        from app.core.security import create_jwt_token, verify_jwt_token
        from freezegun import freeze_time

        with freeze_time("2024-01-01 00:00:00"):
            token = create_jwt_token({"sub": "1"})

        with freeze_time("2024-02-01 00:00:00"):
            result = verify_jwt_token(token)
            assert result is None

    def test_create_jwt_token_with_complex_payload(self):
        """Test creating JWT with nested structures."""
        from app.core.security import create_jwt_token, verify_jwt_token

        complex_payload = {
            "sub": "123",
            "user": {
                "id": 1,
                "name": "Test",
                "permissions": ["read", "write"]
            },
            "metadata": {
                "version": "1.0",
                "timestamp": 1234567890
            }
        }

        token = create_jwt_token(complex_payload)
        payload = verify_jwt_token(token)

        assert payload is not None
        assert payload["user"]["name"] == "Test"
        assert payload["metadata"]["version"] == "1.0"