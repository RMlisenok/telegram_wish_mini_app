import pytest


class TestScenario19PublicProfile:

    @pytest.mark.asyncio
    async def test_positive_get_public_profile(
        self, client, test_users, auth_headers
    ):
        response = await client.get(
            f"/v1/users/{test_users['user_a'].id}",
            headers=auth_headers["user_b"]
        )

        assert response.status_code == 200
        assert "id" in response.json()
        assert "name" in response.json()
        assert "telegram_id" in response.json()
        assert response.json()["name"] == "Анна"

    @pytest.mark.asyncio
    async def test_positive_get_own_profile(
        self, client, test_users, auth_headers
    ):

        response = await client.get(
            "/v1/users/me",
            headers=auth_headers["user_a"]
        )

        assert response.status_code == 200
        assert "telegram_id" in response.json()
        assert "name" in response.json()
        assert "total_wish" in response.json()
        assert "total_wishlist" in response.json()
        assert "subscription" in response.json()
        assert "subsсribers" in response.json()

    @pytest.mark.asyncio
    async def test_positive_profile_contains_subscriptions_when_public(
        self, client, test_users, auth_headers
    ):

        # Включаем отображение подписок
        await client.put(
            "/v1/users/me",
            json={"show_sub": True},
            headers=auth_headers["user_a"]
        )

        response = await client.get(
            f"/v1/users/{test_users['user_a'].id}",
            headers=auth_headers["user_b"]
        )

        assert response.status_code == 200
        assert "name" in response.json()

    @pytest.mark.asyncio
    async def test_positive_get_user_without_avatar(
        self, client, test_users, auth_headers
    ):

        # Создаем пользователя без фото
        user_data = {
            "telegram_id": 777888999,
            "name": "Без Фото"
        }

        create_response = await client.post(
            "/v1/users/user_test_create",
            json=user_data,
            headers=auth_headers["user_a"]
        )
        assert create_response.status_code == 200
        new_user_id = create_response.json()["id"]

        response = await client.get(
            f"/v1/users/{new_user_id}",
            headers=auth_headers["user_b"]
        )

        assert response.status_code == 200
        assert response.json()["name"] == "Без Фото"
        assert response.json().get("photo") is None

    @pytest.mark.asyncio
    async def test_positive_get_public_profile_without_auth(
        self, client, test_users
    ):

        response = await client.get(
            f"/v1/users/{test_users['user_a'].id}"
        )

        assert response.status_code == 200
        assert "name" in response.json()

    @pytest.mark.asyncio
    async def test_negative_get_nonexistent_profile(
        self, client, auth_headers
    ):

        response = await client.get(
            "/v1/users/99999",
            headers=auth_headers["user_a"]
        )

        assert response.status_code == 404
        assert "User not found" in response.json().get("detail", "")

    @pytest.mark.asyncio
    async def test_negative_profile_privacy_settings(
        self, client, test_users, auth_headers
    ):

        # Отключаем отображение подписок
        await client.put(
            "/v1/users/me",
            json={"show_sub": False},
            headers=auth_headers["user_a"]
        )

        response = await client.get(
            f"/v1/users/{test_users['user_a'].id}",
            headers=auth_headers["user_b"]
        )

        assert response.status_code == 200
        assert "id" in response.json()
        assert "name" in response.json()
