import pytest


class TestScenario2WishCreation:

    @pytest.mark.asyncio
    async def test_positive_create_wish_and_link_to_wishlist(
        self, client, test_wishlists, auth_headers
    ):
        """
        Позитивный сценарий: 
        1. POST /v1/wishes/ - создание желания
        2. POST /v1/wishlists/{wishlist_id}/wishes - привязка к вишлисту
        """
        wish_data = {
            "name": "Новое желание",
            "description": "Описание желания",
            "price": 2500.00,
            "currency": "RUB",
            "url_gift": "https://example.com/gift"
        }

        response_create = await client.post(
            "/v1/wishes/",
            json=wish_data,
            headers=auth_headers["user_a"]
        )

        assert response_create.status_code == 201
        wish_id = response_create.json()["id"]
        assert response_create.json()["name"] == "Новое желание"

        wishlist_id = test_wishlists["wishlist_a_public"].id
        connect_data = {
            "wishlist_id": wishlist_id,
            "wish_id": wish_id,
            "is_pinned": False,
            "order_position": 0
        }

        response_link = await client.post(
            f"/v1/wishlists/{wishlist_id}/wishes",
            json=connect_data,
            headers=auth_headers["user_a"]
        )

        assert response_link.status_code == 201
        assert response_link.json()["wish_id"] == wish_id
        assert response_link.json()["wishlist_id"] == wishlist_id

        response_get = await client.get(
            f"/v1/wishlists/{wishlist_id}/wishes",
            headers=auth_headers["user_a"]
        )

        assert response_get.status_code == 200
        wishes = response_get.json()
        wish_ids = [w["id"] for w in wishes]
        assert wish_id in wish_ids

    @pytest.mark.asyncio
    async def test_negative_invalid_wish_data(
        self, client, auth_headers
    ):
        """
        Негативный сценарий: Создание желания с некорректными данными
        """
        invalid_data = {
            "price": 1000,
            "currency": "RUB"
        }
        response = await client.post(
            "/v1/wishes/",
            json=invalid_data,
            headers=auth_headers["user_a"]
        )

        assert response.status_code in [400, 422]

        invalid_price_data = {
            "name": "Тест",
            "price": -100,
            "currency": "RUB"
        }

        response2 = await client.post(
            "/v1/wishes/",
            json=invalid_price_data,
            headers=auth_headers["user_a"]
        )

        assert response2.status_code in [400, 422]

    @pytest.mark.asyncio
    async def test_negative_nonexistent_wishlist(
        self, client, auth_headers
    ):
        """
        Негативный сценарий: Привязка к несуществующему вишлисту
        """
        wish_data = {"name": "Тестовое желание", "price": 1000, "currency": "RUB"}

        response_create = await client.post(
            "/v1/wishes/",
            json=wish_data,
            headers=auth_headers["user_a"]
        )

        assert response_create.status_code == 201
        wish_id = response_create.json()["id"]

        connect_data = {"wishlist_id": 99999, "wish_id": wish_id}

        response_link = await client.post(
            "/v1/wishlists/99999/wishes",
            json=connect_data,
            headers=auth_headers["user_a"]
        )

        assert response_link.status_code in [400, 404, 422]
