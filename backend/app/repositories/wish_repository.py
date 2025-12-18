from typing import Optional, List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update
from app.models.wish import Wish

from app.schemas.wish import WishCreate, WishUpdate


class WishlistRepositories:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(
        self,
        wish_data: WishCreate
    ) -> Wish:
        wish = Wish(**wish_data.model_dump())
        self.session.add(wish)
        await self.session.commit()
        await self.session.refresh(wish)
        return wish

    async def update(
        self,
        wish_id: int,
        wish_data: WishUpdate
    ) -> Optional[Wish]:
        update_data = wish_data.model_dump(exclude_unset=True)
        if not update_data:
            return await self.get(wish_id)
        stmt = (
            update(Wish)
            .where(Wish.id == wish_id)
            .values(**update_data)
            .returning(Wish)
        )
        result = await self.session.execute(stmt)
        await self.session.commit()
        wish = result.scalar_one_or_none()

        if wish:
            await self.session.refresh(wish)
        return wish

    async def get(
        self,
        wish_id: int,
    ) -> Optional[Wish]:
        query = select(Wish).where(Wish.id == wish_id)
        result = await self.session.execute(query)
        return result.scalar_one_or_none()

    async def get_user_wishlist(
        self,
        user_id: int,
        limit: int = 20
    ) -> List[Wish]:
        query = select(Wish).where(Wish.user_id == user_id).limit(limit)
        result = await self.session.execute(query)
        return list(result.scalars().all())

    async def delete(
        self,
        wish_id: int
    ) -> bool:
        wish = await self.session.get(wish_id)
        if wish:
            await self.session.delete(wish)
            await self.session.commit()
            return True
        return False
