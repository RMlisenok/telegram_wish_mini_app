from typing import Optional, List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.models.wish_reservation import WishReservation


class WishReservationRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get(
        self,
        wish_reservation_id: int
    ) -> Optional[WishReservation]:
        query = (
            select(WishReservation)
            .where(WishReservation.id == wish_reservation_id)
        )
        result = await self.session.execute(query)
        return result.scalar_one_or_none()

    async def get_reservations_by_wish_wishlist(
        self,
        wish_wishlist_id: int,
        limit: int = 10
    ) -> List[WishReservation]:
        query = (
            select(WishReservation)
            .where(WishReservation.wish_wishlist_id == wish_wishlist_id)
            .order_by(WishReservation.created_at.desc())
            .limit(limit)
        )
        result = await self.session.execute(query)
        return list(result.scalars().all())

    async def get_user_reservations(
        self,
        user_id: int,
        limit: int = 10
    ) -> List[WishReservation]:
        query = (
            select(WishReservation)
            .where(WishReservation.reserved_by_id == user_id)
            .limit(limit)
        )
        result = await self.session.execute(query)
        return list(result.scalars().all())

    async def check_wish_reservation(
        self,
        wish_wihslist_id: int
    ) -> bool:
        query = (
            select(WishReservation)
            .where(WishReservation.wish_wishlist_id == wish_wihslist_id)
        )
        result = await self.session.execute(query)
        return result.scalar_one_or_none is not None

    async def create(
        self,
        wish_wishlist_id: int,
        user_id: int
    ) -> Optional[WishReservation]:
        existing = self.check_wish_reservation(wish_wishlist_id)
        if existing:
            return None
        reservation = WishReservation(
            wish_wishlist_id=wish_wishlist_id,
            reserved_by_id=user_id
        )
        self.session.add(reservation)
        await self.session.commit()
        await self.session.refresh(reservation)
        return reservation

    async def delete(
        self,
        wish_wishlist_id: int,
        reserved_by_id: int
    ) -> bool:
        reservation = self.get(wish_wishlist_id, reserved_by_id)
        if reservation:
            await self.session.delete(reservation)
            await self.session.commit()
            return True
        return False
