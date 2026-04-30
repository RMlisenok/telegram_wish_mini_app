import pytest
from unittest.mock import patch


class TestScenario1Registration:

    @pytest.mark.asyncio
    async def test_positive_registration(
        self,
        client,
        db_session,
        mock_telegram_bot
    ):
        """Позитивный сценарий: Успешная регистрация нового пользователя"""
        auth_data = {
            "initData": "valid_init_data_from_telegram",
            "user": {
                "id": 111111111,
                "first_name": "Новый",
                "last_name": "Пользователь",
                "username": "new_user",
                "photo_url": None
            }
        }

        with patch(
            "app.api.routers.auth.verify_tg_init_data",
            return_value=True
        ):
            response = await client.post("/v1/auth/telegram", json=auth_data)

        assert response.status_code == 200
        data = response.json()
        assert "token" in data
        assert "user" in data
        assert data["success"] is True
        assert data["user"]["name"] == "Новый Пользователь"

        # Проверяем, что пользователь создан в БД
        from app.services.user_service import UserService
        user_service = UserService(db_session)
        user = await user_service.get_user_by_telegram_id(111111111)
        assert user is not None
        assert user.name == "Новый Пользователь"

    @pytest.mark.asyncio
    async def test_negative_duplicate_registration(
        self, client, test_users, db_session
    ):
        existing_user = test_users["user_a"]

        auth_data = {
            "initData": "valid_init_data_from_telegram",
            "user": {
                "id": existing_user.telegram_id,
                "first_name": (
                    existing_user.name.split()[0]
                    if " " in existing_user.name
                    else existing_user.name
                ),
                "last_name": (
                    existing_user.name.split()[1]
                    if " " in existing_user.name
                    else ""
                ),
                "username": "existing_user",
                "photo_url": None
            }
        }

        with patch(
            "app.api.routers.auth.verify_tg_init_data",
            return_value=True
        ):
            response = await client.post("/v1/auth/telegram", json=auth_data)

        # При повторной регистрации должен вернуться существующий пользователь
        assert response.status_code == 200
        data = response.json()
        assert "token" in data
        assert "user" in data
        assert data["success"] is True
        # Имя должно остаться исходным, не "Дубликат"
        assert data["user"]["name"] == existing_user.name

    @pytest.mark.asyncio
    async def test_negative_telegram_api_unavailable(self, client):
        with patch(
            "app.api.routers.auth.verify_tg_init_data",
            return_value=False
        ):
            auth_data = {
                "initData": "invalid_init_data",
                "user": {
                    "id": 123456789,
                    "first_name": "Test",
                    "last_name": "User"
                }
            }

            response = await client.post("/v1/auth/telegram", json=auth_data)

            assert response.status_code == 401
            msg = response.json().get("detail", "")
            assert "Invalid Telegram signature" in msg

    @pytest.mark.asyncio
    async def test_negative_missing_init_data(self, client):
        auth_data = {
            "user": {
                "id": 123456789,
                "first_name": "Test"
            }
        }

        response = await client.post("/v1/auth/telegram", json=auth_data)

        assert response.status_code == 400
        assert "Invalid init data" in response.json().get("detail", "")

    @pytest.mark.asyncio
    async def test_negative_missing_user_data(self, client):
        auth_data = {
            "initData": "some_init_data"
        }

        response = await client.post("/v1/auth/telegram", json=auth_data)

        assert response.status_code == 400
        assert "Invalid user data" in response.json().get("detail", "")
