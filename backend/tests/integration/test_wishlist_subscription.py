import pytest


class TestScenario18WishlistSubscription:

    @pytest.mark.asyncio
    async def test_positive_subscribe_to_wishlist(
        self, client, test_users, test_wishlists, auth_headers
    ):
        wishlist_id = test_wishlists["wishlist_a_public"].id
        subscribe_data = {"target_wishlist_id": wishlist_id}

        response = await client.post(
            "/v1/subscriptions/wishlists",
            json=subscribe_data,
            headers=auth_headers["user_b"]
        )

        assert response.status_code == 200
        message = response.json().get("message", "")
        assert "Subscribed to thish wishlist successfully" in message

    @pytest.mark.asyncio
    async def test_positive_get_wishlist_subscriptions(
        self, client, auth_headers
    ):
        response = await client.get(
            "/v1/subscriptions/my/wishlists?limit=10",
            headers=auth_headers["user_a"]
        )

        assert response.status_code == 200
        assert "subscriptions" in response.json()

    @pytest.mark.asyncio
    async def test_positive_check_wishlist_subscription(
        self, client, test_users, test_wishlists, auth_headers
    ):
        wishlist_id = test_wishlists["wishlist_a_public"].id
        subscribe_data = {"target_wishlist_id": wishlist_id}

        await client.post(
            "/v1/subscriptions/wishlists",
            json=subscribe_data,
            headers=auth_headers["user_b"]
        )

        response = await client.get(
            f"/v1/subscriptions/check/wishlist/{wishlist_id}",
            headers=auth_headers["user_b"]
        )

        assert response.status_code == 200
        assert response.json()["is_subscribed"] is True

    @pytest.mark.asyncio
    async def test_negative_subscribe_to_own_wishlist(
        self, client, test_users, test_wishlists, auth_headers
    ):
        wishlist_id = test_wishlists["wishlist_a_public"].id
        subscribe_data = {"target_wishlist_id": wishlist_id}

        response = await client.post(
            "/v1/subscriptions/wishlists",
            json=subscribe_data,
            headers=auth_headers["user_a"]
        )

        assert response.status_code == 400

    @pytest.mark.asyncio
    async def test_negative_subscribe_without_auth(
        self, client, test_wishlists
    ):
        wishlist_id = test_wishlists["wishlist_a_public"].id
        subscribe_data = {"target_wishlist_id": wishlist_id}

        response = await client.post(
            "/v1/subscriptions/wishlists",
            json=subscribe_data
        )

        assert response.status_code == 401
