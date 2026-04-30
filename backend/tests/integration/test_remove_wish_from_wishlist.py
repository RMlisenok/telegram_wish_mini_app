import pytest


class TestScenario20RemoveWishFromWishlist:

    @pytest.mark.asyncio
    async def test_positive_remove_wish_from_wishlist(
        self, client, test_users, test_wishlists, auth_headers
    ):
        wish_data = {
            "name": "Желание для удаления",
            "price": 1000,
            "currency": "RUB"
        }

        create_response = await client.post(
            "/v1/wishes/",
            json=wish_data,
            headers=auth_headers["user_a"]
        )
        assert create_response.status_code == 201
        wish_id = create_response.json()["id"]

        # Добавляем желание в вишлист
        wishlist_id = test_wishlists["wishlist_a_public"].id
        connect_data = {
            "wishlist_id": wishlist_id,
            "wish_id": wish_id,
            "is_pinned": False,
            "order_position": 0
        }

        await client.post(
            f"/v1/wishlists/{wishlist_id}/wishes",
            json=connect_data,
            headers=auth_headers["user_a"]
        )

        # Проверяем, что желание есть в вишлисте
        get_before = await client.get(
            f"/v1/wishlists/{wishlist_id}/wishes",
            headers=auth_headers["user_a"]
        )
        wish_ids_before = [w["id"] for w in get_before.json()]
        assert wish_id in wish_ids_before

        # Удаляем желание из вишлиста
        response = await client.delete(
            f"/v1/wishlists/{wishlist_id}/wishes/{wish_id}",
            headers=auth_headers["user_a"]
        )

        assert response.status_code == 204

        # Проверяем, что желание удалено из вишлиста
        get_after = await client.get(
            f"/v1/wishlists/{wishlist_id}/wishes",
            headers=auth_headers["user_a"]
        )
        wish_ids_after = [w["id"] for w in get_after.json()]
        assert wish_id not in wish_ids_after

        # Проверяем, что желание осталось в системе
        get_wish = await client.get(
            f"/v1/wishes/{wish_id}",
            headers=auth_headers["user_a"]
        )
        assert get_wish.status_code == 200

    @pytest.mark.asyncio
    async def test_negative_remove_nonexistent_wish(
        self, client, test_wishlists, auth_headers
    ):

        wishlist_id = test_wishlists["wishlist_a_public"].id

        response = await client.delete(
            f"/v1/wishlists/{wishlist_id}/wishes/99999",
            headers=auth_headers["user_a"]
        )

        assert response.status_code == 404

    @pytest.mark.asyncio
    async def test_negative_remove_wish_from_nonexistent_wishlist(
        self, client, test_users, auth_headers
    ):
        # Создаем желание
        wish_data = {"name": "Тест", "price": 100, "currency": "RUB"}
        create_response = await client.post(
            "/v1/wishes/",
            json=wish_data,
            headers=auth_headers["user_a"]
        )
        assert create_response.status_code == 201
        wish_id = create_response.json()["id"]

        response = await client.delete(
            f"/v1/wishlists/99999/wishes/{wish_id}",
            headers=auth_headers["user_a"]
        )

        assert response.status_code == 404
