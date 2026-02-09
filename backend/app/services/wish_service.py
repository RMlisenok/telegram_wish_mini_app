from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession

from app.repositories.wish_repository import WishRepository
from app.repositories.wish_wishlist_repository import WishWishlistRepository
from app.schemas.wish import (
    WishCreate,
    WishResponse,
    WishUpdate,
    WishResponseMoreInfo,
    WishCreateDb
)
from app.core.s3_client import S3Client


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
        try:
            wish = await self.rep_wish.get(wish_id)
            if not wish:
                return None
            return WishResponse.model_validate(wish)
        except Exception as e:
            print(f"Exception: {e}")
            return None

    async def get_wish_with_wishlists_info(
        self,
        wish_id: int
    ) -> Optional[WishResponseMoreInfo]:
        try:
            wish = await self.rep_wish.get(wish_id)
            if not wish:
                return None

            list_wishlists = await self.rep_wish_wishlist.get_wish_from_all_wishlist(wish_id)
            wishlist_info = []
            for wishlist in list_wishlists:
                if wishlist.wishlist:
                    wishlist_info.append({
                        "id": wishlist.wishlist.id,
                        "name": wishlist.wishlist.name
                    })
            wish_respones = WishResponse.model_validate(wish)
            more_info_response = WishResponseMoreInfo(
                **wish_respones.model_dump(),
                wishlists=wishlist_info
            )
            return more_info_response
        except Exception as e:
            print(f"Exception: {e}")
            return None

    async def create_wish(
        self,
        user_id: int,
        wish_data: WishCreate
    ) -> WishResponse:
        # data = wish_data.model_dump()
        # data["user_id"] = user_id
        if not wish_data.photo:
            wish_data.photo = (
                "https://e4a6ce86-682d-4bf7-921e-9a1f5c537501."
                "selstorage.ru/d118dd34-8236-4e18-b22e-d7f03c1992c6.png"
            )
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
        if wish_data.photo is None:
            wish_data.photo = (
                "https://e4a6ce86-682d-4bf7-921e-9a1f5c537501."
                "selstorage.ru/d118dd34-8236-4e18-b22e-d7f03c1992c6.png"
            )
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

    async def delete_wish_in_wishlists(
        self,
        wish_id: int,
        # user_id: int
    ) -> bool:
        try:
            wish = await self.get_wish(wish_id)
            if not wish:
                return False
            deleted_count = await self.rep_wish_wishlist.delete_wish_in_wishlists(wish_id)
            print(f"Deleted: {deleted_count}")
            return True
        except Exception as e:
            print(f"Error: {e}")
            return False

    async def get_user_wish(
        self,
        user_id: int,
        is_desc: bool = True,
        limit: int = 20
    ) -> Optional[WishResponse]:
        wishes = await self.rep_wish.get_user_wish(user_id, is_desc, limit)
        return [WishResponse.model_validate(wish) for wish in wishes]

    async def get_user_wish_sorted(
        self,
        user_id: int,
        is_finish: bool = True,
        limit: int = 20
    ) -> Optional[WishResponse]:
        wishes = await self.rep_wish.get_user_wish_sorted(
            user_id,
            is_finish,
            limit
        )
        return [WishResponse.model_validate(wish) for wish in wishes]
