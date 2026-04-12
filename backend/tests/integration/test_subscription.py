import pytest
import asyncio


class TestScenario4Subscription:

    @pytest.mark.asyncio
    async def test_positive_subscribe_to_user(
        self, client, test_users, auth_headers
    ):
        """Позитивный сценарий: Подписка пользователя B на пользователя A"""
        subscribe_data = {"target_user_id": test_users["user_a"].id}

        response = await client.post(
            "/v1/subscriptions/users",
            json=subscribe_data,
            headers=auth_headers["user_b"]
        )

        assert response.status_code == 200
        assert "Subscribed to this user successfully" in response.json()["message"]

        check_response = await client.get(
            f"/v1/subscriptions/check/user/{test_users['user_a'].id}",
            headers=auth_headers["user_b"]
        )

        assert check_response.status_code == 200
        assert check_response.json()["is_subscribed"] is True

    @pytest.mark.asyncio
    async def test_negative_subscribe_to_nonexistent_user(
        self, client, auth_headers
    ):
        """Подписка на несуществующего пользователя"""
        subscribe_data = {"target_user_id": 99999}

        response = await client.post(
            "/v1/subscriptions/users",
            json=subscribe_data,
            headers=auth_headers["user_b"]
        )

        assert response.status_code == 400
        assert "Cannot subscribe to this user" in response.json().get("detail", "")

    @pytest.mark.asyncio
    async def test_negative_subscribe_to_self(
        self, client, test_users, auth_headers
    ):
        """Попытка подписаться на самого себя"""
        subscribe_data = {"target_user_id": test_users["user_b"].id}

        response = await client.post(
            "/v1/subscriptions/users",
            json=subscribe_data,
            headers=auth_headers["user_b"]
        )

        assert response.status_code == 400
        assert "Cannot subscribe to this user" in response.json().get("detail", "")

    @pytest.mark.asyncio
    async def test_negative_duplicate_subscription(
        self, client, test_users, auth_headers
    ):
        """Повторная подписка на того же пользователя"""
        subscribe_data = {"target_user_id": test_users["user_a"].id}

        response1 = await client.post(
            "/v1/subscriptions/users",
            json=subscribe_data,
            headers=auth_headers["user_b"]
        )
        assert response1.status_code == 200

        response2 = await client.post(
            "/v1/subscriptions/users",
            json=subscribe_data,
            headers=auth_headers["user_b"]
        )

        assert response2.status_code == 400
        assert "Cannot subscribe to this user" in response2.json().get("detail", "")

    @pytest.mark.asyncio
    async def test_get_my_subscribers(
        self, client, test_users, auth_headers
    ):
        """Получение списка подписчиков пользователя"""
        subscribe_data = {"target_user_id": test_users["user_a"].id}

        await client.post(
            "/v1/subscriptions/users",
            json=subscribe_data,
            headers=auth_headers["user_b"]
        )

        await client.post(
            "/v1/subscriptions/users",
            json=subscribe_data,
            headers=auth_headers["user_c"]
        )

        subscribers_response = await client.get(
            "/v1/subscriptions/my/subscribers",
            headers=auth_headers["user_a"]
        )

        assert subscribers_response.status_code == 200
        subscribers = subscribers_response.json().get("subscribers", [])

        assert len(subscribers) >= 2

        subscriber_ids = [s.get("user_id") for s in subscribers]
        assert test_users["user_b"].id in subscriber_ids
        assert test_users["user_c"].id in subscriber_ids

    @pytest.mark.asyncio
    async def test_unsubscribe_from_user_debug(
        self, client, test_users, auth_headers
    ):
        subscribe_data = {"target_user_id": test_users["user_a"].id}

        response_sub = await client.post(
            "/v1/subscriptions/users",
            json=subscribe_data,
            headers=auth_headers["user_b"]
        )
        assert response_sub.status_code == 200

        check_before = await client.get(
            f"/v1/subscriptions/check/user/{test_users['user_a'].id}",
            headers=auth_headers["user_b"]
        )
        assert check_before.json()["is_subscribed"] is True

        response_unsub = await client.delete(
            f"/v1/subscriptions/users/{test_users['user_a'].id}",
            headers=auth_headers["user_b"]
        )
        assert response_unsub.status_code == 200
        assert "Unsubscribed successfully" in response_unsub.json()["message"]
