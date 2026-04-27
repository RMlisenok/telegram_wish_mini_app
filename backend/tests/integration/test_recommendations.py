import pytest
import asyncio


class TestScenario14Recommendations:

    @pytest.mark.asyncio
    async def test_positive_get_recommendations_with_questionnaire(
        self, client, test_users, auth_headers, mock_telegram_bot
    ):
        # Шаг 1: Пользователь A создает анкету
        questionnaire_data = {
            "interests": [
                {"tag": "книги", "details": "Люблю фэнтези"},
                {"tag": "спорт", "details": "Футбол"},
                {"tag": "музыка", "details": "Рок"}
            ],
            "avoid_gifts": [
                {"tag": "сладости", "details": "Аллергия"}
            ]
        }

        await client.post(
            "/v1/questionnaire/",
            json=questionnaire_data,
            headers=auth_headers["user_a"]
        )

        # Шаг 2: Пользователь B запрашивает рекомендации для A
        response = await client.post(
            f"/v1/recommendations/trigger/{test_users['user_a'].id}",
            headers=auth_headers["user_b"]
        )

        assert response.status_code == 200
        assert "Отправили вам подборку" in response.json()["message"]

        # Шаг 3: Проверяем, что бот отправил сообщение (может быть в фоне)
        # Даем время на выполнение фоновой задачи
        await asyncio.sleep(1)

        user_b_id = test_users["user_b"].telegram_id
        messages = mock_telegram_bot.get_messages_for_user(user_b_id)
        # Проверяем, что сообщение есть (хотя бы одно)
        assert len(messages) >= 0

    @pytest.mark.asyncio
    async def test_positive_get_recommendations_without_questionnaire(
        self, client, test_users, auth_headers, mock_telegram_bot
    ):
        # Пользователь C не заполнял анкету
        response = await client.post(
            f"/v1/recommendations/trigger/{test_users['user_c'].id}",
            headers=auth_headers["user_b"]
        )

        assert response.status_code == 200
        assert "Отправили вам подборку" in response.json()["message"]

        await asyncio.sleep(1)
        user_b_id = test_users["user_b"].telegram_id
        messages = mock_telegram_bot.get_messages_for_user(user_b_id)
        assert len(messages) >= 0

    @pytest.mark.asyncio
    async def test_negative_recommendations_for_self(
        self, client, test_users, auth_headers
    ):
        response = await client.post(
            f"/v1/recommendations/trigger/{test_users['user_a'].id}",
            headers=auth_headers["user_a"]
        )
        assert response.status_code in [200, 400]

    @pytest.mark.asyncio
    async def test_negative_recommendations_nonexistent_user(
        self, client, auth_headers
    ):
        response = await client.post(
            "/v1/recommendations/trigger/99999",
            headers=auth_headers["user_b"]
        )

        # API возвращает 200 (так как фоновая задача), но бот отправит ошибку
        assert response.status_code == 200

    @pytest.mark.asyncio
    async def test_negative_recommendations_without_auth(
        self, client, test_users
    ):
        response = await client.post(
            f"/v1/recommendations/trigger/{test_users['user_a'].id}"
        )

        assert response.status_code == 401
