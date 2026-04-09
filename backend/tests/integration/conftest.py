# tests/integration/conftest.py
import pytest
from typing import AsyncGenerator
from unittest.mock import patch
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
import os
import uuid
from app.api.main import app
from app.core.db import get_db
from app.core.security import create_jwt_token
from app.services.wishlist_service import WishlistService
from app.schemas.wishlist import WishlistCreate
from app.services.user_service import UserService
from app.schemas.user import UserCreate
from fastapi import HTTPException, UploadFile


TEST_DATABASE_URL = os.getenv(
    "TEST_DATABASE_URL",
    "postgresql+asyncpg://testuser:testpass@localhost:5433/testdb"
)


# ==================== База данных ====================

@pytest.fixture(scope="function")
async def engine():
    test_engine = create_async_engine(
        url=TEST_DATABASE_URL,
        echo=False,
        pool_size=1,
        max_overflow=0
    )

    async with test_engine.begin() as conn:
        from app.core.base import Base
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
        print('All tables created')

    yield test_engine

    async with test_engine.begin() as conn:
        from app.core.base import Base
        await conn.run_sync(Base.metadata.drop_all)

    await test_engine.dispose()


@pytest.fixture(scope="function")
async def db_session(engine) -> AsyncGenerator[AsyncSession, None]:
    """Сессия для тестовой БД"""
    async_session = sessionmaker(
        engine,
        class_=AsyncSession,
        expire_on_commit=False,
        autocommit=False,
        autoflush=False,
    )

    session = async_session()
    try:
        yield session
        await session.commit()
    except Exception:
        await session.rollback()
        raise
    finally:
        await session.close()


# ==================== Mock Telegram Bot ====================

class MockTelegramBot:
    def __init__(self):
        self.sent_messages = []

    async def send_message(self, chat_id: int, text: str, **kwargs):
        message = {"chat_id": chat_id, "text": text}
        self.sent_messages.append(message)
        return message

    def get_messages_for_user(self, chat_id: int) -> list:
        return [m for m in self.sent_messages if m["chat_id"] == chat_id]

    def clear(self):
        self.sent_messages.clear()


@pytest.fixture(scope="function")
def mock_telegram_bot():
    bot = MockTelegramBot()

    with patch("app.services.notification_service_bot.bot", bot):
        with patch("app.core.bot_setup.bot", bot):
            yield bot
    bot.clear()


# ==================== Mock S3 Client ====================

class MockS3Client:
    """Мок S3 клиента - хранит файлы в памяти"""
    
    def __init__(self):
        self.files = {}
        self.base_url = "https://mock-s3.example.com/"
    
    async def upload_fastapi_file(self, upload_file, object_name=None):
        """Загрузка файла"""
        content = await upload_file.read()
        filename = upload_file.filename
        ext = filename.split(".")[-1] if "." in filename else ""
        object_name = object_name or f"{uuid.uuid4()}.{ext}"
        self.files[object_name] = content
        return f"{self.base_url}{object_name}"
    
    async def update_file(self, old_url_file, new_file):
        """Обновление файла"""
        object_name = old_url_file.split("/")[-1]
        if object_name in self.files:
            del self.files[object_name]
        return await self.upload_fastapi_file(new_file, object_name)
    
    async def delete_file(self, object_name_url):
        """Удаление файла"""
        object_name = object_name_url.split("/")[-1]
        if object_name in self.files:
            del self.files[object_name]
            return True
        return False
    
    def clear(self):
        """Очистка всех файлов"""
        count = len(self.files)
        self.files.clear()
        return count


# ==================== Мок S3 клиент с monkeypatch (принудительная подмена) ====================

class MockS3Client:
    """Мок S3 клиента"""
    
    def __init__(self, *args, **kwargs):
        """Принимает любые аргументы (игнорирует их)"""
        self.files = {}
        self.base_url = "https://mock-s3.example.com/"
    
    async def upload_fastapi_file(self, upload_file, object_name=None):
        content = await upload_file.read()
        filename = upload_file.filename
        ext = filename.split(".")[-1] if "." in filename else ""
        object_name = object_name or f"{uuid.uuid4()}.{ext}"
        self.files[object_name] = content
        return f"{self.base_url}{object_name}"
    
    async def update_file(self, old_url_file, new_file):
        object_name = old_url_file.split("/")[-1]
        if object_name in self.files:
            del self.files[object_name]
        return await self.upload_fastapi_file(new_file, object_name)
    
    async def delete_file(self, object_name_url):
        object_name = object_name_url.split("/")[-1]
        if object_name in self.files:
            del self.files[object_name]
            return True
        return False
    
    def clear(self):
        count = len(self.files)
        self.files.clear()
        return count


# Удалите фикстуру mock_s3 с monkeypatch, оставьте только эту:

@pytest.fixture(scope="function")
def mock_s3_client():
    """Фикстура с моком S3Client"""
    mock_instance = MockS3Client()
    
    # Патчим функцию, которая создает S3 клиент
    with patch("app.core.s3_client.create_s3_client", return_value=mock_instance):
        with patch("app.core.dependencies.get_client_s3", return_value=mock_instance):
            with patch("app.api.routers.s3_client.get_client_s3", return_value=mock_instance):
                yield mock_instance
    
    mock_instance.clear()


# ==================== Переопределение зависимостей ====================

@pytest.fixture(scope="function")
async def override_dependencies(db_session):
    async def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db
    yield
    app.dependency_overrides.clear()


# ==================== Тестовые данные ====================

@pytest.fixture(scope="function")
async def test_users(db_session):
    user_service = UserService(db_session)

    user_a = await user_service.create_user(
        UserCreate(telegram_id=123456789, name="Анна")
    )
    user_b = await user_service.create_user(
        UserCreate(telegram_id=987654321, name="Борис")
    )
    user_c = await user_service.create_user(
        UserCreate(telegram_id=555555555, name="Виктор")
    )

    return {"user_a": user_a, "user_b": user_b, "user_c": user_c}


@pytest.fixture(scope="function")
def auth_headers(test_users):
    headers = {}
    for key, user in test_users.items():
        token = create_jwt_token({"sub": str(user.id)})
        headers[key] = {"Authorization": f"Bearer {token}"}
    return headers


@pytest.fixture(scope="function")
async def client(override_dependencies):
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        yield client


@pytest.fixture(scope="function")
async def test_wishlists(db_session, test_users):
    service = WishlistService(db_session)

    wishlist_a_public = await service.create_wishlist(
        test_users["user_a"].id,
        WishlistCreate(name="Мои желания", description="Публичный список", typeprivacy="public")
    )

    wishlist_a_private = await service.create_wishlist(
        test_users["user_a"].id,
        WishlistCreate(name="Секретные желания", description="Приватный список", typeprivacy="private")
    )

    wishlist_b = await service.create_wishlist(
        test_users["user_b"].id,
        WishlistCreate(name="Подарки для меня", description="Список желаний Бориса", typeprivacy="public")
    )

    return {
        "wishlist_a_public": wishlist_a_public,
        "wishlist_a_private": wishlist_a_private,
        "wishlist_b": wishlist_b
    }