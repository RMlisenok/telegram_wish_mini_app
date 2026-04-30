import pytest


class TestScenario16WishlistAccess:

    @pytest.mark.asyncio
    async def test_positive_get_wishes_from_public_wishlist(
        self, client, test_users, test_wishlists, auth_headers
    ):
        """
        Позитивный сценарий: Получение желаний из публичного вишлиста
        GET /v1/wishlists/{wishlist_id}/wishes
        """
        wishlist_id = test_wishlists["wishlist_a_public"].id

        response = await client.get(
            f"/v1/wishlists/{wishlist_id}/wishes",
            headers=auth_headers["user_b"]
        )

        assert response.status_code == 200
        assert isinstance(response.json(), list)

    @pytest.mark.asyncio
    async def test_positive_get_wishes_from_own_private_wishlist(
        self, client, test_users, test_wishlists, auth_headers
    ):
        wishlist_id = test_wishlists["wishlist_a_private"].id

        response = await client.get(
            f"/v1/wishlists/{wishlist_id}/wishes",
            headers=auth_headers["user_a"]
        )

        assert response.status_code == 200
        assert isinstance(response.json(), list)

    @pytest.mark.asyncio
    async def test_negative_access_private_wishlist_without_permission(
        self, client, test_users, test_wishlists, auth_headers
    ):
        wishlist_id = test_wishlists["wishlist_a_private"].id

        response = await client.get(
            f"/v1/wishlists/{wishlist_id}/wishes",
            headers=auth_headers["user_b"]
        )

        assert response.status_code == 200
        result = response.json().get("message", "").lower()
        assert "you dont have access" in result

    @pytest.mark.asyncio
    async def test_negative_get_wishes_from_nonexistent_wishlist(
        self, client, auth_headers
    ):
        response = await client.get(
            "/v1/wishlists/99999/wishes",
            headers=auth_headers["user_a"]
        )

        assert response.status_code == 404
        assert "WIshlist not found" in response.json().get("detail", "")

    @pytest.mark.asyncio
    async def test_negative_get_wishes_without_auth(
        self, client, test_wishlists
    ):
        wishlist_id = test_wishlists["wishlist_a_public"].id

        response = await client.get(
            f"/v1/wishlists/{wishlist_id}/wishes"
        )

        assert response.status_code == 401
