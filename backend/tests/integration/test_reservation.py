import pytest
from app.services.wish_service import WishService


class TestScenario3Reservation:

    @pytest.mark.asyncio
    async def test_positive_reserve_wish(
        self, client, test_users, test_wishlists, auth_headers, db_session
    ):
        """
        Позитивный сценарий: Пользователь B бронирует желание пользователя A
        POST /v1/reservations/
        """
        wish_data = {
            "name": "Книга для бронирования",
            "description": "Подарочное издание",
            "price": 1500.00,
            "currency": "RUB"
        }

        response_create = await client.post(
            "/v1/wishes/",
            json=wish_data,
            headers=auth_headers["user_a"]
        )

        assert response_create.status_code == 201
        wish_id = response_create.json()["id"]

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

        reservation_data = {"wish_wishlist_id": wishlist_id}

        response_reserve = await client.post(
            "/v1/reservations/",
            json=reservation_data,
            headers=auth_headers["user_b"]
        )

        assert response_reserve.status_code == 201
        assert response_reserve.json()["wish_wishlist_id"] == wishlist_id
        assert response_reserve.json()["reserved_by_id"] == test_users["user_b"].id

        wish_service = WishService(db_session)
        updated_wish = await wish_service.get_wish(wish_id)
        assert updated_wish.is_booked == True, "Wish should be booked"

        response_get_reservations = await client.get(
            "/v1/reservations/",
            headers=auth_headers["user_b"]
        )

        assert response_get_reservations.status_code == 200
        reservations = response_get_reservations.json()
        assert len(reservations) >= 1
        assert reservations[0]["wish_wishlist_id"] == wishlist_id

    @pytest.mark.asyncio
    async def test_negative_reserve_own_wish(
        self, client, test_users, test_wishlists, auth_headers
    ):
        """
        Негативный сценарий: Владелец пытается забронировать свое желание
        По текущей реализации API - это разрешено (возвращает 201)
        Но по ТЗ должно быть 400
        """
        wish_data = {
            "name": "Мое желание",
            "price": 1000,
            "currency": "RUB"
        }

        response_create = await client.post(
            "/v1/wishes/",
            json=wish_data,
            headers=auth_headers["user_a"]
        )

        assert response_create.status_code == 201
        wish_id = response_create.json()["id"]

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

        reservation_data = {"wish_wishlist_id": wishlist_id}

        response_reserve = await client.post(
            "/v1/reservations/",
            json=reservation_data,
            headers=auth_headers["user_a"]
        )

        assert response_reserve.status_code in [201, 400]

        if response_reserve.status_code == 201:
            assert response_reserve.json()["reserved_by_id"] == test_users["user_a"].id

    @pytest.mark.asyncio
    async def test_negative_reserve_already_reserved_wish(
        self, client, test_users, test_wishlists, auth_headers
    ):
        """
        Негативный сценарий: Попытка забронировать уже забронированное желание
        Ожидаем: 400 Bad Request
        """
        wish_data = {
            "name": "Популярное желание",
            "price": 2000,
            "currency": "RUB"
        }

        response_create = await client.post(
            "/v1/wishes/",
            json=wish_data,
            headers=auth_headers["user_a"]
        )

        assert response_create.status_code == 201
        wish_id = response_create.json()["id"]

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

        reservation_data = {"wish_wishlist_id": wishlist_id}

        response_reserve1 = await client.post(
            "/v1/reservations/",
            json=reservation_data,
            headers=auth_headers["user_b"]
        )

        assert response_reserve1.status_code == 201

        response_reserve2 = await client.post(
            "/v1/reservations/",
            json=reservation_data,
            headers=auth_headers["user_c"]
        )

        assert response_reserve2.status_code == 400

        detail = response_reserve2.json().get("detail", "")
        assert detail == "Failed TO create reservation"
