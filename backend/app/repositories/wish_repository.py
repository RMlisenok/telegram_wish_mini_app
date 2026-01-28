from typing import Optional, List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, func, desc, asc
from app.models.wish import Wish

from app.schemas.wish import WishCreate, WishUpdate


class WishRepository:
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
        wish_data: dict
    ) -> Optional[Wish]:
        # update_data = wish_data.model_dump(exclude_unset=True)
        if not wish_data:
            return await self.get(wish_id)
        stmt = (
            update(Wish)
            .where(Wish.id == wish_id)
            .values(**wish_data)
            .returning(Wish)
        )
        result = await self.session.execute(stmt)
        # await self.session.commit()
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

    async def get_user_wish(
        self,
        user_id: int,
        is_desc: bool = True,
        limit: int = 20
    ) -> List[Wish]:
        query = select(Wish).where(Wish.user_id == user_id)
        if is_desc:
            query = query.order_by(desc(Wish.status_is_finished))
        else:
            query = query.order_by(asc(Wish.status_is_finished))
        query = query.limit(limit)
        result = await self.session.execute(query)
        return list(result.scalars().all())

    async def get_count_user_wish(
        self,
        user_id: int,
    ) -> int:
        query = (select(func.count())
                 .select_from(Wish)
                 .where(Wish.user_id == user_id))
        result = await self.session.execute(query)
        return result.scalar()

    async def delete(
        self,
        wish_id: int
    ) -> bool:
        try:
            wish = await self.get(wish_id)
            if not wish:
                return False
            await self.session.delete(wish)
            return True
        except Exception as e:
            await self.session.rollback()
            print(f"Error deleting wish: {e}")
            return False
