import aiohttp
import uuid
import io
from fastapi import UploadFile
from typing import Optional
from app.core.s3_client import S3Client
import logging

logger = logging.getLogger(__name__)

class PhotoUpdateService:
    def __init__(
        self,
        s3_client: S3Client
        ):
        self.s3_client = s3_client
    
    # async def migrate_photo(
    #     self,
    #     tg_photo_url: str
    # ) -> Optional[str]:

    #     if not tg_photo_url:
    #         return None
        
    #     if self.check_s3_storage(tg_photo_url):
    #         return tg_photo_url
    #     try:
    #         async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=30)) as session:
    #             async with session.get(tg_photo_url) as response:
    #                 if response.status != 200:
    #                     return None
    #             content = await response.read()
    #             if not content:
    #                 return None
    #             content_type = response.headers.get('Content-Type', 'image/jpeg')

    #             file_extension = self._get_extension_from_content_type(content_type)
    #             filename = f"{uuid.uuid4()}.{file_extension}"

    #             upload_file = UploadFile(
    #                 filename=filename,
    #                 file=io.BytesIO(content),
    #                 content_type=content_type,
    #                 size=len(content)
    #             )
    #             new_url = self.s3_client.upload_fastapi_file(upload_file)
    #             return new_url
    #     except aiohttp.ClientError as e:
    #         print(f"Error download file = {e}")
    #         return None
    #     except Exception as e:
    #         print(f"Error e = {e}")
    #         return None



    # async def migrate_telegram_photo(
    #     self, 
    #     telegram_photo_url: str
    # ) -> Optional[str]:
    #     """
    #     Скачивает фото из Telegram и загружает в S3.
    #     Без сложных заголовков.
    #     """
    #     if not telegram_photo_url:
    #         return None
        
    #     # Проверяем, не в нашем ли хранилище уже фото
    #     if 'selstorage.ru' in telegram_photo_url:
    #         return telegram_photo_url
        
    #     try:
    #         logger.info(f"Начинаем миграцию фото: {telegram_photo_url}")
            
    #         # Простой запрос без заголовков
    #         async with aiohttp.ClientSession() as session:
    #             async with session.get(telegram_photo_url) as response:
    #                 if response.status != 200:
    #                     logger.warning(f"Статус ответа: {response.status}")
    #                     return None
                    
    #                 # Читаем содержимое
    #                 content = await response.read()
                    
    #                 if not content:
    #                     logger.warning("Пустой ответ")
    #                     return None
                    
    #                 # Определяем тип файла
    #                 content_type = response.headers.get('Content-Type', '')
                    
    #                 # Создаем имя файла

                    
    #                 # Определяем расширение
    #                 if 'svg' in content_type.lower() or telegram_photo_url.endswith('.svg'):
    #                     file_extension = 'svg'
    #                 elif 'png' in content_type.lower():
    #                     file_extension = 'png'
    #                 elif 'webp' in content_type.lower():
    #                     file_extension = 'webp'
    #                 elif 'jpeg' in content_type.lower() or 'jpg' in content_type.lower():
    #                     file_extension = 'jpg'
    #                 elif 'gif' in content_type.lower():
    #                     file_extension = 'gif'
    #                 else:
    #                     # Пытаемся определить по первым байтам
    #                     if content.startswith(b'<?xml') or b'<svg' in content[:100]:
    #                         file_extension = 'svg'
    #                     else:
    #                         file_extension = 'jpg'  # по умолчанию
                    
    #                 filename = f"{uuid.uuid4()}.{file_extension}"
                    
    #                 # Создаем UploadFile
    #                 upload_file = UploadFile(
    #                     filename=filename,
    #                     file=io.BytesIO(content),
    #                     # content_type=
    #                     # size=len(content)
    #                 )
    #                 upload_file.content_type = content_type or f'image/{file_extension}'
    #                 logger.info("Uploading to S3...")
    #                 # Загружаем в S3
    #                 new_url = await self.s3_client.upload_fastapi_file(upload_file)
                    
    #                 logger.info(f"Фото успешно загружено в S3: {new_url}")
    #                 return new_url
                    
    #     except aiohttp.ClientError as e:
    #         logger.error(f"Ошибка сети: {e}")
    #     except Exception as e:
    #         logger.error(f"Общая ошибка: {e}")
        
    #     return None

    async def migrate_telegram_photo(
        self, 
        telegram_photo_url: str
    ) -> Optional[str]:
        """
        Скачивает фото из Telegram и загружает в S3.
        Использует upload_from_memory чтобы обойти проблему с content_type.
        """
        if not telegram_photo_url:
            return None
        
        # Проверяем, не в нашем ли хранилище уже фото
        if 'selstorage.ru' in telegram_photo_url:
            return telegram_photo_url
        
        try:
            logger.info(f"Начинаем миграцию фото: {telegram_photo_url}")
            
            async with aiohttp.ClientSession() as session:
                async with session.get(telegram_photo_url) as response:
                    if response.status != 200:
                        logger.warning(f"Статус ответа: {response.status}")
                        return None
                    
                    # Читаем содержимое
                    content = await response.read()
                    
                    if not content:
                        logger.warning("Пустой ответ")
                        return None
                    
                    # Определяем тип файла
                    content_type = response.headers.get('Content-Type', '')
                    
                    # Определяем расширение и content_type
                    if telegram_photo_url.endswith('.svg') or 'svg' in content_type.lower():
                        file_extension = 'svg'
                        content_type = 'image/svg+xml'
                    elif 'png' in content_type.lower():
                        file_extension = 'png'
                        content_type = content_type or 'image/png'
                    elif 'webp' in content_type.lower():
                        file_extension = 'webp'
                        content_type = content_type or 'image/webp'
                    elif 'jpeg' in content_type.lower() or 'jpg' in content_type.lower():
                        file_extension = 'jpg'
                        content_type = content_type or 'image/jpeg'
                    elif 'gif' in content_type.lower():
                        file_extension = 'gif'
                        content_type = content_type or 'image/gif'
                    else:
                        # Пытаемся определить по первым байтам
                        if content.startswith(b'<?xml') or b'<svg' in content[:100]:
                            file_extension = 'svg'
                            content_type = 'image/svg+xml'
                        else:
                            file_extension = 'jpg'
                            content_type = 'image/jpeg'
                    
                    filename = f"{uuid.uuid4()}.{file_extension}"
                    
                    logger.info(f"Загружаем файл: {filename}, тип: {content_type}")
                    
                    # Используем upload_from_memory вместо upload_fastapi_file
                    new_url = await self.s3_client.upload_from_memory(
                        file_content=content,
                        object_name=filename,
                        content_type=content_type
                    )
                    
                    logger.info(f"Фото успешно загружено в S3: {new_url}")
                    return new_url
                    
        except aiohttp.ClientError as e:
            logger.error(f"Ошибка сети: {e}")
        except Exception as e:
            logger.error(f"Общая ошибка: {e}", exc_info=True)
        
        return None
        
    def check_s3_storage(
        self,
        url: str
    ) -> bool:
        domains = ["selstorage.ru"]
        return any(domain in url for domain in domains)
