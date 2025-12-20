from typing import Optional, List
from sqlalchemy.ext.asyncio import AsyncSession

from app.repositories.wish_reservation_repository import WishReservationRepository
from app.repositories.wish_wishlist_repository import WishWishlistRepository
from app.repositories.wishlist_repository import WishlistRepository
from app.repositories.wish_repository import WishRepository
from app.schemas.wish_reservation import ReservationCreate, ReservationResponse


class ReservationService:
    def __init__(
        self,
        session: AsyncSession
    ):
        self.session = session
        self.rep_reservation = WishReservationRepository(session)
        self.rep_wish = WishRepository(session)
        self.rep_wishlist = WishlistRepository(session)
        self.rep_wish_wishlist = WishWishlistRepository(session)

    async def get_reservation(
        self,
        reservation_id: int
    ) -> Optional[ReservationResponse]:
        reservation = await self.rep_reservation.get(reservation_id)
        if not reservation:
            return None
        response = ReservationResponse.model_validate(reservation)
        return response

    async def create_reservation(
        self,
        user_id: int,
        reservation_data: ReservationCreate
    ) -> Optional[ReservationResponse]:
        is_reserved = await self.rep_reservation.check_wish_reservation(
            reservation_data.wish_wishlist_id
        )
        if is_reserved:
            return None
        connection = await self.rep_wish_wishlist.get_by_id(
            reservation_data.wish_wishlist_id
        )
        if not connection:
            return None
        
        reservation = await self.rep_reservation.create(
            wish_wishlist_id=reservation_data.wish_wishlist_id,
            reserved_by_id=user_id
        )
        if reservation:
            await self.rep_wish.update(connection.wish_id, is_booked=True)
            await self.session.commit()
            return ReservationResponse.model_validate(reservation)
        return None

    async def remove_reservation(
        self,
        reservation_id: int
    ) -> bool:
        reservation = self.rep_reservation.get(reservation_id)
        if not reservation:
            return False
        connect = self.rep_wish_wishlist.get_by_id(
            reservation.wish_wishlist_id
        )
        remove_status = await self.remove_reservation(reservation_id)

        if remove_status and connect:
            other_reservation = await self.rep_reservation.get_wish(
                reservation.wish_wishlist_id
            )
            if not other_reservation:
                await connect.wish.update(is_booked=False)
                await self.session.commit()
        return remove_status

    async def get_user_reservation(
        self,
        user_id: int,
        limit: 10
    ) -> List[ReservationResponse]:
        reservations = self.rep_reservation.get_user_reservations(
            reserved_id=user_id,
            limit=limit
        )
        return [ReservationResponse.model_validate(res) for res in reservations]

    async def get_wish_reservation(
        self,
        wish_wishlist_id: int,
        limit: int = 10
    ) -> List[ReservationResponse]:
        reservations = self.rep_reservation.get_reservations_by_wish_wishlist(
            wish_wishlist_id=wish_wishlist_id,
            limit=limit
        )
        return [ReservationResponse.model_validate(res) for res in reservations]
