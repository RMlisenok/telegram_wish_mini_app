from typing import Optional, List, Tuple
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.subscription import Subscription
from app.repositories.subscription_repository import SubscriptionRepository
from app.repositories.user_repository import UserRepository
from app.repositories.wishlist_repository import WishlistRepository
from app.repositories.wish_wishlist_repository import WishWishlistRepository
from app.schemas.subscription import (
    SubscribeToWishlistRequest,
    SubscribeToUserRequest,
    SubscribersVisitUpdate,
    SubscriptionsResponse,
    SubscribersResponse
)
from app.services.notification_service_bot import NotificationService
from app.core.bot_setup import bot


class SubscriptionService:
    def __init__(
            self,
            session: AsyncSession
    ):
        self.session = session
        self.rep_subs = SubscriptionRepository(session)
        self.rep_user = UserRepository(session)
        self.rep_wishlist = WishlistRepository(session)
        self.rep_wish_wishlist = WishWishlistRepository(session)

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

        if subscription:
            try:
                from app.services.notification_service_bot import NotificationService
                from app.core.bot_setup import bot

                notif_service = NotificationService(bot)
                await notif_service.notify_new_follower(self.session, user_id, target_user_id)
            except Exception as e:
                print(f"Ошибка отправки уведомления о подписке: {e}")
        return subscription is not None

    # async def subscribe_to_user(
    #     self,
    #     user_id: int,
    #     target_user_id: int
    # ) -> bool:
    #     if user_id == target_user_id:
    #         return False
    #     target_user = await self.rep_user.get_user_by_id(target_user_id)
    #     if not target_user:
    #         return False
    #
    #     existing = await self.rep_subs.get_subscription(
    #         subscriber_id=user_id,
    #         type_sub=True,
    #         target_user_id=target_user_id
    #     )
    #     if existing:
    #         return False
    #
    #     subscription_data = {
    #         "subscriber_id": user_id,
    #         "type_sub": True,
    #         "target_user_id": target_user_id
    #     }
    #     subscription = await self.rep_subs.create(subscription_data)
    #     return subscription is not None

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

    async def update_visit(
            self,
            user_id: int,
            subscribe_id: int
    ) -> SubscribersVisitUpdate:
        update = await self.rep_subs.update(subscribe_id)
        if update:
            return SubscribersVisitUpdate.model_validate(update)
        return None

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
            is_desc: bool = False,
            limit: int = 100
    ) -> SubscriptionsResponse:
        subscriptions = await self.rep_subs.get_user_subscription(
            subscriber_id=user_id,
            is_desc=is_desc,
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
                    "sub_id": sub.id,
                    "name": sub.target_user.name,
                    "birth_date": sub.target_user.birth_date,
                    "photo": sub.target_user.photo,
                    "user_id": sub.target_user.id,
                    "created_at": sub.created_at,
                    "updated_at": sub.updated_at
                })
            else:
                if sub.target_wishlist:
                    count_wishes = await self.rep_wish_wishlist.count_wishes_in_wishlist(
                        sub.target_wishlist_id
                    )
                    subscription_list.append({
                        "type": "wishlist",
                        "sub_id": sub.id,
                        "wishlist_id": sub.target_wishlist.id,
                        "name": sub.target_wishlist.name,
                        "description": sub.target_wishlist.description,
                        "photo": sub.target_wishlist.photo,
                        "type_privacy": sub.target_wishlist.typeprivacy.value,
                        "created_at": sub.created_at,
                        "updated_at": sub.updated_at,
                        "total_wishes": count_wishes,
                        "owner_id": sub.target_wishlist.user_id,
                        "owner_name": sub.target_wishlist.owner.name
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
                    "sub_id": sub.id,
                    "name": sub.target_user.name,
                    "birth_date": sub.target_user.birth_date,
                    "photo": sub.target_user.photo,
                    "user_id": sub.target_user.id,
                    "created_at": sub.created_at,
                    "updated_at": sub.updated_at
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
                count_wishes = await self.rep_wish_wishlist.count_wishes_in_wishlist(
                    sub.target_wishlist_id
                )
                subscription_list.append({
                    "type": "wishlist",
                    "sub_id": sub.id,
                    "wishlist_id": sub.target_wishlist.id,
                    "name": sub.target_wishlist.name,
                    "description": sub.target_wishlist.description,
                    "photo": sub.target_wishlist.photo,
                    "type_privacy": sub.target_wishlist.typeprivacy.value,
                    "created_at": sub.created_at,
                    "updated_at": sub.updated_at,
                    "total_wishes": count_wishes,
                    "owner_id": sub.target_wishlist.user_id,
                    "owner_name": sub.target_wishlist.owner.name
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
                    "sub_id": sub.id,
                    "name": sub.target_user.name,
                    "birth_date": sub.target_user.birth_date,
                    "photo": sub.target_user.photo,
                    "user_id": sub.target_user.id,
                    "created_at": sub.created_at,
                    "updated_at": sub.updated_at
                })
            else:
                if sub.target_wishlist:
                    count_wishes = await self.rep_wish_wishlist.count_wishes_in_wishlist(
                        sub.target_wishlist_id
                    )
                    subscription_list.append({
                        "type": "wishlist",
                        "sub_id": sub.id,
                        "wishlist_id": sub.target_wishlist.id,
                        "name": sub.target_wishlist.name,
                        "description": sub.target_wishlist.description,
                        "photo": sub.target_wishlist.photo,
                        "type_privacy": sub.target_wishlist.typeprivacy.value,
                        "created_at": sub.created_at,
                        "updated_at": sub.updated_at,
                        "total_wishes": count_wishes,
                        "owner_id": sub.target_wishlist.user_id,
                        "owner_name": sub.target_wishlist.owner.name
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

    async def get_user_subscribers(
            self,
            user_id: int,
            is_desc: bool = True,
            limit: int = 100
    ):
        subscribers = await self.rep_subs.get_user_subscribers(
            user_id,
            is_desc,
            limit
        )
        subscribers_list = []
        for sub in subscribers:
            # if sub.type_sub:
            subscribers_list.append({
                "type": "user",
                "sub_id": sub.id,
                "name": sub.subscriber.name,
                "birth_date": sub.subscriber.birth_date,
                "photo": sub.subscriber.photo,
                "user_id": sub.subscriber.id,
                "created_at": sub.created_at,
                "updated_at": sub.updated_at
            })

        return SubscribersResponse(
            subscribers=subscribers_list,
            total=len(subscribers_list)
        )
