import pytest


class TestScenario5AccessRequest:

    @pytest.mark.asyncio
    async def test_positive_create_access_request(
        self, client, test_users, test_wishlists, auth_headers
    ):
        private_wishlist_id = test_wishlists["wishlist_a_private"].id
        request_data = {"wishlist_id": private_wishlist_id}

        response = await client.post(
            "/v1/access-requests/",
            json=request_data,
            headers=auth_headers["user_b"]
        )

        assert response.status_code == 201
        assert response.json()["wishlist_id"] == private_wishlist_id
        assert response.json()["status"].lower() == "pending"
        assert "id" in response.json()

    @pytest.mark.asyncio
    async def test_positive_approve_access_request(
        self, client, test_users, test_wishlists, auth_headers
    ):
        private_wishlist_id = test_wishlists["wishlist_a_private"].id
        request_data = {"wishlist_id": private_wishlist_id}

        create_response = await client.post(
            "/v1/access-requests/",
            json=request_data,
            headers=auth_headers["user_b"]
        )
        assert create_response.status_code == 201
        request_id = create_response.json()["id"]

        approve_data = {"status": "approved"}

        approve_response = await client.patch(
            f"/v1/access-requests/{request_id}",
            json=approve_data,
            headers=auth_headers["user_a"]
        )

        if approve_response.status_code == 422:
            approve_data = {"status": "APPROVED"}
            approve_response = await client.patch(
                f"/v1/access-requests/{request_id}",
                json=approve_data,
                headers=auth_headers["user_a"]
            )

        if approve_response.status_code == 422:
            approve_response = await client.patch(
                f"/v1/access-requests/{request_id}?status=approved",
                headers=auth_headers["user_a"]
            )

        assert approve_response.status_code == 200, (
            f"Expected 200, got {approve_response.status_code}: "
            f"{approve_response.text}"
        )
        assert approve_response.json()["status"].lower() == "approved"

    @pytest.mark.asyncio
    async def test_positive_reject_access_request(
        self, client, test_users, test_wishlists, auth_headers
    ):
        private_wishlist_id = test_wishlists["wishlist_a_private"].id
        request_data = {"wishlist_id": private_wishlist_id}

        create_response = await client.post(
            "/v1/access-requests/",
            json=request_data,
            headers=auth_headers["user_c"]
        )
        assert create_response.status_code == 201
        request_id = create_response.json()["id"]

        reject_data = {"status": "rejected"}

        reject_response = await client.patch(
            f"/v1/access-requests/{request_id}",
            json=reject_data,
            headers=auth_headers["user_a"]
        )

        if reject_response.status_code == 422:
            reject_data = {"status": "REJECTED"}
            reject_response = await client.patch(
                f"/v1/access-requests/{request_id}",
                json=reject_data,
                headers=auth_headers["user_a"]
            )

        assert reject_response.status_code == 200, (
            f"Expected 200, got {reject_response.status_code}"
        )
        assert reject_response.json()["status"].lower() == "rejected"

    @pytest.mark.asyncio
    async def test_get_my_access_requests(
        self, client, test_users, test_wishlists, auth_headers
    ):
        private_wishlist_id = test_wishlists["wishlist_a_private"].id
        request_data = {"wishlist_id": private_wishlist_id}

        await client.post(
            "/v1/access-requests/",
            json=request_data,
            headers=auth_headers["user_b"]
        )

        response = await client.get(
            "/v1/access-requests/my/requests",
            headers=auth_headers["user_b"]
        )

        assert response.status_code == 200
        assert "requests" in response.json()
        assert len(response.json()["requests"]) >= 1

    @pytest.mark.asyncio
    async def test_get_requests_for_my_wishlists(
        self, client, test_users, test_wishlists, auth_headers
    ):
        """
        Позитивный сценарий: Получение заявок на свои вишлисты
        GET /v1/access-requests/my/wishlists
        """
        private_wishlist_id = test_wishlists["wishlist_a_private"].id
        request_data = {"wishlist_id": private_wishlist_id}

        await client.post(
            "/v1/access-requests/",
            json=request_data,
            headers=auth_headers["user_b"]
        )

        response = await client.get(
            "/v1/access-requests/my/wishlists",
            headers=auth_headers["user_a"]
        )

        assert response.status_code == 200
        assert "requests" in response.json()

    @pytest.mark.asyncio
    async def test_negative_access_request_to_nonexistent_wishlist(
        self, client, auth_headers
    ):
        """
        Негативный сценарий: Заявка на несуществующий вишлист
        """
        request_data = {"wishlist_id": 99999}

        response = await client.post(
            "/v1/access-requests/",
            json=request_data,
            headers=auth_headers["user_b"]
        )

        assert response.status_code == 400
