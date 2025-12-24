from typing import Optional, List, Tuple
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.subscription import Subscription
from app.repositories.subscription_repository import SubscriptionRepository
from app.repositories.user_repository import UserRepository
from app.repositories.wishlist_repository import WishlistRepository
from app.schemas.subscription import (
    SubscriptionCreate,
    SubscriptionResponse,
    SubscriptionWithDetailsResponse,
    SubscriptionStatusResponse
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

    async def subscribe(
        self,
        subscriber_id: int,
        subscription_data: SubscriptionCreate
    ) -> Optional[SubscriptionResponse]:
        subscription_data.subscriber_id = subscriber_id

        if subscription_data.type_sub:
            if subscription_data.target_user_id == subscriber_id:
                raise ValueError("User connot subscribe yourself")
            target_user = await self.rep_user.get_user_by_id(subscription_data.target_user_id)
            if not target_user:
                raise ValueError("User not found")
        else:
            target_wishlist = await self.rep_wishlist.get(subscription_data.target_wishlist_id)
            if not target_wishlist:
                raise ValueError("Wishlist not found")
            if target_wishlist.user_id == subscriber_id:
                raise ValueError("User cannot subscribe your wishlit")

        existing = await self.rep_subs.get_subscription(
            subscriber_id=subscription_data.subscriber_id,
            type_sub=subscription_data.type_sub,
            target_user_id=subscription_data.target_user_id,
            target_wishlist_id=subscription_data.target_wishlist_id
        )
        if existing:
            raise ValueError("Subscription already exists")
        subscription = self.rep_subs.create(subscription_data)
        if subscription:
            return SubscriptionResponse.model_validate(subscription)
        return None

    async def unsubscribe_by_id(
        self,
        subscribe_id: int,
        user_id: int
    ) -> bool:
        subscription = await self.rep_subs.get_subscribe_id(subscribe_id)
        if not subscription:
            return False
        if subscription.subscriber_id != user_id:
            raise ValueError("Not authorized to delete this subscription")
        return await self.rep_subs.delete_for_subscription_id(subscribe_id)    

    async def unsubscribe_by_target(
        self,
        subscriber_id: int,
        type_sub: bool,
        target_user_id: Optional[int] = None,
        target_wishlist_id: Optional[int] = None
    ) -> bool:
        if subscriber_id is None:
            raise ValueError("subscriber_id is required")
        if type_sub and not target_user_id:
            raise ValueError("target_user_id is required for user subscription")
        if not type_sub and not target_wishlist_id:
            raise ValueError("target_wishlist_id is required for wishlist subscription")
        existing = await self.rep_subs.get_subscription(
            subscriber_id=subscriber_id,
            type_sub=type_sub,
            target_user_id=target_user_id,
            target_wishlist_id=target_wishlist_id
        )
        if not existing:
            raise ValueError("Subscription not found")
        return await self.rep_subs.delete_by_target(
            subscriber_id=subscriber_id,
            type_sub=type_sub,
            target_user_id=target_user_id,
            target_wishlist_id=target_wishlist_id
        )

    async def get_subsription(
        self,
        user_id: int,
        subscription_id: int,
    ) -> Optional[SubscriptionWithDetailsResponse]:
        subscription = await self.rep_subs.get_subscribe_id(subscription_id)
        if not subscription:
            raise ValueError("Subscription not found")
        if user_id == subscription.subscriber_id:
            raise ValueError("Not authorized to view this subscription")
        return self.get_subscription_data(subscription)

    async def get_user_sibscriptions(
        self,
        subscriber_id: int,
        limit: int = 100,
        require_ownership: bool = True
        # user_id: int - Если делать проверку внутри
    ) -> Tuple[List[SubscriptionWithDetailsResponse], int]:
        if not require_ownership:
            raise ValueError("Not acces")
        # можно сюда добавить проверку на разрешения или уже на фронте
        subscriptions, total = await self.rep_subs.get_user_subscribers(
            subscriber_id,
            limit
        )
        result = [self.get_subscription_data(sub) for sub in subscriptions]
        return result, total
    
    
    async def get_my_sibscriptions(
        self,
        subscriber_id: int, # Добавить Dependencies
        limit: int = 100,
    ) -> Tuple[List[SubscriptionWithDetailsResponse], int]:
        
        subscriptions, total = await self.rep_subs.get_user_subscribers(
            subscriber_id,
            limit
        )
        result = [self.get_subscription_data(sub) for sub in subscriptions]
        return result, total

    # не знаю насколько нужно для пользователей, но пускай будет
    async def get_user_subscribers(
        self,
        target_user_id: int,
        limit: int = 100,
        require_ownership: bool = True
        # user_id: int Если делать проверку внутри
    ) -> Tuple[List[SubscriptionWithDetailsResponse], int]:
        if require_ownership:
            raise ValueError("Not acces")
        subscriptions, total = await self.rep_subs.get_user_subscribers(
            target_user_id,
            limit
        )
        result = [self.get_subscription_data(sub) for sub in subscriptions]
        return result, total

    async def get_my_subscribers(
        self,
        target_user_id: int,  # Dependencies
        limit: int = 100,
    ) -> Tuple[List[SubscriptionWithDetailsResponse], int]:
        subscriptions, total = await self.rep_subs.get_user_subscribers(
            target_user_id,
            limit
        )
        result = [self.get_subscription_data(sub) for sub in subscriptions]
        return result, total

    def get_subscription_data(
        self,
        subscription: Subscription,
    ) -> SubscriptionWithDetailsResponse:
        data = SubscriptionWithDetailsResponse.model_validate(subscription)
        if subscription.subscriber:
            data.subscriber_name = subscription.subscriber.name

        if subscription.type_sub and subscription.target_user:
            data.target_user_name = subscription.target_user.name
        elif not subscription.type_sub and subscription.target_wishlist:
            data.target_wishlist_title = subscription.target_wishlist.name
        return data
