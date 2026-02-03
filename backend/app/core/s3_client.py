from aiobotocore.session import get_session
from contextlib import asynccontextmanager
from aiobotocore.session import get_session
from contextlib import asynccontextmanager
import aiofiles
from botocore.config import Config
from fastapi import UploadFile
from typing import Optional, BinaryIO
import os
import uuid
from .config import settings

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
        if not object_name:
            ext = upload_file.filename.split(".")[-1] if "." in upload_file.filename else ""

            object_name = f"{uuid.uuid4()}.{ext}" if ext else str(uuid.uuid4())

        content = await upload_file.read()
        return await self.upload_from_memory(
            content,
            object_name,
            upload_file.content_type
        )

    async def delete_file(self, object_name: str) -> bool:
        async with self.get_client() as client:
            await client.delete_object(
                Bucket=self.bucket_name,
                Key=object_name
            )
            return True


def create_s3_client() -> S3Client:
    return S3Client(
        access_key=settings.ACCESS_KEY,
        secret_key=settings.SECRET_KEY,
        endpoint_url=settings.ENDPOINT_URL,
        bucket_name=settings.BUCKET_NAME,
        data_save_url=settings.URL_DATA_SAVE
    )
