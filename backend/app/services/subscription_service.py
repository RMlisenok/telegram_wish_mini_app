from typing import Optional, List, Tuple
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.subscription import Subscription
from app.repositories.subscription_repository import SubscriptionRepository
from app.repositories.user_repository import UserRepository
from app.repositories.wishlist_repository import WishlistRepository
from app.schemas.subscription import (
    SubscribeToWishlistRequest,
    SubscribeToUserRequest,
    SubscriptionsResponse
    )


class SubscriptionService:
    def __init__(
        self,
        session: AsyncSession
    ):
        self.session = session
        self.rep_subs = SubscriptionRepository(session)
        self.rep_user = UserRepository(session)
        self.rep_wishlist = WishlistRepository(session)

    async def subscribe_to_user(
        self,
        user_id: int,
        target_user_id: int
    ) -> bool:
        if user_id == target_user_id:
            return False
        target_user = await self.rep_user.get_user_by_id(target_user_id)
        if not target_user:
            return False
        
        existing = await self.rep_subs.get_subscription(
            subscriber_id=user_id,
            type_sub=True,
            target_user_id=target_user_id
        )
        if existing:
            return False
        
        subscription_data = {
            "subscriber_id": user_id,
            "type_sub": True,
            "target_user_id": target_user_id
        }
        subscription = await self.rep_subs.create(subscription_data)
        return subscription is not None

    async def subscribe_to_wishlist(
        self,
        user_id: int,
        target_wishlist_id: int
    ) -> bool:
        wishlist = await self.rep_wishlist.get(target_wishlist_id)
        if not wishlist:
            return False

        if wishlist.user_id == user_id:
            return False
        
        existing = await self.rep_subs.get_subscription(
            subscriber_id=user_id,
            type_sub=False,
            target_wishlist_id=target_wishlist_id
        )
        if existing:
            return False
        
        subscription_data = {
            "subscriber_id": user_id,
            "type_sub": False,
            "target_wishlist_id": target_wishlist_id
        }
        subscription = await self.rep_subs.create(subscription_data)
        return subscription is not None

    async def unsubscribe_from_user(
        self,
        user_id: int,
        target_user_id: int
    ) -> bool:
        return await self.rep_subs.delete_by_target(
            subscriber_id=user_id,
            type_sub=True,
            target_user_id=target_user_id
        )

    async def unsubscribe_from_wishlist(
        self,
        user_id: int,
        target_wishlist_id: int
    ) -> bool:
        return await self.rep_subs.delete_by_target(
            subscriber_id=user_id,
            type_sub=False,
            target_user_id=target_wishlist_id
        )

    async def get_my_subscription(
        self,
        user_id: int,
        limit: int = 100
    ) -> SubscriptionsResponse:
        subscriptions = await self.rep_subs.get_user_subscription(
            subscriber_id=user_id,
            limit=limit
        )
        total = await self.rep_subs.count_user_subscriptions(
            subscriber_id=user_id
        )
        subscription_list = []
        for sub in subscriptions:
            if sub.type_sub:
                subscription_list.append({
                    "type": "user",
                    "id": sub.target_user.id,
                    "name": sub.target_user.name,
                    "photo": sub.target_user.photo,
                    "user_id": sub.target_user.id
                })
            else:
                if sub.target_wishlist:
                    subscription_list.append({
                        "type": "wishlist",
                        "id": sub.target_wishlist.id,
                        "name": sub.target_wishlist.name,
                        "description": sub.target_wishlist.description,
                        "photo": sub.target_wishlist.photo,
                        "type_privacy": sub.target_wishlist.typeprivacy.value,
                    })
        return SubscriptionsResponse(
            subscriptions=subscription_list,
            total=total
        )

    async def get_my_user_subscriptions(
        self,
        user_id: int,
        limit: int = 100
    ) -> SubscriptionsResponse:
        subscriptions = await self.rep_subs.get_user_subscription(
            subscriber_id=user_id,
            limit=limit,
            only_users=True
        )
        total = await self.rep_subs.count_user_subscriptions(
            subscriber_id=user_id,
            only_users=True
        )
        subscription_list = []
        for sub in subscriptions:
            if sub.type_sub:
                subscription_list.append({
                    "type": "user",
                    "id": sub.target_user.id,
                    "name": sub.target_user.name,
                    "photo": sub.target_user.photo,
                    "user_id": sub.target_user.id
                })
        return SubscriptionsResponse(
            subscriptions=subscription_list,
            total=total
        )

    async def get_my_wishlist_subscriptions(
        self,
        user_id: int,
        limit: int = 100
    ) -> SubscriptionsResponse:
        subscriptions = await self.rep_subs.get_user_subscription(
            subscriber_id=user_id,
            limit=limit,
            only_wishlists=True
        )
        total = await self.rep_subs.count_user_subscriptions(
            subscriber_id=user_id,
            only_wishlists=True
        )
        subscription_list = []
        for sub in subscriptions:
            if sub.target_wishlist:
                subscription_list.append({
                    "type": "wishlist",
                    "id": sub.target_wishlist.id,
                    "name": sub.target_wishlist.name,
                    "description": sub.target_wishlist.description,
                    "photo": sub.target_wishlist.photo,
                    "type_privacy": sub.target_wishlist.typeprivacy.value,
                })
        return SubscriptionsResponse(
            subscriptions=subscription_list,
            total=total
        )

    async def get_user_subscriptions(
        self,
        user_id: int,
        current_user_id: Optional[int] = None,
        limit: int = 100
    ) -> SubscriptionsResponse:
        user = await self.rep_user.get_user_by_id(user_id=user_id)
        if not user:
            raise ValueError("User not found")
        if current_user_id != user_id and not user.show_sub:
            raise ValueError("User's subscriptions are private")
        subscriptions = await self.rep_subs.get_user_subscription(
            subscriber_id=user_id,
            limit=limit
        )
        total = await self.rep_subs.count_user_subscriptions(
            subscriber_id=user_id
        )
        subscription_list = []
        for sub in subscriptions:
            if sub.type_sub:
                subscription_list.append({
                    "type": "user",
                    "id": sub.target_user.id,
                    "name": sub.target_user.name,
                    "photo": sub.target_user.photo,
                    "user_id": sub.target_user.id
                })
            else:
                if sub.target_wishlist:
                    subscription_list.append({
                        "type": "wishlist",
                        "id": sub.target_wishlist.id,
                        "name": sub.target_wishlist.name,
                        "description": sub.target_wishlist.description,
                        "photo": sub.target_wishlist.photo,
                        "type_privacy": sub.target_wishlist.typeprivacy.value,
                    })
        return SubscriptionsResponse(
            subscriptions=subscription_list,
            total=total
        )

    async def check_user_subscription(
        self,
        user_id: int,
        target_user_id: int
    ) -> bool:
        subscription = await self.rep_subs.get_subscription(
            subscriber_id=user_id,
            type_sub=True,
            target_user_id=target_user_id
        )
        return subscription is not None

    async def check_wishlist_subscription(
        self,
        user_id: int,
        target_wishlist_id: int
    ) -> bool:
        subscription = await self.rep_subs.get_subscription(
            subscriber_id=user_id,
            type_sub=False,
            target_wishlist_id=target_wishlist_id
        )
        return subscription is not None
