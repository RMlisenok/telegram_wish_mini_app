from typing import Optional, List
from sqlalchemy.ext.asyncio import AsyncSession

from app.repositories.wishlist_repository import WishlistRepository
from app.repositories.wish_wishlist_repository import WishWishlistRepository
from app.models.wishlist import Wishlist
from app.models.wish_wishlist import WishWishlist
from app.schemas.wishlist import WishlistCreate, WishlistCreateDb, WishlistResponse, WishlistUpdate
from app.schemas.wish_wishlist import WishWishlistCreate, WishWishlistUpdate, WishWishlistResponse, WishInWishlistResponse


class WishlistService:
    def __init__(
        self,
        session: AsyncSession
    ):
        self.session = session
        self.rep_wishlist = WishlistRepository(session)
        self.rep_wish_wishlist = WishWishlistRepository(session)

    async def get_wishlist(
        self,
        wishlist_id: int
    ) -> Optional[Wishlist]:
        wishlist = await self.rep_wishlist.get(wishlist_id)
        if wishlist:
            response = WishlistResponse.model_validate(wishlist)
            response.wishes_count = await self.rep_wish_wishlist.count_wishes_in_wishlist(wishlist_id)
            return response
        return None

    async def create_wishlist(
        self,
        user_id: int,
        wishlist_data: WishlistCreate
    ) -> WishlistResponse:
        wishlist_with_user = WishlistCreateDb(
            user_id=user_id,
            **wishlist_data.model_dump()
        )
        wishlist = await self.rep_wishlist.create(wishlist_with_user)
        response = WishlistResponse.model_validate(wishlist)
        response.wishes_count = 0
        return response

    async def update_wishlist(
        self,
        wishlist_id: int,
        wishlist_data: WishlistUpdate
    ) -> Optional[WishlistResponse]:

        update_data = wishlist_data.model_dump(exclude_unset=True)
        wishlist = await self.rep_wishlist.update(wishlist_id, update_data)
        if wishlist:
            return await self.get_wishlist(wishlist_id)
        return None

    async def delete(
        self,
        wishlist_id: int
    ) -> bool:
        success = await self.rep_wishlist.delete(wishlist_id)
        if success:
            await self.session.commit()
        return success

    async def get_user_wishlist(
        self,
        user_id: int,
        limit: int = 10
    ) -> List[WishlistResponse]:
        wishlists = await self.rep_wishlist.get_user_wishlist(user_id, limit)

        result = []
        for wishlist in wishlists:
            response = WishlistResponse.model_validate(wishlist)
            count = await self.rep_wish_wishlist.count_wishes_in_wishlist(
                wishlist.id
            )
            response.wishes_count = count
            result.append(response)
        return result

    async def get_wishes_from_wishlist(
        self,
        wishlist_id: int,
        limit: int = 10
    ) -> List[dict]:
        connections = await self.rep_wish_wishlist.get_wishes_from_wishlist(
            wishlist_id,
            limit
        )
        result = []
        for connection in connections:
            # Создаем объект ответа
            wish_data = WishInWishlistResponse(
                # Поля из Wish
                id=connection.wish.id,
                name=connection.wish.name,
                photo=connection.wish.photo,
                url_gift=connection.wish.url_gift,
                price=float(connection.wish.price) if connection.wish.price else None,
                currency=connection.wish.currency,
                description=connection.wish.description,
                is_booked=connection.wish.is_booked,
                status_is_finished=connection.wish.status_is_finished,
                created_at=connection.wish.created_at,
                updated_at=connection.wish.updated_at,

                # Поля из WishWishlist
                connection_id=connection.id,
                is_pinned=connection.is_pinned,
                order_position=connection.order_position,
                added_at=connection.created_at
            )
            result.append(wish_data)

        return result

    async def add_wish_to_wishlist(
        self,
        connection_data: WishWishlistCreate
    ) -> Optional[WishWishlistResponse]:
        connection = await self.rep_wish_wishlist.create_wish_to_wishlist(
            connection_data.wish_id,
            connection_data.wishlist_id,
            connection_data.is_pinned,
            connection_data.order_position
        )
        if connection:
            return WishWishlistResponse.model_validate(connection)
        return None

    async def update_wihs_in_wishlits(
        self,
        connection_id: int,
        update_data: WishWishlistUpdate
    ) -> Optional[WishWishlistResponse]:
        data = update_data.model_dump(exclude_unset=True)
        connection = await self.rep_wish_wishlist.update_connection(
            connection_id,
            data
        )
        if connection:
            return WishWishlistResponse.model_validate(connection)
        return None

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
    ) -> List[WishWishlistResponse]:

        connection = await self.rep_wish_wishlist.get_wishlist_from_all_wishes(
            wishlits_id,
            limit
        )
        if connection:
            result = []
            for conn in connection:
                response = WishWishlistResponse.model_validate(conn)
                result.append(response)
            return result
        return None
