from typing import Optional, List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, func, desc
from sqlalchemy.orm import joinedload
from app.models.wish_wishlist import WishWishlist
from app.models.wish import Wish
from app.models.wishlist import Wishlist


class WishWishlistRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get(
        self,
        wish_id: int,
        wishlist_id: int,
    ) -> Optional[WishWishlist]:
        query = select(WishWishlist).where(
            and_(
                WishWishlist.wish_id == wish_id,
                WishWishlist.wishlist_id == wishlist_id
            )
        )
        result = await self.session.execute(query)
        return result.scalar_one_or_none()

    async def get_by_id(
        self,
        wish_wishlist_id: int
    ) -> Optional[WishWishlist]:
        query = (
            select(WishWishlist)
            .where(WishWishlist.id == wish_wishlist_id)
        )
        result = await self.session.execute(query)
        return result.scalar_one_or_none()

    async def get_wishes_from_wishlist(
        self,
        wishlist_id: int,
        limit: int = 10
    ) -> List[WishWishlist]:
        query = (
            select(WishWishlist)
            .where(WishWishlist.wishlist_id == wishlist_id)
            .options(joinedload(WishWishlist.wish))
            .order_by(WishWishlist.order_position)
            .limit(limit)
        )
        result = await self.session.execute(query)
        return list(result.unique().scalars().all())

    async def create_wish_to_wishlist(
        self,
        wish_id: int,
        wishlist_id: int,
        is_pinned: bool,
        order_position: Optional[int] = None
    ) -> Optional[WishWishlist]:
        existing = await self.get(wish_id, wishlist_id)
        if existing:
            return None
        wish_exists = await self.session.execute(
            select(Wish).where(Wish.id == wish_id)
        )
        if not wish_exists.scalar_one_or_none():
            return None
        wishlist_exists = await self.session.execute(
            select(Wishlist).where(Wishlist.id == wishlist_id)
        )
        if not wishlist_exists.scalar_one_or_none():
            return None

        if order_position is None:
            count = await self.count_wishes_in_wishlist(wishlist_id)
            order_position = count

        connection = WishWishlist(
            wish_id=wish_id,
            wishlist_id=wishlist_id,
            is_pinned=is_pinned,
            order_position=order_position
        )

        self.session.add(connection)
        await self.session.commit()
        await self.session.refresh(connection)
        return connection

    async def update_connection(
        self,
        connection_id: int,
        update_data
    ) -> Optional[WishWishlist]:
        connection = await self.get_by_id(connection_id)
        if not connection:
            return None
        for key, value in update_data.items():
            setattr(connection, key, value)
        await self.session.commit()
        await self.session.refresh(connection)
        return connection

    # async def update_connection_by_ids(
    #     self,
    #     wish_id: int,
    #     wishlist_id: int,
    #     **update_data
    # ) -> Optional[WishWishlist]:
    #     connection = await self.get(wish_id, wishlist_id)
    #     if not connection:
    #         return None
    #     for key, value in update_data.items():
    #         setattr(connection, key, value)

    #     await self.session.commit()
    #     await self.session.refresh(connection)
    #     return connection

    # async def update_connection_by_ids(
    #     self,
    #     connection_id: int,
    #     **update_data
    # ) -> Optional[WishWishlist]:
    #     connection = await self.get_by_id(connection_id)
    #     if not connection:
    #         return None
    #     for key, value in update_data.items():
    #         setattr(connection, key, value)

    #     await self.session.commit()
    #     await self.session.refresh(connection)
    #     return connection

    async def remove_wish_from_wishlist(
        self,
        wish_id: int,
        wishlist_id: int
    ) -> bool:
        connection = await self.get(wish_id, wishlist_id)
        if connection:
            await self.session.delete(connection)
            await self.session.commit()
            return True
        return False

    async def get_wish_from_all_wishlist(
        self,
        wish_id: int,
        limit: int = 50
    ) -> List[WishWishlist]:
        query = (
            select(WishWishlist)
            .where(WishWishlist.wish_id == wish_id)
            .options(
                joinedload(WishWishlist.wishlist).joinedload(Wishlist.owner)
            )
            .order_by(desc(WishWishlist.created_at))
            .limit(limit)
        )
        result = await self.session.execute(query)
        return list(result.scalars().all())

    async def get_wishlist_from_all_wishes(
        self,
        wishlist_id: int,
        limit: int = 10
    ) -> List[WishWishlist]:
        query = (
            select(WishWishlist)
            .where(WishWishlist.wishlist_id == wishlist_id)
            .order_by(WishWishlist.order_position)
            .limit(limit)
        )
        result = await self.session.execute(query)
        return list(result.scalars().all())

    async def count_wishes_in_wishlist(
        self,
        wishlist_id
    ) -> int:
        query = (
            select(func.count())
            .select_from(WishWishlist)
            .where(WishWishlist.wishlist_id == wishlist_id)
        )
        result = await self.session.execute(query)
        count = result.scalar_one_or_none()
        return count if count is not None else 0


    async def delete_wish_in_wishlists(self, wish_id: int) -> int:
        # query = (
        #     select(WishWishlist)
        #     .where(WishWishlist.wish_id == wish_id)
        # )
        # result = await self.session.execute(query)
        # connections = result.scalars().all()

        # count = 0
        # for connection in connections:
        #     await self.session.delete(connection)
        #     count += 1

        # if count > 0:
        #     await self.session.commit()

        # return count
        try:
            stmt = delete(WishWishlist).where(WishWishlist.wish_id == wish_id)
            result = await self.session.execute(stmt)
            # rowcount возвращает количество удаленных строк
            deleted_count = result.rowcount
            
            print(f"Deleted {deleted_count} wish-wishlist connections for wish_id: {wish_id}")
            
            return deleted_count
        except Exception as e:
            print(f"Error deleting wish-wishlist connections: {e}")
            return 0