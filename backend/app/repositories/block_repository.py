from typing import Optional, List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, and_, func, desc
from sqlalchemy.orm import joinedload
from app.models.block import BlockedUser
from app.models.user import User
from app.schemas.block import BlockCreate, BlockResponse, UpdateBlock


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
        block_data: BlockCreate,
    ) -> Optional[BlockedUser]:
        existing = await self.get_block(blocker_id, block_data.blocked_id)
        if existing:
            return existing

        block = BlockedUser(
            blocker_id=blocker_id,
            blocked_id=block_data.blocked_id,
            block_profile=block_data.block_profile,
            block_wishlists=block_data.block_wishlists
        )
        self.session.add(block)
        await self.session.commit()
        await self.session.refresh(block)
        return block

    async def update_block(
        self,
        blocker_id: int,
        blocked_id: int,
        update_data: UpdateBlock
    ) -> Optional[BlockedUser]:
        existing = await self.get_block(blocker_id, blocked_id)
        if not existing:
            return None
        stmt = (
            update(BlockedUser)
            .where(
                and_(
                    BlockedUser.blocked_id == blocked_id,
                    BlockedUser.blocker_id == blocker_id
                )
            )
            .values(
                block_profile=update_data.block_profile,
                block_wishlists=update_data.block_wishlists,
                updated_at=func.now()
            )
            .returning(BlockedUser)
        )

        result = await self.session.execute(stmt)
        await self.session.commit()
        blocked = result.scalar_one_or_none()
        if blocked:
            await self.session.refresh(blocked)
        return blocked

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
    ) -> List[BlockedUser]:
        query = (
            select(BlockedUser)
            .where(BlockedUser.blocker_id == blocker_id)
            .options(joinedload(BlockedUser.blocked))
            .order_by(desc(BlockedUser.updated_at))
        )
        result = await self.session.execute(query)
        return list(result.scalars().all())
