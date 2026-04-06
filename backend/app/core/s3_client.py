from aiobotocore.session import get_session
from contextlib import asynccontextmanager
from aiobotocore.session import get_session
from contextlib import asynccontextmanager
import aiofiles
from botocore.config import Config
from fastapi import UploadFile, HTTPException, status
from typing import Optional, BinaryIO, Tuple
import uuid
import io
from .config import settings
from PIL import Image


class S3Client:

    def __init__(
        self,
        access_key: str,
        secret_key: str,
        endpoint_url: str,
        bucket_name: str,
        data_save_url: str
    ):
        self.config = {
            "aws_access_key_id": access_key,
            "aws_secret_access_key": secret_key,
            "endpoint_url": endpoint_url,
            "verify": False
        }
        self.bucket_name = bucket_name
        self.data_save_url = data_save_url
        self.session = get_session()

        self.allowed_content_types = {
            'image/jpeg', 'image/png', 'image/gif',
            'image/webp', 'image/svg+xml'
        }
        self.allowed_extensions = {
            'jpg', 'jpeg', 'png',
            'gif', 'webp', 'svg'
        }
        self.max_size_file = 10 * 1024 * 1024  # 10 MB
        self.max_image_resolution = (4096, 4096)
        self.min_image_resolution = (50, 50)
        self.resolution_check_types = {
            'image/jpeg', 'image/png', 'image/gif', 'image/webp'
        }

    @asynccontextmanager
    async def get_client(self):
        async with self.session.create_client("s3", **self.config) as client:
            yield client

    async def upload_file(self, file_path: str):
        object_name = file_path.split("/")[-1]
        async with self.get_client() as client:
            async with aiofiles.open(file_path, "rb") as file:
                await client.put_object(
                    Bucket=self.bucket_name,
                    Key=object_name,
                    Body=file,
                )

    async def upload_from_memory(
        self,
        file_content: bytes,
        object_name: str,
        content_type: Optional[str] = None
    ) -> str:
        async with self.get_client() as client:
            put_kwargs = {
                "Bucket": self.bucket_name,
                "Key": object_name,
                "Body": file_content,
            }
            if content_type:
                put_kwargs["ContentType"] = content_type
            await client.put_object(**put_kwargs)
        return self.data_save_url + object_name

    async def upload_fastapi_file(
        self,
        upload_file: UploadFile,
        object_name: Optional[str] = None
    ) -> str:
        if upload_file.content_type not in self.allowed_content_types:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Uncorrect format: {upload_file.content_type}"
            )
        content = await upload_file.read()
        upload_file.file.seek(0)
        if len(content) > self.max_size_file:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"File size more allowed size: {
                    round(self.max_size_file / (1024 * 1024), 1)
                }"
            )

        ext = (
            upload_file.filename.split(".")[-1].lower()
            if "." in upload_file.filename else ""
        )
        if ext not in self.allowed_extensions:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Uncorrect file extension: {ext}"
            )
        if not object_name:
            object_name = f"{uuid.uuid4()}.{ext}" if ext else str(uuid.uuid4())

        width, height = await self.check_image_resolution(
            content,
            upload_file.content_type
        )
        return await self.upload_from_memory(
            content,
            object_name,
            upload_file.content_type
        )

    async def update_file(
        self,
        old_url_file: str,
        new_file: UploadFile
    ) -> str:
        object_name = self.get_object_name(old_url_file)
        if not object_name:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Uncorrect old URL"
            )
        return await self.upload_fastapi_file(new_file, object_name)

    def get_object_name(self, url_file: str) -> Optional[str]:
        try:
            if url_file.startswith(self.data_save_url):
                return url_file.split("/")[-1]
            return None
        except Exception:
            return None

    async def check_image_resolution(
        self,
        file_content: bytes,
        content_type: str
    ) -> Tuple[int, int]:

        if content_type == "image/svg+xml":
            return (0, 0)
        if content_type not in self.resolution_check_types:
            return (0, 0)
        try:
            image = Image.open(io.BytesIO(file_content))
            width, height = image.size
            if width > self.max_image_resolution[0] or height > self.max_image_resolution[1]:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=(
                        f"File uncorrect image ({width}x{height}) "
                        f"Max allowed ({self.max_image_resolution[0]}x{self.max_image_resolution[1]})"
                        )
                )
            if width < self.min_image_resolution[0] or height < self.min_image_resolution[1]:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=(
                        f"File uncorrect image ({width}x{height}) "
                        f"Min allowed ({self.min_image_resolution[0]}x{self.min_image_resolution[1]})"
                        )
                )
            image.close()
            return width, height
        except HTTPException:
            raise
        except Exception as e:
            print(f"Dont check image resolution: {e}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Dont check image resolution, please check valid file"
            )

    async def delete_file(self, object_name_url: str) -> bool:
        object_name = self.get_object_name(object_name_url)
        if not object_name:
            return False
        async with self.get_client() as client:
            try:
                await client.delete_object(
                    Bucket=self.bucket_name,
                    Key=object_name
                )
                return True
            except Exception as e:
                print(f"Error when delete file: {e}")
                return False


def create_s3_client() -> S3Client:
    return S3Client(
        access_key=settings.S3_ACCESS_KEY,
        secret_key=settings.S3_SECRET_KEY,
        endpoint_url=settings.ENDPOINT_URL,
        bucket_name=settings.BUCKET_NAME,
        data_save_url=settings.URL_DATA_SAVE
    )
