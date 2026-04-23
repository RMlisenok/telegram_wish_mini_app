# tests/integration/test_block_user.py
import pytest


class TestScenario7BlockUser:
    """Сценарий 7: Блокировка пользователя и проверка доступа"""
    
    @pytest.mark.asyncio
    async def test_positive_block_user(
        self, client, test_users, auth_headers
    ):
        """
        Позитивный сценарий: Пользователь B блокирует пользователя A
        POST /v1/users/block/{blocked_id}
        """
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
        """
        Позитивный сценарий: Проверка статуса блокировки
        GET /v1/users/block/status/{user_id}?blocker_id={blocker_id}
        """
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
        response = await client.get(
            f"/v1/users/block/status/{test_users['user_a'].id}?blocker_id={test_users['user_b'].id}",
            headers=auth_headers["user_a"]
        )
        
        assert response.status_code == 200
        assert response.json()["is_blocked"] is True
    
    @pytest.mark.asyncio
    async def test_negative_block_self(
        self, client, test_users, auth_headers
    ):
        """
        Негативный сценарий: Попытка заблокировать самого себя
        """
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
        # Сначала блокируем
        block_data = {
            "blocked_id": test_users["user_a"].id,
            "block_profile": True,
            "block_wishlists": True
        }

        status_response_first = await client.get(
            f"/v1/users/block/status/{test_users['user_a'].id}?blocker_id={test_users['user_b'].id}",
            headers=auth_headers["user_a"]
        )

        print(status_response_first.json()["is_blocked"])


        response_block = await client.post(
            f"/v1/users/block/{test_users['user_a'].id}",
            json=block_data,
            headers=auth_headers["user_b"]
        )
        
        status_response_second = await client.get(
            f"/v1/users/block/status/{test_users['user_a'].id}?blocker_id={test_users['user_b'].id}",
            headers=auth_headers["user_a"]
        )

        print(status_response_second.json()["is_blocked"])

        
        # print(response_block.status_code)
        
        
        # Разблокируем
        response = await client.delete(
            f"/v1/users/block/{test_users['user_a'].id}",
            headers=auth_headers["user_b"]
        )
        # print(response.status_code)
        # print(response.json()["message"])
        assert response.status_code == 200
        assert "User unblocked successfully" in response.json()["message"]
        
        # Проверяем, что блокировки больше нет
        status_response = await client.get(
            f"/v1/users/block/status/{test_users['user_a'].id}?blocker_id={test_users['user_b'].id}",
            headers=auth_headers["user_a"]
        )

        print(status_response.status_code)
        print(status_response.json()["is_blocked"])
        assert status_response.status_code == 200
        assert status_response.json()["is_blocked"] is False
    
    @pytest.mark.asyncio
    async def test_get_blocked_users_list(
        self, client, test_users, auth_headers
    ):
        """
        Позитивный сценарий: Получение списка заблокированных пользователей
        GET /v1/users/block/list
        """
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
        blocked_ids = [u["blocked_user"]["id"] for u in response.json()["blocked_users"]]
        assert test_users["user_a"].id in blocked_ids
    
    @pytest.mark.asyncio
    async def test_update_block_settings(
        self, client, test_users, auth_headers
    ):
        """
        Позитивный сценарий: Обновление настроек блокировки
        PUT /v1/users/block/{blocked_id}
        """
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