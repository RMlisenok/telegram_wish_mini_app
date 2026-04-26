import pytest
from io import BytesIO
from PIL import Image
from app.api.main import app
from app.core.dependencies import get_client_s3


class TestScenario6UpdateProfile:

    @pytest.fixture
    def valid_test_image(self):
        """Создает валидное тестовое изображение"""
        img = Image.new('RGB', (200, 200), color=(73, 109, 137))
        img_byte_arr = BytesIO()
        img.save(img_byte_arr, format='JPEG')
        img_byte_arr.seek(0)
        return ("test_avatar.jpg", img_byte_arr, "image/jpeg")

    @pytest.fixture
    def valid_test_image_png(self):
        """PNG изображение для теста замены"""
        img = Image.new('RGB', (150, 150), color=(255, 0, 0))
        img_byte_arr = BytesIO()
        img.save(img_byte_arr, format='PNG')
        img_byte_arr.seek(0)
        return ("test_avatar.png", img_byte_arr, "image/png")

    @pytest.fixture(autouse=True)
    def setup_s3_mock(self, mock_s3_client):
        # Это критически важная строка для синхронизации мока и API
        app.dependency_overrides[get_client_s3] = lambda: mock_s3_client

        mock_s3_client.clear()
        yield
        mock_s3_client.clear()

        # Убираем подмену после теста
        app.dependency_overrides.pop(get_client_s3, None)

    @pytest.mark.asyncio
    async def test_upload_avatar_to_s3(
        self, client, auth_headers, valid_test_image, mock_s3_client
    ):
        """Загрузка аватара в S3"""
        filename, file_content, content_type = valid_test_image
        files = {"file": (filename, file_content, content_type)}

        response = await client.post(
            "/v1/s3/file/",
            files=files,
            headers=auth_headers["user_a"]
        )

        assert response.status_code == 200
        data = response.json()
        assert "file_url" in data

        assert len(mock_s3_client.files) >= 1
        print(f"File uploaded to mock storage: {data['file_url']}")

    @pytest.mark.asyncio
    async def test_update_profile_with_avatar(
        self, client, auth_headers, valid_test_image, mock_s3_client
    ):
        """Обновление профиля с аватаркой"""
        filename, file_content, content_type = valid_test_image

        # Загружаем
        upload_res = await client.post(
            "/v1/s3/file/",
            files={"file": (filename, file_content, content_type)},
            headers=auth_headers["user_a"]
        )
        file_url = upload_res.json()["file_url"]

        # Обновляем профиль
        update_data = {"name": "Анна С Аватаром", "photo": file_url}
        update_response = await client.put(
            "/v1/users/me",
            json=update_data,
            headers=auth_headers["user_a"]
        )

        assert update_response.status_code == 200
        assert update_response.json()["photo"] == file_url
        print("Profile updated with mock URL")

    @pytest.mark.asyncio
    async def test_replace_avatar(
        self,
        client,
        auth_headers,
        valid_test_image,
        valid_test_image_png,
        mock_s3_client
    ):
        # 1. Грузим первый
        fn1, ct1, typ1 = valid_test_image
        res1 = await client.post(
            "/v1/s3/file/",
            files={"file": (fn1, ct1, typ1)},
            headers=auth_headers["user_a"]
        )
        old_url = res1.json()["file_url"]

        # 2. Меняем на второй
        fn2, ct2, typ2 = valid_test_image_png
        replace_response = await client.put(
            f"/v1/s3/file/replace?file_url={old_url}",
            files={"file": (fn2, ct2, typ2)},
            headers=auth_headers["user_a"]
        )

        assert replace_response.status_code == 200
        # В моке должен остаться 1 файл (старый заменен новым)
        assert len(mock_s3_client.files) == 1
        print("Avatar replaced in mock storage")

    @pytest.mark.asyncio
    async def test_update_profile_without_avatar(self, client, auth_headers):
        update_data = {"name": "Анна Без Аватара"}
        response = await client.put(
            "/v1/users/me",
            json=update_data,
            headers=auth_headers["user_a"]
        )
        assert response.status_code == 200
        assert response.json()["name"] == "Анна Без Аватара"

    @pytest.mark.asyncio
    async def test_get_current_user(self, client, auth_headers):
        response = await client.get(
            "/v1/users/me",
            headers=auth_headers["user_a"]
        )
        assert response.status_code == 200
        assert "name" in response.json()

    @pytest.mark.asyncio
    async def test_update_birth_date(self, client, auth_headers):
        update_data = {"birth_date": "1990-05-15"}
        response = await client.put(
            "/v1/users/me",
            json=update_data,
            headers=auth_headers["user_a"]
        )
        assert response.status_code == 200
        assert response.json()["birth_date"] == "1990-05-15"

    @pytest.mark.asyncio
    async def test_update_theme(self, client, auth_headers):
        update_data = {"theme": "dark"}
        response = await client.put(
            "/v1/users/me",
            json=update_data,
            headers=auth_headers["user_a"]
        )
        assert response.status_code == 200
        assert response.json()["theme"] == "dark"
