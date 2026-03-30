# # tests/test_user_service.py
# import pytest
# from unittest.mock import AsyncMock, MagicMock, patch
# from datetime import date, datetime
# import sys
# from pathlib import Path

# # Добавляем путь к проекту для корректных импортов
# sys.path.insert(0, str(Path(__file__).parent.parent))

# from app.services.user_service import UserService
# from app.models.user import User
# from app.schemas.user import UserCreate, UserUpdate, ThemeEnum, TextSizeEnum, UserResponesForMainScreen
# from app.schemas.block import BlockCreate
# from app.schemas.subscription import SubscribersResponse


# class TestUserService:
#     @pytest.fixture
#     def mock_session(self):
#         """Фикстура для мок-сессии"""
#         session = AsyncMock()
#         return session

#     @pytest.fixture
#     def user_service(self, mock_session):
#         """Фикстура для сервиса с моками"""
#         service = UserService(mock_session)
        
#         # Создаем моки для репозиториев
#         service.rep_user = AsyncMock()
#         service.rep_block = AsyncMock()
#         service.rep_wishlist = AsyncMock()
#         service.rep_wish = AsyncMock()
#         service.rep_subs = AsyncMock()
#         service.rep_wish_wishlist = AsyncMock()
#         service.serv_subs = AsyncMock()
#         service.serv_wishlist = AsyncMock()
        
#         return service

#     def create_test_user(self, id=1, telegram_id=123456, name="Test User"):
#         """Вспомогательный метод для создания тестового пользователя со всеми полями"""
#         return User(
#             id=id,
#             telegram_id=telegram_id,
#             name=name,
#             birth_date=date(1990, 1, 1),
#             photo="https://example.com/photo.jpg",
#             theme=ThemeEnum.light,
#             text_size=TextSizeEnum.medium,
#             show_sub=True,
#             created_at=datetime.now(),
#             updated_at=datetime.now()
#         )

#     @pytest.mark.asyncio
#     async def test_get_user_success(self, user_service):
#         """Тест успешного получения пользователя"""
#         # Подготовка
#         user = self.create_test_user()
#         user_service.rep_user.get_user_by_id = AsyncMock(return_value=user)

#         # Выполнение
#         result = await user_service.get_user(1)

#         # Проверка
#         assert result is not None
#         assert result.id == 1
#         assert result.name == "Test User"
#         assert result.theme == ThemeEnum.light
#         assert result.text_size == TextSizeEnum.medium
#         user_service.rep_user.get_user_by_id.assert_called_once_with(1)

#     @pytest.mark.asyncio
#     async def test_get_user_not_found(self, user_service):
#         """Тест когда пользователь не найден"""
#         # Подготовка
#         user_service.rep_user.get_user_by_id = AsyncMock(return_value=None)

#         # Выполнение
#         result = await user_service.get_user(999)

#         # Проверка
#         assert result is None
#         user_service.rep_user.get_user_by_id.assert_called_once_with(999)

#     @pytest.mark.asyncio
#     async def test_get_user_by_telegram_id_success(self, user_service):
#         """Тест получения пользователя по telegram_id"""
#         # Подготовка
#         user = self.create_test_user(telegram_id=123456)
#         user_service.rep_user.get_user_by_tg_id = AsyncMock(return_value=user)

#         # Выполнение
#         result = await user_service.get_user_by_telegram_id(123456)

#         # Проверка
#         assert result is not None
#         assert result.telegram_id == 123456
#         user_service.rep_user.get_user_by_tg_id.assert_called_once_with(123456)

#     @pytest.mark.asyncio
#     async def test_get_all_users(self, user_service):
#         """Тест получения всех пользователей"""
#         # Подготовка
#         users = [
#             self.create_test_user(id=1, name="User 1"),
#             self.create_test_user(id=2, name="User 2"),
#         ]
#         user_service.rep_user.get_all_users = AsyncMock(return_value=users)

#         # Выполнение
#         result = await user_service.get_all_users(limit=10)

#         # Проверка
#         assert len(result) == 2
#         assert result[0].name == "User 1"
#         user_service.rep_user.get_all_users.assert_called_once_with(10)

#     @pytest.mark.asyncio
#     async def test_create_user_success(self, user_service):
#         """Тест успешного создания пользователя"""
#         # Подготовка
#         user_data = UserCreate(
#             telegram_id=123456,
#             name="New User",
#             birth_date=date(1990, 1, 1)
#         )
#         created_user = self.create_test_user(
#             id=1,
#             telegram_id=123456,
#             name="New User"
#         )
#         user_service.rep_user.create = AsyncMock(return_value=created_user)

#         # Выполнение
#         result = await user_service.create_user(user_data)

#         # Проверка
#         assert result is not None
#         assert result.telegram_id == 123456
#         assert result.name == "New User"
#         user_service.rep_user.create.assert_called_once_with(user_data)

#     @pytest.mark.asyncio
#     async def test_update_user_success(self, user_service):
#         """Тест успешного обновления пользователя"""
#         # Подготовка
#         user_update = UserUpdate(name="Updated Name")
#         updated_user = self.create_test_user(
#             id=1,
#             name="Updated Name"
#         )
#         user_service.rep_user.update = AsyncMock(return_value=updated_user)

#         # Выполнение
#         result = await user_service.update_user(1, user_update)

#         # Проверка
#         assert result is not None
#         assert result.name == "Updated Name"
#         user_service.rep_user.update.assert_called_once_with(1, user_update)

#     @pytest.mark.asyncio
#     async def test_block_user_success(self, user_service):
#         """Тест успешной блокировки пользователя"""
#         # Подготовка - используем правильное имя поля blocked_id
#         block_data = BlockCreate(
#             blocked_id=2,  # Исправлено: blocked_user_id -> blocked_id
#             block_profile=True,
#             block_wishlists=False
#         )
#         block = MagicMock()
#         user_service.rep_block.block_user = AsyncMock(return_value=block)

#         # Выполнение
#         result = await user_service.block_user(1, block_data)

#         # Проверка
#         assert result is not None
#         user_service.rep_block.block_user.assert_called_once_with(1, block_data)

#     @pytest.mark.asyncio
#     async def test_unblock_user_success(self, user_service):
#         """Тест успешной разблокировки пользователя"""
#         # Подготовка
#         user_service.rep_block.unblock_user = AsyncMock(return_value=True)

#         # Выполнение
#         result = await user_service.unblock_user(1, 2)

#         # Проверка
#         assert result is True
#         user_service.rep_block.unblock_user.assert_called_once_with(1, 2)

#     @pytest.mark.asyncio
#     async def test_check_block_status(self, user_service):
#         """Тест проверки статуса блокировки"""
#         # Подготовка
#         user_service.rep_block.is_user_blocked = AsyncMock(return_value=True)

#         # Выполнение
#         result = await user_service.check_block_status(1, 2)

#         # Проверка
#         assert result is True
#         user_service.rep_block.is_user_blocked.assert_called_once_with(1, 2)

#     @pytest.mark.asyncio
#     async def test_get_user_block_list(self, user_service):
#         """Тест получения списка заблокированных пользователей"""
#         # Подготовка
#         blocked_user = self.create_test_user(id=2, name="Blocked User")
#         blocked_record = MagicMock()
#         blocked_record.blocked = blocked_user
#         blocked_record.block_profile = True
#         blocked_record.block_wishlists = False
#         blocked_record.created_at = datetime.now()

#         user_service.rep_block.get_user_block = AsyncMock(return_value=[blocked_record])

#         # Выполнение
#         result = await user_service.get_user_block(1)

#         # Проверка
#         assert result.total == 1
#         assert len(result.blocked_users) == 1
#         assert result.blocked_users[0].blocked_user.name == "Blocked User"
#         user_service.rep_block.get_user_block.assert_called_once_with(1)

#     @pytest.mark.asyncio
#     async def test_get_user_block_list_empty(self, user_service):
#         """Тест получения пустого списка заблокированных пользователей"""
#         # Подготовка
#         user_service.rep_block.get_user_block = AsyncMock(return_value=[])

#         # Выполнение
#         result = await user_service.get_user_block(1)

#         # Проверка
#         assert result.total == 0
#         assert len(result.blocked_users) == 0
#         user_service.rep_block.get_user_block.assert_called_once_with(1)

#     @pytest.mark.asyncio
#     async def test_get_user_for_main_screen(self, user_service):
#         """Тест получения данных для главного экрана"""
#         # Подготовка
#         user = self.create_test_user()
#         user_service.rep_user.get_user_by_id = AsyncMock(return_value=user)
#         user_service.serv_wishlist.get_user_wishlist = AsyncMock(return_value=[])
#         user_service.rep_wish.get_count_user_wish = AsyncMock(return_value=5)
#         user_service.rep_wishlist.get_count_user_wishlist = AsyncMock(return_value=3)
        
#         # Создаем правильный объект SubscribersResponse
#         mock_subscribers_response = SubscribersResponse(
#             subscribers=[],
#             total=0
#         )
#         user_service.serv_subs.get_user_subscribers = AsyncMock(return_value=mock_subscribers_response)
        
#         # Создаем мок для подписки
#         mock_subscription = MagicMock()
#         mock_subscription.model_dump = MagicMock(return_value={"items": []})
#         user_service.serv_subs.get_my_subscription = AsyncMock(return_value=mock_subscription)

#         # Выполнение
#         result = await user_service.get_user_for_main_screen(1)

#         # Проверка
#         assert result is not None
#         assert result.name == "Test User"
#         assert result.total_wish == 5
#         assert result.total_wishlist == 3
#         assert result.subscription == {"subscription": {"items": []}}
#         assert result.subsсribers.total == 0
#         assert len(result.subsсribers.subscribers) == 0
        
#         user_service.rep_user.get_user_by_id.assert_called_once_with(1)
#         user_service.serv_wishlist.get_user_wishlist.assert_called_once_with(
#             user_id=1, is_desc=True, limit=3
#         )
#         user_service.rep_wish.get_count_user_wish.assert_called_once_with(1)
#         user_service.rep_wishlist.get_count_user_wishlist.assert_called_once_with(1)
#         user_service.serv_subs.get_user_subscribers.assert_called_once_with(1, True, 2)
#         user_service.serv_subs.get_my_subscription.assert_called_once_with(1, True, 2)

#     # @pytest.mark.asyncio
#     # async def test_get_user_for_main_screen_with_data(self, user_service):
#     #     """Тест получения данных для главного экрана с реальными данными"""
#     #     # Подготовка
#     #     user = self.create_test_user()
#     #     user_service.rep_user.get_user_by_id = AsyncMock(return_value=user)
        
#     #     # Мокаем вишлисты
#     #     mock_wishlist = MagicMock()
#     #     mock_wishlist.id = 1
#     #     mock_wishlist.name = "Test Wishlist"
#     #     mock_wishlist.description = "Test Description"
#     #     user_service.serv_wishlist.get_user_wishlist = AsyncMock(return_value=[mock_wishlist])
        
#     #     user_service.rep_wish.get_count_user_wish = AsyncMock(return_value=10)
#     #     user_service.rep_wishlist.get_count_user_wishlist = AsyncMock(return_value=5)
        
#     #     # Создаем подписчиков с данными
#     #     mock_subscriber = MagicMock()
#     #     mock_subscriber.subscriber = self.create_test_user(id=3, name="Subscriber")
#     #     mock_subscriber.created_at = datetime.now()
        
#     #     mock_subscribers_response = SubscribersResponse(
#     #         subscribers=[{"subscriber": mock_subscriber}],
#     #         total=1
#     #     )
#     #     user_service.serv_subs.get_user_subscribers = AsyncMock(return_value=mock_subscribers_response)
        
#     #     # Создаем подписки с данными
#     #     mock_subscription_item = MagicMock()
#     #     mock_subscription_item.target_user = self.create_test_user(id=4, name="Subscribed User")
#     #     mock_subscription_item.created_at = datetime.now()
        
#     #     mock_subscription = MagicMock()
#     #     mock_subscription.model_dump = MagicMock(return_value={"subscriptions": [mock_subscription_item]})
#     #     user_service.serv_subs.get_my_subscription = AsyncMock(return_value=mock_subscription)

#     #     # Выполнение
#     #     result = await user_service.get_user_for_main_screen(1)

#     #     # Проверка
#     #     assert result is not None
#     #     assert result.name == "Test User"
#     #     assert result.total_wish == 10
#     #     assert result.total_wishlist == 5
#     #     assert len(result.wishlist_last_update) == 1
#     #     assert result.wishlist_last_update[0].name == "Test Wishlist"
#     #     assert result.subsсribers.total == 1

#     @pytest.mark.asyncio
#     async def test_get_user_for_main_screen_user_not_found(self, user_service):
#         """Тест когда пользователь не найден на главном экране"""
#         # Подготовка
#         user_service.rep_user.get_user_by_id = AsyncMock(return_value=None)

#         # Выполнение
#         result = await user_service.get_user_for_main_screen(999)

#         # Проверка
#         assert result is None
#         user_service.rep_user.get_user_by_id.assert_called_once_with(999)

#     @pytest.mark.asyncio
#     async def test_get_user_for_main_screen_with_empty_wishlists(self, user_service):
#         """Тест получения данных для главного экрана с пустыми вишлистами"""
#         # Подготовка
#         user = self.create_test_user()
#         user_service.rep_user.get_user_by_id = AsyncMock(return_value=user)
#         user_service.serv_wishlist.get_user_wishlist = AsyncMock(return_value=[])
#         user_service.rep_wish.get_count_user_wish = AsyncMock(return_value=0)
#         user_service.rep_wishlist.get_count_user_wishlist = AsyncMock(return_value=0)
        
#         mock_subscribers_response = SubscribersResponse(subscribers=[], total=0)
#         user_service.serv_subs.get_user_subscribers = AsyncMock(return_value=mock_subscribers_response)
        
#         mock_subscription = MagicMock()
#         mock_subscription.model_dump = MagicMock(return_value={"subscription": []})
#         user_service.serv_subs.get_my_subscription = AsyncMock(return_value=mock_subscription)

#         # Выполнение
#         result = await user_service.get_user_for_main_screen(1)

#         # Проверка
#         assert result is not None
#         assert result.total_wish == 0
#         assert result.total_wishlist == 0
#         assert len(result.wishlist_last_update) == 0
#         user_service.rep_wish.get_count_user_wish.assert_called_once_with(1)
#         user_service.rep_wishlist.get_count_user_wishlist.assert_called_once_with(1)