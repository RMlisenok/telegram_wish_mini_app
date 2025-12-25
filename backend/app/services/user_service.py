from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession

from app.repositories.user_repository import UserRepository
from app.models.user import User
from app.schemas.user import UserCreate, UserResponse


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

    async def create_user(self, user_data: UserCreate) -> User:
        user = await self.rep_user.create(user_data)
        return UserResponse.model_validate(user)
