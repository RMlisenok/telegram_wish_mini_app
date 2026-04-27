import pytest
import asyncio # noqa


class TestScenario4Subscription:

    @pytest.mark.asyncio
    async def test_positive_subscribe_to_user(
        self, client, test_users, auth_headers
    ):
        subscribe_data = {"target_user_id": test_users["user_a"].id}

        response = await client.post(
            "/v1/subscriptions/users",
            json=subscribe_data,
            headers=auth_headers["user_b"]
        )

        assert response.status_code == 200
        msg = response.json()["message"]
        assert "Subscribed to this user successfully" in msg

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
        subscribe_data = {"target_user_id": 99999}

        response = await client.post(
            "/v1/subscriptions/users",
            json=subscribe_data,
            headers=auth_headers["user_b"]
        )

        assert response.status_code == 400
        msg = response.json().get("detail", "")
        assert "Cannot subscribe to this user" in msg

    @pytest.mark.asyncio
    async def test_negative_subscribe_to_self(
        self, client, test_users, auth_headers
    ):
        subscribe_data = {"target_user_id": test_users["user_b"].id}

        response = await client.post(
            "/v1/subscriptions/users",
            json=subscribe_data,
            headers=auth_headers["user_b"]
        )

        msg = response.json().get("detail", "")
        assert response.status_code == 400
        assert "Cannot subscribe to this user" in msg

    @pytest.mark.asyncio
    async def test_negative_duplicate_subscription(
        self, client, test_users, auth_headers
    ):
        subscribe_data = {"target_user_id": test_users["user_a"].id}

        # Первая подписка - успешна
        response1 = await client.post(
            "/v1/subscriptions/users",
            json=subscribe_data,
            headers=auth_headers["user_b"]
        )
        assert response1.status_code == 200

        # Вторая подписка - должна быть ошибка
        response2 = await client.post(
            "/v1/subscriptions/users",
            json=subscribe_data,
            headers=auth_headers["user_b"]
        )

        assert response2.status_code == 400
        msg = response2.json().get("detail", "")
        assert "Cannot subscribe to this user" in msg

    @pytest.mark.asyncio
    async def test_get_my_subscribers(
        self, client, test_users, auth_headers
    ):
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
