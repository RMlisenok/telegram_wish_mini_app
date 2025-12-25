from typing import Optional, List
from sqlalchemy.ext.asyncio import AsyncSession

from app.repositories.user_repository import UserRepository
from app.repositories.block_repository import BlockRepository
from app.models.user import User
from app.schemas.user import UserCreate, UserResponse, UserUpdate
from app.schemas.block import BlockResponse


class UserService:
    def __init__(self, session: AsyncSession):
        self.rep_user = UserRepository(session)
        self.rep_block = BlockRepository(session)

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
        users = await self.rep_user.get_all_users(limit)
        return [UserResponse.model_validate(user) for user in users]

    async def create_user(self, user_data: UserCreate) -> User:
        user = await self.rep_user.create(user_data)
        return UserResponse.model_validate(user)

    async def update_user(
        self,
        user_id: int,
        user_data: UserUpdate
    ) -> Optional[UserResponse]:
        user = await self.rep_user.update(user_id, user_data)
        if user:
            return UserResponse.model_validate(user)
        return None

    async def block_user(
        self,
        blocker_id: int,
        blocked_id: int,
    ) -> Optional[BlockResponse]:
        block = await self.rep_block.block_user(blocker_id, blocked_id)
        if block:
            return BlockResponse.model_validate(block)
        return None

    async def unblock_user(
        self,
        blocker_id: int,
        blocked_id: int,
    ) -> bool:
        return await self.rep_block.unblock_user(blocker_id, blocked_id)

    async def check_block_status(
        self,
        blocker_id: int,
        blocked_id: int,
    ) -> bool:
        return await self.rep_block.is_user_blocked(blocker_id, blocked_id)

    async def get_user_block(
        self,
        blocker_id: int
    ) -> List[UserResponse]:
        users = await self.rep_block.get_user_block(blocker_id)
        return [UserResponse.model_validate(user) for user in users]
