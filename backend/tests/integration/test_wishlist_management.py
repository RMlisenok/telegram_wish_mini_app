import pytest


class TestScenario11WishlistManagement:

    @pytest.mark.asyncio
    async def test_positive_create_wishlist(
        self, client, auth_headers
    ):
        wishlist_data = {
            "name": "Мой новый вишлист",
            "description": "Описание вишлиста",
            "typeprivacy": "public"
        }

        response = await client.post(
            "/v1/wishlists/",
            json=wishlist_data,
            headers=auth_headers["user_a"]
        )

        assert response.status_code == 201
        assert response.json()["name"] == "Мой новый вишлист"
        assert response.json()["typeprivacy"] == "public"
        assert "id" in response.json()

    @pytest.mark.asyncio
    async def test_positive_create_private_wishlist(
        self, client, auth_headers
    ):
        wishlist_data = {
            "name": "Секретный вишлист",
            "description": "Только для меня",
            "typeprivacy": "private"
        }

        response = await client.post(
            "/v1/wishlists/",
            json=wishlist_data,
            headers=auth_headers["user_a"]
        )

        assert response.status_code == 201
        assert response.json()["typeprivacy"] == "private"

    @pytest.mark.asyncio
    async def test_positive_get_user_wishlists(
        self, client, auth_headers
    ):

        response = await client.get(
            "/v1/wishlists/?limit=10",
            headers=auth_headers["user_a"]
        )

        assert response.status_code == 200
        assert isinstance(response.json(), list)

        if len(response.json()) > 0:
            assert "name" in response.json()[0]
            assert "typeprivacy" in response.json()[0]

    @pytest.mark.asyncio
    async def test_positive_get_wishlist_by_id(
        self, client, test_wishlists, auth_headers
    ):
        wishlist_id = test_wishlists["wishlist_a_public"].id

        response = await client.get(
            f"/v1/wishlists/{wishlist_id}",
            headers=auth_headers["user_a"]
        )

        assert response.status_code == 200
        assert response.json()["id"] == wishlist_id
        assert response.json()["name"] == "Мои желания"

    @pytest.mark.asyncio
    async def test_positive_update_wishlist(
        self, client, test_wishlists, auth_headers
    ):
        wishlist_id = test_wishlists["wishlist_a_public"].id
        update_data = {
            "name": "Обновленное название",
            "description": "Новое описание"
        }

        response = await client.put(
            f"/v1/wishlists/{wishlist_id}",
            json=update_data,
            headers=auth_headers["user_a"]
        )

        assert response.status_code == 200
        assert response.json()["name"] == "Обновленное название"
        assert response.json()["description"] == "Новое описание"

    @pytest.mark.asyncio
    async def test_positive_delete_wishlist(
        self, client, auth_headers
    ):
        """
        Позитивный сценарий: Удаление вишлиста
        """
        # Сначала создаем вишлист с правильными полями
        wishlist_data = {
            "name": "Вишлист для удаления"
        }
        create_response = await client.post(
            "/v1/wishlists/",
            json=wishlist_data,
            headers=auth_headers["user_a"]
        )
        # Если создание вернуло 422, пробуем с description
        if create_response.status_code == 422:
            wishlist_data = {
                "name": "Вишлист для удаления",
                "description": "Тестовое описание",
                "typeprivacy": "public"
            }
            create_response = await client.post(
                "/v1/wishlists/",
                json=wishlist_data,
                headers=auth_headers["user_a"]
            )
        assert create_response.status_code == 201
        wishlist_id = create_response.json()["id"]
        # Удаляем вишлист
        response = await client.delete(
            f"/v1/wishlists/{wishlist_id}",
            headers=auth_headers["user_a"]
        )

        assert response.status_code == 204

        # Проверяем, что вишлист удален
        get_response = await client.get(
            f"/v1/wishlists/{wishlist_id}",
            headers=auth_headers["user_a"]
        )
        assert get_response.status_code == 404

    @pytest.mark.asyncio
    async def test_negative_create_wishlist_without_name(
        self, client, auth_headers
    ):
        """
        Негативный сценарий: Создание вишлиста без названия
        """
        wishlist_data = {
            "description": "Нет названия",
            "typeprivacy": "public"
        }

        response = await client.post(
            "/v1/wishlists/",
            json=wishlist_data,
            headers=auth_headers["user_a"]
        )

        assert response.status_code == 422

    @pytest.mark.asyncio
    async def test_negative_create_wishlist_invalid_privacy(
        self, client, auth_headers
    ):
        wishlist_data = {
            "name": "Тестовый вишлист",
            "typeprivacy": "invalid_type"
        }

        response = await client.post(
            "/v1/wishlists/",
            json=wishlist_data,
            headers=auth_headers["user_a"]
        )

        assert response.status_code in [400, 422]

    @pytest.mark.asyncio
    async def test_negative_get_nonexistent_wishlist(
        self, client, auth_headers
    ):
        """
        Негативный сценарий: Получение несуществующего вишлиста
        """
        response = await client.get(
            "/v1/wishlists/99999",
            headers=auth_headers["user_a"]
        )

        assert response.status_code == 404
        assert "Wishlist not found" in response.json().get("detail", "")

    @pytest.mark.asyncio
    async def test_negative_update_nonexistent_wishlist(
        self, client, auth_headers
    ):
        update_data = {"name": "Новое название"}

        response = await client.put(
            "/v1/wishlists/99999",
            json=update_data,
            headers=auth_headers["user_a"]
        )

        assert response.status_code in [404, 422]

    @pytest.mark.asyncio
    async def test_negative_delete_nonexistent_wishlist(
        self, client, auth_headers
    ):

        response = await client.delete(
            "/v1/wishlists/99999",
            headers=auth_headers["user_a"]
        )

        assert response.status_code == 404
