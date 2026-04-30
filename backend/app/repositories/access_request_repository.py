from datetime import datetime
from typing import Optional, List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, and_, func, desc
from sqlalchemy.orm import joinedload

from app.models.access_request import AccessRequestStatus, AccessRequest
from app.models.user import User
from app.models.wishlist import Wishlist


class AccessRequestRepository():
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(
        self,
        wishlist_id: int,
        requester_id: int
    ) -> Optional[AccessRequest]:
        try:
            existing = await self.get_request(
                wishlist_id,
                requester_id
            )
            if existing:
                return None

            access_request = AccessRequest(
                wishlist_id=wishlist_id,
                requester_id=requester_id,
                status=AccessRequestStatus.PENDING
            )
            self.session.add(access_request)
            await self.session.commit()
            await self.session.refresh(access_request)
            return access_request
        except Exception:
            await self.session.rollback()
            return None

    async def get_request_id(
        self,
        request_id: int
    ) -> Optional[AccessRequest]:
        query = select(AccessRequest).where(AccessRequest.id == request_id)
        result = await self.session.execute(query)
        return result.scalar_one_or_none()

    async def update_status(
        self,
        request_id: int,
        status: AccessRequestStatus
    ) -> bool:
        try:
            processed_at = datetime.utcnow() if status != AccessRequestStatus.PENDING else None
            stmt = (
                update(AccessRequest)
                .where(AccessRequest.id == request_id)
                .values(status=status, processed_at=processed_at)
                .returning(AccessRequest)
            )
            result = await self.session.execute(stmt)
            await self.session.commit()
            request = result.scalar_one_or_none()
            if request:
                await self.session.refresh(request)
            return True
        except Exception as e:
            await self.session.rollback()
            print(f"Error uodating request: {e}")
            return False

    async def delete(
        self,
        request_id: int
    ) -> bool:
        try:
            request = await self.get_request_id(request_id)
            if not request:
                return False
            await self.session.delete(request)
            await self.session.commit()
            return True
        except Exception as e:
            await self.session.rollback()
            print(f"Error deleting wish: {e}")
            return False

    async def has_access(
        self,
        wishlist_id: int,
        user_id: int
    ) -> bool:
        query = (
            select(AccessRequest)
            .where(
                and_(
                    AccessRequest.wishlist_id == wishlist_id,
                    AccessRequest.requester_id == user_id,
                    AccessRequest.status == AccessRequestStatus.APPROVED
                )
            )
        )
        result = await self.session.execute(query)
        return result.scalar_one_or_none() is not None

    async def get_for_wishlist(
        self,
        wishlist_id: int,
        status: Optional[AccessRequestStatus] = None,
        limit: int = 100
    ) -> List[AccessRequest]:
        conditions = [AccessRequest.wishlist_id == wishlist_id]
        if status:
            conditions.append(AccessRequest.status == status)
        query = (
            select(AccessRequest)
            .where(and_(*conditions))
            .order_by(desc(AccessRequest.created_at))
            .limit(limit)
        )
        result = await self.session.execute(query)
        return list(result.scalars().all())

    async def get_for_requester(
        self,
        requester_id: int,
        status: Optional[AccessRequestStatus] = None,
        limit: int = 100
    ) -> List[AccessRequest]:
        conditions = [AccessRequest.requester_id == requester_id]
        if status:
            conditions.append(AccessRequest.status == status)
        query = (
            select(AccessRequest)
            .where(and_(*conditions))
            .order_by(desc(AccessRequest.created_at))
            .limit(limit)
        )
        result = await self.session.execute(query)
        return list(result.scalars().all())

    async def get_for_wishlist_owner(
        self,
        owner_id: int,
        status: Optional[AccessRequestStatus] = None,
        limit: int = 100
    ) -> List[AccessRequest]:
        query = (
            select(AccessRequest)
            .join(Wishlist, AccessRequest.wishlist_id == Wishlist.id)
            .where(Wishlist.user_id == owner_id)
        )

        if status:
            query = query.where(AccessRequest.status == status)

        query = query.order_by(desc(AccessRequest.created_at)).limit(limit)
        result = await self.session.execute(query)
        return list(result.scalars().all())

    async def get_request(
        self,
        wishlist_id: int,
        requester_id: int,
    ) -> Optional[AccessRequest]:
        query = (
            select(AccessRequest)
            .where(
                and_(
                    AccessRequest.wishlist_id == wishlist_id,
                    AccessRequest.requester_id == requester_id
                )
            )
        )
        result = await self.session.execute(query)
        return result.scalar_one_or_none()

    async def get_with_details(
        self,
        request_id: int
    ) -> Optional[AccessRequest]:
        query = (
            select(AccessRequest)
            .where(AccessRequest.id == request_id)
            .options(
                joinedload(AccessRequest.wishlist),
                joinedload(AccessRequest.requester)
            )
        )
        result = await self.session.execute(query)
        return result.scalar_one_or_none()

    async def get_for_requester_with_details(
        self,
        requester_id: int,
        status: Optional[AccessRequestStatus] = None,
        limit: int = 100
    ) -> List[AccessRequest]:
        conditions = [AccessRequest.requester_id == requester_id]

        if status:
            conditions.append(AccessRequest.status == status)

        query = (
            select(AccessRequest)
            .where(and_(*conditions))
            .options(
                joinedload(AccessRequest.wishlist).joinedload(Wishlist.owner)
            )
            .order_by(desc(AccessRequest.created_at))
            .limit(limit)
        )
        result = await self.session.execute(query)
        return list(result.scalars().all())

    async def get_for_wishlist_owner_with_details(
        self,
        owner_id: int,
        status: Optional[AccessRequestStatus] = None,
        limit: int = 100
    ) -> List[AccessRequest]:
        query = (
            select(AccessRequest)
            .join(Wishlist, AccessRequest.wishlist_id == Wishlist.id)
            .where(Wishlist.user_id == owner_id)
        )
        if status:
            query = query.where(AccessRequest.status == status)
        query = (
            query
            .options(joinedload(AccessRequest.requester))
            .order_by(desc(AccessRequest.created_at))
            .limit(limit)
        )
        result = await self.session.execute(query)
        return list(result.scalars().all())
