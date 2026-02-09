import aiohttp
import uuid
import io
from fastapi import UploadFile
from typing import Optional
from app.core.s3_client import S3Client


class PhotoUpdateService:
    def __init__(
        self,
        s3_client: S3Client
        ):
        self.s3_client = s3_client
    
    async def migrate_photo(
        self,
        tg_photo_url: str
    ) -> Optional[str]:

        if not tg_photo_url:
            return None
        
        if self.check_s3_storage(tg_photo_url):
            return tg_photo_url
        try:
            async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=30)) as session:
                async with session.get(tg_photo_url) as response:
                    if response.status != 200:
                        return None
                content = await response.read()
                if not content:
                    return None
                content_type = response.headers.get('Content-Type', 'image/jpeg')

                file_extension = self._get_extension_from_content_type(content_type)
                filename = f"{uuid.uuid4()}.{file_extension}"

                upload_file = UploadFile(
                    filename=filename,
                    file=io.BytesIO(content),
                    content_type=content_type,
                    size=len(content)
                )
                new_url = self.s3_client.upload_fastapi_file(upload_file)
                return new_url
        except aiohttp.ClientError as e:
            print(f"Error download file = {e}")
            return None
        except Exception as e:
            print(f"Error e = {e}")
            return None

    def check_s3_storage(
        self,
        url: str
    ) -> bool:
        domains = ["selstorage.ru"]
        return any(domain in url for domain in domains)
