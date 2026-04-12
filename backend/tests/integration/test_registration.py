import pytest
from unittest.mock import patch


class TestScenario1Registration:

    @pytest.mark.asyncio
    async def test_positive_registration(self, client, db_session, mock_telegram_bot):
        """
        Позитивный сценарий: Успешная регистрация через POST /v1/auth/test
        """
        new_user_data = {
            "telegram_id": 111111111,
            "name": "Новый Пользователь",
            "birth_date": "1995-05-15"
        }

        response = await client.post("/v1/auth/test", json=new_user_data)

        assert response.status_code == 200
        data = response.json()
        assert "token" in data
        assert "user" in data
        assert data["success"] is True

        from app.services.user_service import UserService
        user_service = UserService(db_session)
        user = await user_service.get_user_by_telegram_id(111111111)
        assert user is not None
        assert user.name == "Новый Пользователь"

    @pytest.mark.asyncio
    async def test_negative_duplicate_registration(self, client, test_users):
        """
        Негативный сценарий: Попытка регистрации уже существующего пользователя
        """
        existing_user_data = {
            "telegram_id": test_users["user_a"].telegram_id,
            "name": "Дубликат",
            "birth_date": "1990-01-01"
        }

        response = await client.post("/v1/users/user_test_create", json=existing_user_data)

        assert response.status_code == 400
        assert "already exists" in response.json().get("detail", "")

    @pytest.mark.asyncio
    async def test_negative_telegram_api_unavailable(self, client):
        """
        Негативный сценарий: Telegram API недоступен (неверная подпись)
        Используем эндпоинт /v1/auth/telegram, который проверяет подпись
        """
        with patch("app.api.routers.auth.verify_tg_init_data", return_value=False):
            auth_data = {
                "initData": "invalid_init_data",
                "user": {
                    "id": 123456789,
                    "first_name": "Test",
                    "last_name": "User"
                }
            }

            response = await client.post("/v1/auth/telegram", json=auth_data)

            # Ожидаем ошибку авторизации 401
            assert response.status_code == 401
            assert "Invalid Telegram signature" in response.json().get("detail", "")

    @pytest.mark.asyncio
    async def test_negative_missing_init_data(self, client):
        """
        Негативный сценарий: Отсутствует initData в запросе
        """
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
        """
        Негативный сценарий: Отсутствует user в запросе
        """
        auth_data = {
            "initData": "some_init_data"
        }

        response = await client.post("/v1/auth/telegram", json=auth_data)

        assert response.status_code == 400
        assert "Invalid user data" in response.json().get("detail", "")
