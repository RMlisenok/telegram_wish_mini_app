import pytest


class TestScenario7BlockUser:

    @pytest.mark.asyncio
    async def test_positive_block_user(
        self, client, test_users, auth_headers
    ):

        block_data = {
            "blocked_id": test_users["user_a"].id,
            "block_profile": True,
            "block_wishlists": True
        }

        response = await client.post(
            f"/v1/users/block/{test_users['user_a'].id}",
            json=block_data,
            headers=auth_headers["user_b"]
        )

        assert response.status_code == 200
        assert response.json()["blocked_id"] == test_users["user_a"].id
        assert response.json()["block_profile"] is True
        assert response.json()["block_wishlists"] is True

    @pytest.mark.asyncio
    async def test_check_block_status(
        self, client, test_users, auth_headers
    ):
        # Сначала блокируем (B блокирует A)
        block_data = {
            "blocked_id": test_users["user_a"].id,
            "block_profile": True,
            "block_wishlists": True
        }

        await client.post(
            f"/v1/users/block/{test_users['user_a'].id}",
            json=block_data,
            headers=auth_headers["user_b"]
        )

        # Проверяем статус: A проверяет, заблокирован ли он пользователем B
        # Согласно вашему роутеру: GET /block/status/{user_id}?blocker_id=...
        # user_id - это ID пользователя, которого проверяем (A)
        # blocker_id - это ID того, кто мог заблокировать (B)
        user_id_a = test_users['user_a'].id
        user_id_b = test_users['user_b'].id
        url = f"/v1/users/block/status/{user_id_a}?blocker_id={user_id_b}"
        response = await client.get(
            url,
            headers=auth_headers["user_a"]
        )

        assert response.status_code == 200
        assert response.json()["is_blocked"] is True

    @pytest.mark.asyncio
    async def test_negative_block_self(
        self, client, test_users, auth_headers
    ):
        block_data = {
            "blocked_id": test_users["user_a"].id,
            "block_profile": True,
            "block_wishlists": True
        }

        response = await client.post(
            f"/v1/users/block/{test_users['user_a'].id}",
            json=block_data,
            headers=auth_headers["user_a"]
        )

        assert response.status_code == 400
        assert "Cannot block yourself" in response.json().get("detail", "")

    @pytest.mark.asyncio
    async def test_unblock_user(
        self, client, test_users, auth_headers
    ):
        """
        Позитивный сценарий: Разблокировка пользователя
        DELETE /v1/users/block/{blocked_id}
        """
        # Шаг 1: Блокируем
        block_data = {
            "blocked_id": test_users["user_a"].id,
            "block_profile": True,
            "block_wishlists": True
        }

        user_id_a = test_users['user_a'].id
        user_id_b = test_users['user_b'].id

        url_status = (
            f"/v1/users/block/status/"
            f"{user_id_a}?blocker_id={user_id_b}"
        )
        status_before = await client.get(
            url_status,
            headers=auth_headers["user_a"]
        )
        print(f"Before block: {status_before.json()['is_blocked']}")

        # Блокируем
        block_response = await client.post(
            f"/v1/users/block/{user_id_a}",
            json=block_data,
            headers=auth_headers["user_b"]
        )
        assert block_response.status_code == 200
        print(f"Block response: {block_response.status_code}")

        # Проверяем, что блокировка создалась
        status_after_block = await client.get(
            url_status,
            headers=auth_headers["user_a"]
        )
        print(f"After block: {status_after_block.json()['is_blocked']}")
        assert status_after_block.json()["is_blocked"] is True

        # Шаг 2: Разблокируем
        unblock_response = await client.delete(
            f"/v1/users/block/{user_id_a}",
            headers=auth_headers["user_b"]
        )
        print(f"Unblock response status: {unblock_response.status_code}")
        print(f"Unblock response body: {unblock_response.text}")

        assert unblock_response.status_code == 200
        msg = unblock_response.json().get("message", "")
        assert "User unblocked successfully" in msg

        # Шаг 3: Проверяем, что блокировки больше нет
        status_after_unblock = await client.get(
            url_status,
            headers=auth_headers["user_a"]
        )
        print(f"After unblock: {status_after_unblock.json()['is_blocked']}")
        assert status_after_unblock.status_code == 200
        assert status_after_unblock.json()["is_blocked"] is False

    @pytest.mark.asyncio
    async def test_get_blocked_users_list(
        self, client, test_users, auth_headers
    ):
        # Блокируем пользователя A
        block_data = {
            "blocked_id": test_users["user_a"].id,
            "block_profile": True,
            "block_wishlists": True
        }

        await client.post(
            f"/v1/users/block/{test_users['user_a'].id}",
            json=block_data,
            headers=auth_headers["user_b"]
        )

        # Получаем список заблокированных
        response = await client.get(
            "/v1/users/block/list",
            headers=auth_headers["user_b"]
        )

        assert response.status_code == 200
        assert "blocked_users" in response.json()

        # Проверяем, что пользователь A в списке

        blocked_ids = [u["blocked_user"]["id"] for u in response.json()["blocked_users"]] # noqa
        assert test_users["user_a"].id in blocked_ids

    @pytest.mark.asyncio
    async def test_update_block_settings(
        self, client, test_users, auth_headers
    ):
        # Сначала блокируем
        block_data = {
            "blocked_id": test_users["user_a"].id,
            "block_profile": True,
            "block_wishlists": True
        }

        await client.post(
            f"/v1/users/block/{test_users['user_a'].id}",
            json=block_data,
            headers=auth_headers["user_b"]
        )

        # Обновляем настройки (отключаем блокировку профиля)
        update_data = {
            "block_profile": False,
            "block_wishlists": True
        }

        response = await client.put(
            f"/v1/users/block/{test_users['user_a'].id}",
            json=update_data,
            headers=auth_headers["user_b"]
        )

        assert response.status_code == 200
        assert response.json()["block_profile"] is False
        assert response.json()["block_wishlists"] is True
