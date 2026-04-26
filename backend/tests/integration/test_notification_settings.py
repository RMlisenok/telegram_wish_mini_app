import pytest


class TestScenario9NotificationSettings:

    @pytest.mark.asyncio
    async def test_positive_get_notification_settings(
        self, client, auth_headers
    ):
        """Получение настроек уведомлений"""
        response = await client.get(
            "/v1/settings/notifications",
            headers=auth_headers["user_a"]
        )

        assert response.status_code == 200
        assert "new_followers" in response.json()
        assert "access_requests" in response.json()
        assert "birt_before" in response.json()

    @pytest.mark.asyncio
    async def test_positive_update_notification_settings(
        self, client, auth_headers
    ):
        """Обновление всех настроек уведомлений"""
        update_data = {
            "new_followers": False,
            "access_requests": False,
            "birt_before": True,
            "birt_after": False
        }

        response = await client.patch(
            "/v1/settings/notifications",
            json=update_data,
            headers=auth_headers["user_a"]
        )

        assert response.status_code == 200
        assert response.json()["status"] == "success"
        assert response.json()["update_data"]["new_followers"] is False
        assert response.json()["update_data"]["access_requests"] is False
        assert response.json()["update_data"]["birt_before"] is True

    @pytest.mark.asyncio
    async def test_positive_update_single_setting(
        self, client, auth_headers
    ):
        """Обновление только одной настройки"""
        get_before = await client.get(
            "/v1/settings/notifications",
            headers=auth_headers["user_a"]
        )
        before_value = get_before.json().get("new_followers")

        update_data = {"new_followers": not before_value}

        response = await client.patch(
            "/v1/settings/notifications",
            json=update_data,
            headers=auth_headers["user_a"]
        )

        assert response.status_code == 200

        get_after = await client.get(
            "/v1/settings/notifications",
            headers=auth_headers["user_a"]
        )
        assert get_after.json()["new_followers"] is not before_value

    @pytest.mark.asyncio
    async def test_negative_update_invalid_settings(
        self, client, auth_headers
    ):
        # Сохраняем текущие настройки
        before = await client.get(
            "/v1/settings/notifications",
            headers=auth_headers["user_a"]
        )
        before_followers = before.json().get("new_followers")
        before_access = before.json().get("access_requests")

        # Передаем несуществующее поле (должно быть проигнорировано)
        invalid_data = {"invalid_field": True}

        response = await client.patch(
            "/v1/settings/notifications",
            json=invalid_data,
            headers=auth_headers["user_a"]
        )

        assert response.status_code == 200

        # Проверяем, что настройки НЕ изменились
        after = await client.get(
            "/v1/settings/notifications",
            headers=auth_headers["user_a"]
        )

        assert after.json().get("new_followers") == before_followers
        assert after.json().get("access_requests") == before_access

    @pytest.mark.asyncio
    async def test_negative_update_wrong_type(
        self, client, auth_headers
    ):
        invalid_data = {"new_followers": "not_a_boolean"}

        response = await client.patch(
            "/v1/settings/notifications",
            json=invalid_data,
            headers=auth_headers["user_a"]
        )

        assert response.status_code == 422

    @pytest.mark.asyncio
    async def test_negative_update_without_auth(
        self, client
    ):
        update_data = {"new_followers": False}

        response = await client.patch(
            "/v1/settings/notifications",
            json=update_data
        )

        assert response.status_code == 401
