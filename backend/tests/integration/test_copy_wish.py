import pytest


class TestScenario8CopyWish:

    @pytest.mark.asyncio
    async def test_positive_copy_wish_to_another_wishlist(
        self, client, test_users, test_wishlists, auth_headers
    ):
        # Шаг 1: Создаем желание
        wish_data = {
            "name": "Копируемое желание",
            "description": "Это желание будет скопировано",
            "price": 1000.00,
            "currency": "RUB"
        }

        create_response = await client.post(
            "/v1/wishes/",
            json=wish_data,
            headers=auth_headers["user_a"]
        )
        assert create_response.status_code == 201
        wish_id = create_response.json()["id"]

        # Шаг 2: Добавляем желание в первый вишлист
        wishlist_a_id = test_wishlists["wishlist_a_public"].id
        connect_data = {
            "wishlist_id": wishlist_a_id,
            "wish_id": wish_id,
            "is_pinned": False,
            "order_position": 0
        }

        add_response = await client.post(
            f"/v1/wishlists/{wishlist_a_id}/wishes",
            json=connect_data,
            headers=auth_headers["user_a"]
        )
        assert add_response.status_code == 201

        # Шаг 3: Копируем желание во второй вишлист
        wishlist_b_id = test_wishlists["wishlist_b"].id
        copy_data = {
            "wishlist_id": wishlist_b_id,
            "wish_id": wish_id,
            "is_pinned": False,
            "order_position": 0
        }

        copy_response = await client.post(
            f"/v1/wishlists/{wishlist_b_id}/wishes",
            json=copy_data,
            headers=auth_headers["user_a"]
        )

        assert copy_response.status_code == 201
        assert copy_response.json()["wish_id"] == wish_id
        assert copy_response.json()["wishlist_id"] == wishlist_b_id

        # Шаг 4: Проверяем, что желание появилось в обоих вишлистах
        # Проверяем первый вишлист
        get_wishlist_a = await client.get(
            f"/v1/wishlists/{wishlist_a_id}/wishes",
            headers=auth_headers["user_a"]
        )
        assert get_wishlist_a.status_code == 200
        wishes_a = get_wishlist_a.json()
        wish_ids_a = [w["id"] for w in wishes_a]
        assert wish_id in wish_ids_a

        # Проверяем второй вишлист
        get_wishlist_b = await client.get(
            f"/v1/wishlists/{wishlist_b_id}/wishes",
            headers=auth_headers["user_a"]
        )
        assert get_wishlist_b.status_code == 200
        wishes_b = get_wishlist_b.json()
        wish_ids_b = [w["id"] for w in wishes_b]
        assert wish_id in wish_ids_b

    @pytest.mark.asyncio
    async def test_negative_copy_to_nonexistent_wishlist(
        self, client, test_users, auth_headers
    ):
        # Создаем желание
        wish_data = {
            "name": "Тестовое желание",
            "price": 500,
            "currency": "RUB"
        }

        create_response = await client.post(
            "/v1/wishes/",
            json=wish_data,
            headers=auth_headers["user_a"]
        )
        assert create_response.status_code == 201
        wish_id = create_response.json()["id"]

        # Пытаемся добавить в несуществующий вишлист
        connect_data = {
            "wishlist_id": 99999,
            "wish_id": wish_id,
            "is_pinned": False,
            "order_position": 0
        }

        response = await client.post(
            "/v1/wishlists/99999/wishes",
            json=connect_data,
            headers=auth_headers["user_a"]
        )

        assert response.status_code == 400

    @pytest.mark.asyncio
    async def test_negative_copy_nonexistent_wish(
        self, client, test_wishlists, auth_headers
    ):
        wishlist_id = test_wishlists["wishlist_a_public"].id
        connect_data = {
            "wishlist_id": wishlist_id,
            "wish_id": 99999,
            "is_pinned": False,
            "order_position": 0
        }

        response = await client.post(
            f"/v1/wishlists/{wishlist_id}/wishes",
            json=connect_data,
            headers=auth_headers["user_a"]
        )

        assert response.status_code == 400
        msg = response.json().get("detail", "")
        assert "Failed to add wish to wishlist" in msg
