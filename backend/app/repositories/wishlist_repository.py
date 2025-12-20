from typing import Optional, List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update
from app.models.wishlist import Wishlist


from app.schemas.wishlist import WishlistCreate, WishlistUpdate


class WishlistRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(
        self,
        wishlist_data: WishlistCreate
    ) -> Wishlist:
        wishlist = Wishlist(**wishlist_data.model_dump())
        self.session.add(wishlist)
        await self.session.commit()
        await self.session.refresh(wishlist)
        return wishlist

    async def get(
        self,
        wishlist_id: int,
    ) -> Optional[Wishlist]:
        query = select(Wishlist).where(Wishlist.id == wishlist_id)
        result = await self.session.execute(query)
        return result.scalar_one_or_none()

    async def get_user_wishlist(
        self,
        user_id: int,
        limit: int = 10
    ) -> List[Wishlist]:
        query = (
            select(Wishlist)
            .where(Wishlist.user_id == user_id)
            .limit(limit)
        )
        result = await self.session.execute(query)
        return list(result.scalars().all())

    async def update(
        self,
        wishlist_id: int,
        wishlist_data: WishlistUpdate
    ) -> Optional[Wishlist]:
        # update_data = wishlist_data.model_dump(exclude_unset=True)

        if not wishlist_data:
            return await self.get(wishlist_id)

        stmt = (
            update(Wishlist)
            .where(Wishlist.id == wishlist_id)
            .values(**wishlist_data)
            .returning(Wishlist)
        )

        result = await self.session.execute(stmt)
        await self.session.commit()

        wishlist = result.scalar_one_or_none()

        if wishlist:
            await self.session.refresh(wishlist)
        return wishlist

    async def delete(
        self,
        wishlist_id
    ) -> bool:
        try:
            wishlist = await self.get(wishlist_id)
            if not wishlist:
                return False
            await self.session.delete(wishlist)
            return True
        except Exception as e:
            print(f"Error deleting wishlist: {e}")
            return False
