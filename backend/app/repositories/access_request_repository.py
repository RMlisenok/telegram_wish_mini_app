from typing import Optional, List, Tuple
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete, and_, func
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
            existing = await self.get_pending_request(
                wishlist_id,
                requester_id
            )
            if existing:
                return existing

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

    async def get(
        self,
        request_id: int
    ) -> Optional[AccessRequest]:
        query = select(AccessRequest).where(AccessRequest.id == request_id)
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

    async def get_pending_request(
        self,
        wishlist_id: int,
        requester_id: int,
    ) -> Optional[AccessRequest]:
        query = (
            select(AccessRequest)
            .where(
                and_(
                    AccessRequest.wishlist_id == wishlist_id,
                    AccessRequest.requester_id == requester_id,
                    AccessRequest.status == AccessRequestStatus.PENDING
                )
            )
        )
        result = await self.session.execute(query)
        return result.scalar_one_or_none()
