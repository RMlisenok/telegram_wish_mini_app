from typing import Optional, List
from sqlalchemy.ext.asyncio import AsyncSession

from app.services.subscription_service import SubscriptionService
from app.repositories.user_repository import UserRepository
from app.repositories.block_repository import BlockRepository
from app.repositories.wishlist_repository import WishlistRepository
from app.repositories.subscription_repository import SubscriptionRepository
from app.repositories.wish_repository import WishRepository
from app.models.user import User
from app.schemas.user import UserCreate, UserResponse, UserUpdate, UserResponesForMainScreen
from app.schemas.block import BlockResponse
from app.schemas.wishlist import WishlistShort, WishlistResponse
from app.schemas.subscription import SubscriptionsResponse, SubscribersResponse

import logging
logger = logging.getLogger(__name__)


class UserService:
    def __init__(self, session: AsyncSession):
        self.rep_user = UserRepository(session)
        self.rep_block = BlockRepository(session)
        self.rep_wishlist = WishlistRepository(session)
        self.rep_wish = WishRepository(session)
        self.rep_subs = SubscriptionRepository(session)
        self.serv_subs = SubscriptionService(session)

    async def get_user(self, user_id: int) -> Optional[UserResponse]:
        user = await self.rep_user.get_user_by_id(user_id)
        if not user:
            return None
        return UserResponse.model_validate(user)

    async def get_user_for_main_screen(
        self,
        user_id: int
    ) -> Optional[UserResponesForMainScreen]:
        user = await self.rep_user.get_user_by_id(user_id)
        if not user:
            return None
        logger.warning(f'\nINFO|           : {user}\n')
        wishlist = await self.rep_wishlist.get_user_wishlist_short(
            user_id=user_id,
            is_desc=True,
            limit=3
        )
        wish_short = []
        for wish in wishlist:
            wish_data = WishlistResponse.model_validate(wish)
            wish_short.append(wish_data)
        logger.warning(f'\nINFO|           WISH: {wish_short}]\n')
        total_wish = await self.rep_wish.get_count_user_wish(user_id)
        total_wishlist = await self.rep_wishlist.get_count_user_wishlist(user_id)
        logger.warning(f'\nINFO|          wish_:{total_wish} | wishlsit_: {total_wishlist}\n')

        subscribers = await self.rep_subs.get_user_subscribers(user_id, True, 2)
        total_subscribers = await self.rep_subs.count_user_subscribers(user_id)

        subscribers_list = []
        for user_sub in subscribers:
            subscribers_list.append({
                "name": user_sub.name,
                "photo": user_sub.photo,
                "birth_date": user_sub.birth_date
            })
        my_subscribers = SubscribersResponse(
            subscribers=subscribers_list,
            total=total_subscribers
        )
        subscription = await self.serv_subs.get_my_subscription(user_id, 2)
        subscr = {"subscription": subscription.model_dump()}
        logger.warning(f"\nDEBUG subscription type: {type(subscription)}\n")
        logger.warning(f"\nDEBUG subscription value: {subscription}\n")

        return UserResponesForMainScreen(
            telegram_id=user.telegram_id,
            name=user.name,
            birth_date=user.birth_date,
            photo=user.photo,
            theme=user.theme,
            text_size=user.text_size,
            show_sub=user.show_sub,
            total_wish=total_wish,
            total_wishlist=total_wishlist,
            wishlist_last_update=wish_short,
            subscription=subscr,
            subsсribers=my_subscribers
        )

    async def get_user_by_telegram_id(
        self,
        telegram_id: int
    ) -> Optional[UserResponse]:
        user = await self.rep_user.get_user_by_tg_id(telegram_id)
        if not user:
            return None
        return UserResponse.model_validate(user)

    async def get_all_users(
        self,
        limit: int = 10
    ) -> List[UserResponse]:
        users = await self.rep_user.get_all_users(limit)
        return [UserResponse.model_validate(user) for user in users]

    async def create_user(self, user_data: UserCreate) -> UserResponse:
        user = await self.rep_user.create(user_data)
        return UserResponse.model_validate(user)

    async def update_user(
        self,
        user_id: int,
        user_data: UserUpdate
    ) -> Optional[UserResponse]:
        user = await self.rep_user.update(user_id, user_data)
        if user:
            return UserResponse.model_validate(user)
        return None

    async def block_user(
        self,
        blocker_id: int,
        blocked_id: int,
    ) -> Optional[BlockResponse]:
        block = await self.rep_block.block_user(blocker_id, blocked_id)
        if block:
            return BlockResponse.model_validate(block)
        return None

    async def unblock_user(
        self,
        blocker_id: int,
        blocked_id: int,
    ) -> bool:
        return await self.rep_block.unblock_user(blocker_id, blocked_id)

    async def check_block_status(
        self,
        blocker_id: int,
        blocked_id: int,
    ) -> bool:
        return await self.rep_block.is_user_blocked(blocker_id, blocked_id)

    async def get_user_block(
        self,
        blocker_id: int
    ) -> List[UserResponse]:
        users = await self.rep_block.get_user_block(blocker_id)
        return [UserResponse.model_validate(user) for user in users]
