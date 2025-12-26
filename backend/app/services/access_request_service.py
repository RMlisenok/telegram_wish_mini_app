from typing import Optional, List, Tuple
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.access_request import AccessRequestStatus, AccessRequest
from app.repositories.access_request_repository import AccessRequestRepository
from app.repositories.user_repository import UserRepository
from app.repositories.wishlist_repository import WishlistRepository
from app.schemas.access_request import (
    AccessRequestCreate,
    AccessRequestResponse,
    AccessRequestWithDetails,
    UpdateAccessRequest
)


class AccessRequestService():
    def __init__(self, session: AsyncSession):
        self.session = session
        self.rep_access = AccessRequestRepository(session)
        self.rep_user = UserRepository(session)
        self.rep_wishlist = WishlistRepository(session)

    async def create_request(
        self,
        user_id: int,
        request_data: AccessRequestCreate
    ) -> Optional[AccessRequestWithDetails]:
        wishlist = await self.rep_wishlist.get(request_data.wishlist_id)
        if not wishlist:
            raise ValueError("Wishlist not found")
        if wishlist.user_id == user_id:
            raise ValueError("You cannot request access to your wishlist")
        if wishlist.typeprivacy == "public":
            raise ValueError("Wishlist is public, request not needed")
        has_access = await self.rep_access.has_access(
            wishlist_id=request_data.wishlist_id,
            user_id=user_id
        )
        if has_access:
            raise ValueError("You have access for this wishlsit")
        access_request = await self.rep_access.create(
            request_data.wishlist_id,
            requester_id=user_id
        )
        if not access_request:
            raise ValueError("Dont created access")
        return await self.get_request_with_details(access_request.id)

    async def get_request(
        self,
        request_id: int,
        user_id: int
    ) -> Optional[AccessRequestWithDetails]:
        access_request = await self.rep_access.get_request_id(request_id)
        if not access_request:
            return None
        if not await self.can_view_request(access_request, user_id):
            raise ValueError("Dont access to view this request")
        return await self.get_request_with_details(access_request.id)

    async def update_request_status(
        self,
        request_id: int,
        update_data: UpdateAccessRequest,
        user_id: int
    ) -> Optional[AccessRequestWithDetails]:
        access_request = await self.rep_access.get_request_id(request_id)
        if not access_request:
            raise ValueError("Access request not found")
        wishlist = await self.rep_wishlist.get(access_request.wishlist_id)
        if not wishlist or wishlist.user_id != user_id:
            raise ValueError("Only owned wishlist can change status")
        if access_request.status != AccessRequestStatus.PENDING:
            raise ValueError("This request alreade handler")

        success = await self.rep_access.update_status(
            request_id=access_request.id,
            status=update_data
        )

        if not success:
            raise ValueError("Error for update status")
        return await self.get_request_with_details(access_request.id)

    async def get_request_with_details(
        self,
        request_id: int
    ) -> Optional[AccessRequestWithDetails]:
        access_request = await self.rep_access.get_with_details(
            request_id=request_id
        )
        if not access_request:
            return None

        return await self.format_request_response(access_request)

    async def format_request_response(
        self,
        access_request: AccessRequest
    ) -> AccessRequestWithDetails:
        wishlist = access_request.wishlist if hasattr(
            access_request,
            "wishlist"
        ) else None
        requester = access_request.requester if hasattr(
            access_request,
            "requester"
        ) else None

        owner_id = None
        owner_name = None
        if wishlist:
            owner_id = wishlist.user_id
            if hasattr(wishlist, "owner") and wishlist.owner:
                owner_name = wishlist.owner.name
        return AccessRequestWithDetails(
            id=access_request.id,
            wishlist_id=access_request.wishlist_id,
            requester_id=access_request.requester_id,
            status=access_request.status,
            created_at=access_request.created_at,
            processed_at=access_request.processed_at,
            wishlist_name=wishlist.name if wishlist else None,
            wishlist_photo=wishlist.photo if wishlist else None,
            requester_name=requester.name if requester else None,
            requester_photo=requester.name if requester else None,
            owner_id=owner_id,
            owner_name=owner_name
        )
