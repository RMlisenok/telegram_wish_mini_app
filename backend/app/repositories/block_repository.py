from typing import Optional, List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, and_

from app.models.block import BlockedUser
from app.models.user import User
from app.schemas.block import BlockCreate, BlockResponse


class BlockRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_block(
        self,
        blocker_id: int,
        blocked_id: int
    ) -> Optional[BlockedUser]:
        query = (
            select(BlockedUser)
            .where(
                and_(
                    BlockedUser.blocker_id == blocker_id,
                    BlockedUser.blocked_id == blocked_id
                )
            )
        )
        result = await self.session.execute(query)
        return result.scalar_one_or_none()

    async def block_user(
        self,
        blocker_id: int,
        blocked_id: int
    ) -> Optional[BlockedUser]:
        existing = await self.get_block(blocker_id, blocked_id)
        if existing:
            return existing

        block = BlockedUser(
            blocker_id=blocker_id,
            blocked_id=blocked_id
        )
        self.session.add(block)
        await self.session.commit()
        await self.session.refresh()
        return block

    async def unblock_user(
        self,
        blocker_id: int,
        blocked_id: int
    ) -> bool:
        block = await self.get_block(blocker_id, blocked_id)
        if not block:
            return False
        await self.session.delete(block)
        return True

    async def is_user_blocked(
        self,
        blocker_id: int,
        blocked_id: int
    ) -> bool:
        block = await self.get_block(blocker_id, blocked_id)
        return block is not None

    async def get_user_block(
        self,
        blocker_id: int
    ) -> List[User]:
        query = (
            select(BlockedUser.blocked_id)
            .where(BlockedUser.blocker_id == blocker_id)
        )
        result = await self.session.execute(query)
        blocked_ids = [row[0] for row in result.all()]
        if not blocked_ids:
            return []
        user_query = (
            select(User)
            .where(User.id.in_(blocked_ids))
        )
        user_res = await self.session.execute(user_query)
        return list(user_res.scalars().all())
