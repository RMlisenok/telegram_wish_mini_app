import pytest


class TestScenario17MarkWishCompleted:

    @pytest.mark.asyncio
    async def test_positive_mark_wish_as_completed(
        self, client, test_users, test_wishlists, auth_headers, db_session
    ):
        wish_data = {
            "name": "Исполняемое желание",
            "description": "Это желание будет исполнено",
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
        original_name = create_response.json()["name"]

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

        update_data = {
            "name": original_name,
            "status_is_finished": True
        }

        response = await client.put(
            f"/v1/wishes/{wish_id}",
            json=update_data,
            headers=auth_headers["user_a"]
        )

        assert response.status_code == 200
        assert response.json()["status_is_finished"] is True

        from app.services.wish_service import WishService
        wish_service = WishService(db_session)
        updated_wish = await wish_service.get_wish(wish_id)
        assert updated_wish.status_is_finished is True

        finished_response = await client.get(
            "/v1/wishes/finish?is_finish=true&limit=10",
            headers=auth_headers["user_a"]
        )

        assert finished_response.status_code == 200

    @pytest.mark.asyncio
    async def test_positive_get_finished_wishes(
        self, client, auth_headers
    ):
        response = await client.get(
            "/v1/wishes/finish?is_finish=true&limit=10",
            headers=auth_headers["user_a"]
        )

        assert response.status_code == 200
        assert isinstance(response.json(), list)

    @pytest.mark.asyncio
    async def test_positive_get_active_wishes(
        self, client, auth_headers
    ):
        response = await client.get(
            "/v1/wishes/finish?is_finish=false&limit=10",
            headers=auth_headers["user_a"]
        )

        assert response.status_code == 200
        assert isinstance(response.json(), list)

    @pytest.mark.asyncio
    async def test_negative_mark_nonexistent_wish_as_completed(
        self, client, auth_headers
    ):
        update_data = {
            "name": "Тест",
            "status_is_finished": True
        }

        response = await client.put(
            "/v1/wishes/99999",
            json=update_data,
            headers=auth_headers["user_a"]
        )

        assert response.status_code == 404
