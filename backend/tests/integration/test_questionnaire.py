import pytest


class TestScenario13Questionnaire:

    @pytest.mark.asyncio
    async def test_positive_create_questionnaire(
        self, client, auth_headers
    ):

        questionnaire_data = {
            "interests": [
                {"tag": "книги", "details": "Люблю читать фантастику"},
                {"tag": "кино", "details": "Обожаю научную фантастику"},
                {"tag": "музыка", "details": "Рок и классика"}
            ],
            "avoid_gifts": [
                {"tag": "сладости", "details": "Аллергия на шоколад"},
                {"tag": "цветы", "details": "Не люблю срезанные цветы"}
            ]
        }

        response = await client.post(
            "/v1/questionnaire/",
            json=questionnaire_data,
            headers=auth_headers["user_a"]
        )

        assert response.status_code == 200
        assert response.json()["success"] is True
        assert "items_count" in response.json()

    @pytest.mark.asyncio
    async def test_positive_get_my_questionnaire(
        self, client, auth_headers
    ):
        # Сначала создаем анкету
        questionnaire_data = {
            "interests": [
                {"tag": "спорт", "details": "Футбол"},
                {"tag": "путешествия", "details": "Горы"},
                {"tag": "фотография", "details": "Пейзажи"}
            ],
            "avoid_gifts": [
                {"tag": "сувениры", "details": "Некуда складывать"}
            ]
        }

        await client.post(
            "/v1/questionnaire/",
            json=questionnaire_data,
            headers=auth_headers["user_a"]
        )

        # Получаем анкету
        response = await client.get(
            "/v1/questionnaire/",
            headers=auth_headers["user_a"]
        )
        print(response.status_code)

        assert response.status_code == 200
        assert "interests" in response.json()
        print(response.json()["interests"])
        assert "avoid_gifts" in response.json()
        assert len(response.json()["interests"]) >= 3
        assert len(response.json()["avoid_gifts"]) >= 1

    @pytest.mark.asyncio
    async def test_positive_get_user_questionnaire(
        self, client, test_users, auth_headers
    ):
        # Пользователь A создает анкету
        questionnaire_data = {
            "interests": [
                {"tag": "книги", "details": "Фантастика"},
                {"tag": "кино", "details": "Комедии"},
                {"tag": "музыка", "details": "Джаз"}
            ],
            "avoid_gifts": [
                {"tag": "алкоголь", "details": "Не пью"}
            ]
        }

        await client.post(
            "/v1/questionnaire/",
            json=questionnaire_data,
            headers=auth_headers["user_a"]
        )

        # Пользователь B получает анкету A
        response = await client.get(
            f"/v1/questionnaire/{test_users['user_a'].id}",
            headers=auth_headers["user_b"]
        )

        assert response.status_code == 200
        assert "interests" in response.json()
        assert "avoid_gifts" in response.json()

    @pytest.mark.asyncio
    async def test_positive_update_questionnaire(
        self, client, auth_headers
    ):
        # Создаем первую анкету
        first_data = {
            "interests": [
                {"tag": "книги", "details": "Детективы"},
                {"tag": "кино", "details": "Комедии"},
                {"tag": "музыка", "details": "Джаз"}
            ],
            "avoid_gifts": [
                {"tag": "алкоголь", "details": "Не пью"}
            ]
        }

        await client.post(
            "/v1/questionnaire/",
            json=first_data,
            headers=auth_headers["user_a"]
        )

        # Обновляем анкету
        second_data = {
            "interests": [
                {"tag": "спорт", "details": "Бег"},
                {"tag": "йога", "details": "Медитация"},
                {"tag": "путешествия", "details": "Азия"}
            ],
            "avoid_gifts": [
                {"tag": "сладости", "details": "Диета"},
                {"tag": "цветы", "details": "Аллергия"}
            ]
        }

        response = await client.post(
            "/v1/questionnaire/",
            json=second_data,
            headers=auth_headers["user_a"]
        )

        assert response.status_code == 200
        assert response.json()["success"] is True

        # Проверяем, что анкета обновилась
        get_response = await client.get(
            "/v1/questionnaire/",
            headers=auth_headers["user_a"]
        )

        interests_tags = [i["tag"] for i in get_response.json()["interests"]]
        assert "спорт" in interests_tags
        assert "йога" in interests_tags
        assert "книги" not in interests_tags

    @pytest.mark.asyncio
    async def test_positive_get_available_tags(
        self, client, auth_headers
    ):
        response = await client.get(
            "/v1/questionnaire/tags/available?is_interest=true",
            headers=auth_headers["user_a"]
        )

        assert response.status_code == 200
        assert "tags" in response.json()
        assert isinstance(response.json()["tags"], list)

    @pytest.mark.asyncio
    async def test_positive_create_custom_tag(
        self, client, auth_headers
    ):
        tag_data = {
            "tag_value": "айкидо",
            "type_tag": True,
            "detail": "Люблю восточные единоборства"
        }

        response = await client.post(
            "/v1/questionnaire/answer",
            json=tag_data,
            headers=auth_headers["user_a"]
        )

        assert response.status_code == 200
        assert response.json()["status"] == "success"
        assert "tag" in response.json()

    @pytest.mark.asyncio
    async def test_negative_get_questionnaire_without_auth(
        self, client
    ):
        """
        Негативный сценарий: Получение анкеты без авторизации
        Ожидаемый результат: 401
        """
        response = await client.get("/v1/questionnaire/")
        assert response.status_code == 401

    @pytest.mark.asyncio
    async def test_negative_get_user_questionnaire_nonexistent(
        self, client, auth_headers
    ):
        """
        Негативный сценарий: Получение анкеты несуществующего пользователя
        GET /v1/questionnaire/99999
        Ожидаемый результат: 404
        """
        response = await client.get(
            "/v1/questionnaire/99999",
            headers=auth_headers["user_a"]
        )

        assert response.status_code == 404

    @pytest.mark.asyncio
    async def test_negative_create_custom_tag_duplicate(
        self, client, auth_headers
    ):
        tag_data = {
            "tag_value": "уникальный_тег_123",
            "type_tag": True,
            "detail": "Описание"
        }

        # Создаем первый раз
        response1 = await client.post(
            "/v1/questionnaire/answer",
            json=tag_data,
            headers=auth_headers["user_a"]
        )
        assert response1.status_code == 200

        # Создаем второй раз
        response2 = await client.post(
            "/v1/questionnaire/answer",
            json=tag_data,
            headers=auth_headers["user_a"]
        )

        assert response2.status_code == 400
