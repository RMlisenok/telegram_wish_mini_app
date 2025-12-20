from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession

from app.repositories.wish_repository import WishRepository
from app.repositories.wish_wishlist_repository import WishWishlistRepository
from app.schemas.wish import WishCreate, WishResponse, WishUpdate, WishShort, WishCreateDb


class WishService:
    def __init__(
        self,
        session: AsyncSession
    ):
        self.session = session
        self.rep_wish = WishRepository(session)
        self.rep_wish_wishlist = WishWishlistRepository(session)

    async def get_wish(
        self,
        wish_id: int
    ) -> Optional[WishResponse]:
        wish = await self.rep_wish.get(wish_id)
        if not wish:
            return None
        return WishResponse.model_validate(wish)

    async def create_wish(
        self,
        user_id: int,
        wish_data: WishCreate
    ) -> WishResponse:
        # data = wish_data.model_dump()
        # data["user_id"] = user_id
        wish_data_wish_user = WishCreateDb(
            user_id=user_id,
            **wish_data.model_dump()
        )
        wish = await self.rep_wish.create(wish_data_wish_user)
        response = WishResponse.model_validate(wish)
        return response

    async def update_wish(
        self,
        wish_id,
        wish_data: WishUpdate
    ) -> Optional[WishResponse]:
        update_data = wish_data.model_dump(exclude_unset=True)
        wish = await self.rep_wish.update(wish_id, update_data)
        if wish:
            return await self.get_wish(wish_id)
        return None

    async def delete_wish(
        self,
        wish_id: int
    ) -> bool:
        success = await self.rep_wish.delete(wish_id)
        if success:
            await self.session.commit()
        return success

    async def get_user_wish(
        self,
        user_id: int,
        limit: int = 10
    ) -> Optional[WishShort]:
        wishes = await self.rep_wish.get_user_wishlist(user_id, limit)
        return [WishShort.model_validate(wish) for wish in wishes]
