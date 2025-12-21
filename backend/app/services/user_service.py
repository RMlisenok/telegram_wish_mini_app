from typing import Optional, List
from sqlalchemy.ext.asyncio import AsyncSession

from app.repositories.user_repository import UserRepository
from app.models.user import User
from app.schemas.user import UserCreate, UserResponse, UserUpdate


class UserService:
    def __init__(self, session: AsyncSession):
        self.rep_user = UserRepository(session)

    async def get_user(self, user_id: int) -> Optional[User]:
        return await self.rep_user.get_user_by_id(user_id)

    async def get_user_by_telegram_id(
        self,
        telegram_id: int
    ) -> Optional[User]:
        return await self.rep_user.get_user_by_tg_id(telegram_id)

    async def get_all_users(
        self,
        limit: int = 10
    ) -> List[UserResponse]:
        users = await self.get_all_users(limit)
        return [UserResponse.model_validate(user) for user in users]

    async def create_user(self, user_data: UserCreate) -> User:
        user = await self.rep_user.create(user_data)
        return UserResponse.model_validate(user)

    async def update_user(
        self,
        user_id: int,
        user_data: UserUpdate
    ) -> Optional[UserResponse]:
        pass
