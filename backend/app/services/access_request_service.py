from typing import Optional, List, Tuple
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.wishlist import TypePrivacyEnum
from app.models.access_request import AccessRequestStatus, AccessRequest
from app.repositories.access_request_repository import AccessRequestRepository
from app.repositories.user_repository import UserRepository
from app.repositories.wishlist_repository import WishlistRepository
from app.schemas.access_request import (
    AccessRequestCreate,
    AccessRequestResponse,
    AccessRequestsResponse,
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
    ) -> Optional[AccessRequestResponse]:
        wishlist = await self.rep_wishlist.get(request_data.wishlist_id)
        if not wishlist:
            raise ValueError("Wishlist not found")
        if wishlist.user_id == user_id:
            raise ValueError("You cannot request access to your wishlist")
        if wishlist.typeprivacy == TypePrivacyEnum.public:
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

        try:
            from app.services.notification_service_bot import NotificationService
            from app.core.bot_setup import bot
            notif_service = NotificationService(bot)

            await notif_service.notify_access_request(
                session=self.session,
                requester_id=user_id,
                owner_id=wishlist.user_id,
                wishlist_name=wishlist.name,
                request_id=access_request.id
            )
        except Exception as e:
            print(f"Ошибка уведомления о заявке: {e}")

        return AccessRequestResponse.model_validate(access_request)

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
            raise ValueError("This request already handled")

        success = await self.rep_access.update_status(
            request_id=access_request.id,
            status=update_data.status
        )

        if not success:
            raise ValueError("Error for update status")
        try:
            from app.core.bot_setup import bot
            status_action = "одобрил" if update_data.status == AccessRequestStatus.APPROVED else "отклонил"

            # Находим данные того, кто просил доступ
            requester = await self.rep_user.get_user_by_id(access_request.requester_id)
            if requester and requester.telegram_id:
                msg = f"Владелец {status_action} ваш доступ к вишлисту \"{wishlist.name}\"."
                await bot.send_message(requester.telegram_id, msg)
        except Exception as e:
            print(f"Ошибка уведомления об ответе на заявку: {e}")

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

    # async def update_request_status(
    #     self,
    #     request_id: int,
    #     update_data: UpdateAccessRequest,
    #     user_id: int
    # ) -> Optional[AccessRequestWithDetails]:
    #     access_request = await self.rep_access.get_request_id(request_id)
    #     if not access_request:
    #         raise ValueError("Access request not found")
    #     wishlist = await self.rep_wishlist.get(access_request.wishlist_id)
    #     if not wishlist or wishlist.user_id != user_id:
    #         raise ValueError("Only owned wishlist can change status")
    #     if access_request.status != AccessRequestStatus.PENDING:
    #         raise ValueError("This request alreade handler")
    #
    #     success = await self.rep_access.update_status(
    #         request_id=access_request.id,
    #         status=update_data.status
    #     )
    #
    #     if not success:
    #         raise ValueError("Error for update status")
    #     return await self.get_request_with_details(access_request.id)

    async def delete_request(
        self,
        request_id: int,
        user_id: int
    ) -> bool:
        access_request = await self.rep_access.get_request_id(request_id)
        if not access_request:
            return False
        wishlist = await self.rep_wishlist.get(access_request.wishlist_id)
        if not wishlist:
            return False
        can_delete = (
            access_request.requester_id == user_id or
            wishlist.user_id == user_id
        )
        if not can_delete:
            raise ValueError("Not have permission to delete this request")
        if access_request.status != AccessRequestStatus.PENDING:
            raise ValueError("Delete error, this request arleady handler")
        return await self.rep_access.delete(request_id)

    async def get_my_requests(
        self,
        user_id: int,
        status: Optional[AccessRequestStatus] = None,
        limit: int = 100
    ) -> AccessRequestsResponse:
        requests = await self.rep_access.get_for_requester_with_details(
            requester_id=user_id,
            status=status,
            limit=limit
        )
        request_list = []
        for req in requests:
            request_list.append(await self.format_request_response(req))
        total = len(request_list)

        return AccessRequestsResponse(
            requests=request_list,
            total=total
        )

    async def get_requests_for_my_wishlists(
        self,
        user_id: int,
        status: Optional[AccessRequestStatus],
        limit: int = 100
    ) -> AccessRequestsResponse:
        requests = await self.rep_access.get_for_wishlist_owner_with_details(
            owner_id=user_id,
            status=status,
            limit=limit
        )
        request_list = []
        for req in requests:
            request_list.append(await self.format_request_response(req))
        total = len(request_list)
        return AccessRequestsResponse(
            requests=request_list,
            total=total
        )

    async def check_access(
        self,
        wishlist_id: int,
        user_id: int
    ) -> bool:
        wishlist = await self.rep_wishlist.get(wishlist_id)
        if wishlist and wishlist.user_id == user_id:
            return True
        if wishlist.typeprivacy == TypePrivacyEnum.public:
            return True
        if wishlist.typeprivacy == TypePrivacyEnum.private:
            return False
        return await self.rep_access.has_access(
            wishlist_id,
            user_id
        )

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

        wishlist_id = access_request.wishlist_id
        requester_id = access_request.requester_id

        wishlist = await self.rep_wishlist.get(wishlist_id)
        requester = await self.rep_user.get_user_by_id(requester_id)

        owner_id = wishlist.user_id if wishlist else None
        owner = await self.rep_user.get_user_by_id(owner_id) if owner_id else None

        return AccessRequestWithDetails(
            id=access_request.id,
            wishlist_id=wishlist_id,
            requester_id=requester_id,
            status=access_request.status,
            created_at=access_request.created_at,
            processed_at=access_request.processed_at,
            wishlist_name=wishlist.name if wishlist else None,
            wishlist_photo=wishlist.photo if wishlist else None,
            requester_name=requester.name if requester else None,
            requester_photo=requester.photo if requester else None,
            owner_id=owner_id,
            owner_name=owner.name if owner else None
        )

    async def can_view_request(
        self,
        access_request,
        user_id: int
    ) -> bool:
        if access_request.requester_id == user_id:
            return True

        wishlist = await self.rep_wishlist.get(access_request.wishlist_id)

        if wishlist and wishlist.user_id == user_id:
            return True

        return False
