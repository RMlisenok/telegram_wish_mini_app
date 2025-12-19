from typing import Optional, List
from sqlalchemy.ext.asyncio import AsyncSession

from app.repositories.wishlist_repository import WishlistRepository
from app.repositories.wish_wishlist_repository import WishWishlistRepository
from app.models.wishlist import Wishlist
from app.schemas.wishlist import WishlistCreate, WishlistResponse, WishlistUpdate
from app.schemas.wish_wishlist import WishWishlistCreate, WishWishlistUpdate


class WishlistService:
    def __init__(
        self,
        session: AsyncSession
    ):
        self.rep_wishlist = WishlistRepository(session)
        self.rep_wish_wishlist = WishWishlistRepository(session)

    async def get_wishlist(
        self,
        wishlist_id: int
    ) -> Optional[Wishlist]:
        wishlist = await self.rep_wishlist.get(wishlist_id)
        if not wishlist:
            return None

        connections = await self.rep_wish_wishlist.get_wishlist_from_all_wishes(
            wishlist_id=wishlist_id,
            limit=10
        )
        response = WishlistResponse.model_validate(wishlist)
        response.wishes = [connection.wish for connection in connections]
        response.wishes_count = len(response.wishes)
        return response

    async def create_wishlist(
        self,
        user_id: int,
        wishlist_data: WishlistCreate
    ) -> WishlistResponse:
        data = wishlist_data.model_dump()
        data["user"] = user_id
        wishlist = self.rep_wishlist.create(data)
        response = WishlistResponse.model_validate(wishlist)
        response.wishes_count = 0
        return response

    async def update_wishlist(
        self,
        wishlist_id: int,
        wishlist_data: WishlistUpdate
    ) -> Optional[WishlistResponse]:

        update_data = wishlist_data.model_dump(exclude_unset=True)
        wishlist = self.rep_wishlist.update(wishlist_id, update_data)
        if wishlist:
            return await self.get_wishlist(wishlist_id)
        return None

    async def delete(
        self,
        wishlist_id: int
    ) -> bool:
        return await self.rep_wishlist.delete(wishlist_id)

    async def get_user_wishlist(
        self,
        user_id: int,
        limit: 10
    ) -> List[WishlistResponse]:
        wishlists = await self.rep_wishlist.get_user_wishlist(user_id, limit)

        result = []
        for wishlist in wishlists:
            response = WishlistResponse.model_validate(wishlist)
            response = await self.rep_wish_wishlist.count_wishes_in_wishlist(
                wishlist.id
            )
            result.append(response)
        return result

    async def add_wish_to_wishlist(
        self,
        connection_data: WishWishlistCreate
    ) -> Optional[WishWishlist]:
        return await self.rep_wish_wishlist.create_wish_to_wishlist(
            connection_data.wish_id,
            connection_data.wishlist_id,
            connection_data.is_pinned,
            connection_data.order_position
        )
    
    async def update_wihs_in_wishlits(
        self,
        connection_id: int,
        update_data: WishWishlistUpdate
    ) -> Optional[WishWishlist]:
        data = update_data.model_dump(exclude_unset=True)
        return await self.rep_wish_wishlist.create_wish_to_wishlist(
            connection_id,
            data
        )

    async def remove_wish_from_wishlist(
        self,
        wish_id: int,
        wishlist_id: int
    ) -> bool:
        return await self.rep_wish_wishlist.remove_wish_from_wishlist(
            wish_id,
            wishlist_id
        )

    async def get_wishlist_connection(
        self,
        wishlits_id: int,
        limit: int,
    ) -> List[WishWishlist]:

        return await self.rep_wish_wishlist.get_wishlist_from_all_wishes(
            wishlits_id,
            limit
        )
