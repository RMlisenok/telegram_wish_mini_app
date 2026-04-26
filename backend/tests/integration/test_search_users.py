import pytest


class TestScenario10SearchUsers:

    @pytest.mark.asyncio
    async def test_positive_get_all_users(
        self, client, test_users, auth_headers
    ):
        response = await client.get(
            "/v1/users/all?limit=10",
            headers=auth_headers["user_a"]
        )

        assert response.status_code == 200
        assert isinstance(response.json(), list)
        assert len(response.json()) >= 1

        # Проверяем структуру ответа
        user = response.json()[0]
        assert "id" in user
        assert "name" in user
        assert "telegram_id" in user

    @pytest.mark.asyncio
    async def test_positive_get_all_users_without_limit(
        self, client, auth_headers
    ):
        response = await client.get(
            "/v1/users/all",
            headers=auth_headers["user_a"]
        )

        assert response.status_code == 200
        assert isinstance(response.json(), list)

    @pytest.mark.asyncio
    async def test_positive_get_user_by_id(
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
        assert response.json()["id"] == test_users["user_a"].id

    @pytest.mark.asyncio
    async def test_positive_get_own_profile(
        self, client, auth_headers
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
        assert "wishlist_last_update" in response.json()
        assert "subscription" in response.json()
        assert "subsсribers" in response.json()

    @pytest.mark.asyncio
    async def test_positive_get_user_with_limit(
        self, client, auth_headers
    ):
        response = await client.get(
            "/v1/users/all?limit=2",
            headers=auth_headers["user_a"]
        )

        assert response.status_code == 200
        assert len(response.json()) <= 2

    @pytest.mark.asyncio
    async def test_negative_get_nonexistent_user(
        self, client, auth_headers
    ):
        response = await client.get(
            "/v1/users/99999",
            headers=auth_headers["user_a"]
        )

        assert response.status_code == 404
        assert "User not found" in response.json().get("detail", "")

    @pytest.mark.asyncio
    async def test_negative_get_user_by_negative_id(
        self, client, auth_headers
    ):
        response = await client.get(
            "/v1/users/-1",
            headers=auth_headers["user_a"]
        )
        assert response.status_code in [400, 404, 422]

    @pytest.mark.asyncio
    async def test_positive_get_all_users_with_large_limit(
        self, client, auth_headers
    ):
        response = await client.get(
            "/v1/users/all?limit=100",
            headers=auth_headers["user_a"]
        )

        assert response.status_code == 200
        assert isinstance(response.json(), list)
        # В БД есть хотя бы 3 тестовых пользователя
        assert len(response.json()) >= 3
