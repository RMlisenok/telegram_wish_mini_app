# tests/unit/test_core/test_s3_client.py
import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from fastapi import HTTPException, UploadFile
from io import BytesIO
from app.core.s3_client import S3Client, create_s3_client
from app.core.config import settings


class TestS3Client:
    """Test suite for S3Client."""

    @pytest.fixture
    def s3_client(self):
        return S3Client(
            access_key="test_key",
            secret_key="test_secret",
            endpoint_url="http://localhost:9000",
            bucket_name="test-bucket",
            data_save_url="http://localhost:9000/test-bucket/"
        )

    @pytest.mark.asyncio
    async def test_get_client(self, s3_client):
        """Test getting S3 client context manager."""
        async with s3_client.get_client() as client:
            assert client is not None

    @pytest.mark.asyncio
    async def test_upload_from_memory_success(self, s3_client):
        """Test uploading from memory."""
        with patch.object(s3_client, 'get_client') as mock_get_client:
            mock_client = AsyncMock()
            mock_get_client.return_value.__aenter__.return_value = mock_client

            result = await s3_client.upload_from_memory(b"test content", "test.jpg", "image/jpeg")

            assert result == s3_client.data_save_url + "test.jpg"
            mock_client.put_object.assert_called_once()

    @pytest.mark.asyncio
    async def test_upload_fastapi_file_success(self, s3_client):
        """Test uploading FastAPI file."""
        # Создаем правильный мок UploadFile
        mock_file = MagicMock(spec=UploadFile)
        mock_file.filename = "test.jpg"
        mock_file.content_type = "image/jpeg"
        mock_file.read = AsyncMock(return_value=b"image content")

        # Создаем мок для file атрибута
        mock_file_object = MagicMock()
        mock_file_object.seek = MagicMock()
        mock_file.file = mock_file_object

        with patch.object(s3_client, 'upload_from_memory', AsyncMock(return_value="http://localhost/test.jpg")):
            with patch.object(s3_client, 'check_image_resolution', AsyncMock(return_value=(100, 100))):
                result = await s3_client.upload_fastapi_file(mock_file)

                assert result == "http://localhost/test.jpg"

    @pytest.mark.asyncio
    async def test_upload_fastapi_file_invalid_content_type(self, s3_client):
        """Test uploading file with invalid content type."""
        mock_file = MagicMock(spec=UploadFile)
        mock_file.content_type = "application/pdf"
        mock_file.read = AsyncMock(return_value=b"content")
        mock_file.file = MagicMock()

        with pytest.raises(HTTPException) as exc_info:
            await s3_client.upload_fastapi_file(mock_file)

        assert exc_info.value.status_code == 400
        assert "Uncorrect format" in str(exc_info.value.detail)

    @pytest.mark.asyncio
    async def test_upload_fastapi_file_too_large(self, s3_client):
        """Test uploading file that is too large."""
        mock_file = MagicMock(spec=UploadFile)
        mock_file.content_type = "image/jpeg"
        mock_file.filename = "test.jpg"
        mock_file.read = AsyncMock(return_value=b"x" * (11 * 1024 * 1024))  # 11 MB
        mock_file.file = MagicMock()

        with pytest.raises(HTTPException) as exc_info:
            await s3_client.upload_fastapi_file(mock_file)

        assert exc_info.value.status_code == 400
        assert "File size more allowed size" in str(exc_info.value.detail)

    @pytest.mark.asyncio
    async def test_upload_fastapi_file_invalid_extension(self, s3_client):
        """Test uploading file with invalid extension."""
        mock_file = MagicMock(spec=UploadFile)
        mock_file.content_type = "image/jpeg"
        mock_file.filename = "test.exe"
        mock_file.read = AsyncMock(return_value=b"content")
        mock_file.file = MagicMock()

        with pytest.raises(HTTPException) as exc_info:
            await s3_client.upload_fastapi_file(mock_file)

        assert exc_info.value.status_code == 400
        assert "Uncorrect file extension" in str(exc_info.value.detail)

    @pytest.mark.asyncio
    async def test_update_file_success(self, s3_client):
        """Test updating file."""
        old_url = s3_client.data_save_url + "old.jpg"
        mock_file = MagicMock(spec=UploadFile)
        mock_file.file = MagicMock()

        with patch.object(s3_client, 'get_object_name', return_value="old.jpg"):
            with patch.object(s3_client, 'upload_fastapi_file', AsyncMock(return_value="http://localhost/new.jpg")):
                result = await s3_client.update_file(old_url, mock_file)

                assert result == "http://localhost/new.jpg"

    @pytest.mark.asyncio
    async def test_update_file_invalid_url(self, s3_client):
        """Test updating file with invalid URL."""
        with patch.object(s3_client, 'get_object_name', return_value=None):
            with pytest.raises(HTTPException) as exc_info:
                await s3_client.update_file("invalid_url", MagicMock())

            assert exc_info.value.status_code == 400

    def test_get_object_name_valid(self, s3_client):
        """Test getting object name from valid URL."""
        url = s3_client.data_save_url + "image.jpg"
        result = s3_client.get_object_name(url)

        assert result == "image.jpg"

    def test_get_object_name_invalid(self, s3_client):
        """Test getting object name from invalid URL."""
        result = s3_client.get_object_name("http://other.com/image.jpg")

        assert result is None

    @pytest.mark.asyncio
    async def test_check_image_resolution_valid(self, s3_client):
        """Test checking valid image resolution."""
        # Создаем реальное изображение для теста
        from PIL import Image
        import io

        # Создаем простое изображение
        img = Image.new('RGB', (800, 600), color='red')
        img_bytes = io.BytesIO()
        img.save(img_bytes, format='JPEG')
        img_content = img_bytes.getvalue()

        width, height = await s3_client.check_image_resolution(img_content, "image/jpeg")

        assert width == 800
        assert height == 600

    @pytest.mark.asyncio
    async def test_check_image_resolution_too_large(self, s3_client):
        """Test checking image resolution too large."""
        from PIL import Image
        import io

        # Создаем слишком большое изображение
        img = Image.new('RGB', (5000, 4000), color='red')
        img_bytes = io.BytesIO()
        img.save(img_bytes, format='JPEG')
        img_content = img_bytes.getvalue()

        with pytest.raises(HTTPException) as exc_info:
            await s3_client.check_image_resolution(img_content, "image/jpeg")

        assert exc_info.value.status_code == 400

    @pytest.mark.asyncio
    async def test_check_image_resolution_too_small(self, s3_client):
        """Test checking image resolution too small."""
        from PIL import Image
        import io

        # Создаем слишком маленькое изображение
        img = Image.new('RGB', (30, 30), color='red')
        img_bytes = io.BytesIO()
        img.save(img_bytes, format='JPEG')
        img_content = img_bytes.getvalue()

        with pytest.raises(HTTPException) as exc_info:
            await s3_client.check_image_resolution(img_content, "image/jpeg")

        assert exc_info.value.status_code == 400

    @pytest.mark.asyncio
    async def test_check_image_resolution_svg(self, s3_client):
        """Test checking SVG image resolution."""
        width, height = await s3_client.check_image_resolution(b"<svg></svg>", "image/svg+xml")

        assert width == 0
        assert height == 0

    @pytest.mark.asyncio
    async def test_delete_file_success(self, s3_client):
        """Test deleting file successfully."""
        url = s3_client.data_save_url + "image.jpg"

        with patch.object(s3_client, 'get_client') as mock_get_client:
            mock_client = AsyncMock()
            mock_get_client.return_value.__aenter__.return_value = mock_client

            result = await s3_client.delete_file(url)

            assert result is True
            mock_client.delete_object.assert_called_once()

    @pytest.mark.asyncio
    async def test_delete_file_invalid_url(self, s3_client):
        """Test deleting file with invalid URL."""
        result = await s3_client.delete_file("invalid_url")

        assert result is False

    @pytest.mark.asyncio
    async def test_delete_file_exception(self, s3_client):
        """Test deleting file with exception."""
        url = s3_client.data_save_url + "image.jpg"

        with patch.object(s3_client, 'get_client') as mock_get_client:
            mock_client = AsyncMock()
            mock_client.delete_object = AsyncMock(side_effect=Exception("S3 error"))
            mock_get_client.return_value.__aenter__.return_value = mock_client

            result = await s3_client.delete_file(url)

            assert result is False

    def test_create_s3_client(self):
        """Test creating S3 client instance."""
        client = create_s3_client()

        assert client is not None
        assert client.bucket_name == settings.BUCKET_NAME