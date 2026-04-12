# tests/unit/test_core/test_dependencies.py
import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from fastapi import HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials
from app.core.dependencies import get_current_user_id, get_current_user, get_client_s3
from app.core.config import settings


class TestDependencies:
    """Test suite for dependencies."""

    @pytest.mark.asyncio
    async def test_get_current_user_id_success(self, mock_db_session):
        """Test getting current user ID from valid token."""
        credentials = HTTPAuthorizationCredentials(scheme="Bearer", credentials="valid_token")

        with patch("app.core.dependencies.verify_jwt_token") as mock_verify:
            mock_verify.return_value = {"sub": "1"}

            with patch("app.core.dependencies.UserService") as mock_user_service:
                mock_user_service.return_value.get_user = AsyncMock(return_value=MagicMock(id=1))

                result = await get_current_user_id(credentials, mock_db_session)

                assert result == 1

    @pytest.mark.asyncio
    async def test_get_current_user_id_invalid_token(self, mock_db_session):
        """Test with invalid token."""
        credentials = HTTPAuthorizationCredentials(scheme="Bearer", credentials="invalid")

        with patch("app.core.dependencies.verify_jwt_token") as mock_verify:
            mock_verify.return_value = None

            with pytest.raises(HTTPException) as exc_info:
                await get_current_user_id(credentials, mock_db_session)

            assert exc_info.value.status_code == status.HTTP_401_UNAUTHORIZED
            assert exc_info.value.detail == "Invalid Token"

    @pytest.mark.asyncio
    async def test_get_current_user_id_user_not_found(self, mock_db_session):
        """Test when user not found."""
        credentials = HTTPAuthorizationCredentials(scheme="Bearer", credentials="valid_token")

        with patch("app.core.dependencies.verify_jwt_token") as mock_verify:
            mock_verify.return_value = {"sub": "999"}

            with patch("app.core.dependencies.UserService") as mock_user_service:
                mock_user_service.return_value.get_user = AsyncMock(return_value=None)

                with pytest.raises(HTTPException) as exc_info:
                    await get_current_user_id(credentials, mock_db_session)

                assert exc_info.value.status_code == status.HTTP_401_UNAUTHORIZED
                assert exc_info.value.detail == "User not found"

    @pytest.mark.asyncio
    async def test_get_current_user_success(self, mock_db_session):
        """Test getting current user."""
        credentials = HTTPAuthorizationCredentials(scheme="Bearer", credentials="valid_token")
        mock_user = MagicMock()
        mock_user.id = 1

        with patch("app.core.dependencies.verify_jwt_token") as mock_verify:
            mock_verify.return_value = {"sub": "1"}

            with patch("app.core.dependencies.UserService") as mock_user_service:
                mock_user_service.return_value.get_user = AsyncMock(return_value=mock_user)

                result = await get_current_user(credentials, mock_db_session)

                assert result == mock_user

    @pytest.mark.asyncio
    async def test_get_current_user_invalid_token(self, mock_db_session):
        """Test with invalid token."""
        credentials = HTTPAuthorizationCredentials(scheme="Bearer", credentials="invalid")

        with patch("app.core.dependencies.verify_jwt_token") as mock_verify:
            mock_verify.return_value = None

            with pytest.raises(HTTPException) as exc_info:
                await get_current_user(credentials, mock_db_session)

            assert exc_info.value.status_code == status.HTTP_401_UNAUTHORIZED
            assert exc_info.value.detail == "Invalid token"

    @pytest.mark.asyncio
    async def test_get_current_user_no_user_id(self, mock_db_session):
        """Test token without user ID."""
        credentials = HTTPAuthorizationCredentials(scheme="Bearer", credentials="valid_token")

        with patch("app.core.dependencies.verify_jwt_token") as mock_verify:
            mock_verify.return_value = {}

            with pytest.raises(HTTPException) as exc_info:
                await get_current_user(credentials, mock_db_session)

            assert exc_info.value.status_code == status.HTTP_401_UNAUTHORIZED

    @pytest.mark.asyncio
    async def test_get_current_user_exception(self, mock_db_session):
        """Test exception handling."""
        credentials = HTTPAuthorizationCredentials(scheme="Bearer", credentials="valid_token")

        with patch("app.core.dependencies.verify_jwt_token") as mock_verify:
            mock_verify.side_effect = Exception("Unexpected error")

            with pytest.raises(HTTPException) as exc_info:
                await get_current_user(credentials, mock_db_session)

            assert exc_info.value.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR

    @pytest.mark.asyncio
    async def test_get_client_s3(self):
        """Test creating S3 client."""
        client = await get_client_s3()

        assert client is not None
        assert client.bucket_name == settings.BUCKET_NAME