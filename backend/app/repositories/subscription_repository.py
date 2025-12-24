from typing import Optional, List, 
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, func, Tuple
from sqlalchemy.orm import joinedload

from app.models.subscription import Subscription
from app.models.user import User
from app.models.wishlist import Wishlist
from app.schemas.subscription import SubscriptionCreate


class SubscriptionRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(
        self,
        subscription_data: SubscriptionCreate,
    ) -> Optional[Subscription]:
        if subscription_data.type_sub:
                existing = await self.get_subscription(
                subscriber_id=subscription_data.subscriber_id,
                type_sub=subscription_data.type_sub,
                target_user_id=subscription_data.target_user_id,
            )
        else:
                existing = await self.get_subscription(
                subscriber_id=subscription_data.subscriber_id,
                type_sub=subscription_data.type_sub,
                target_wishlist_id=subscription_data.target_wishlist_id,
            )

        if existing:
            return existing
        try:
            subscription = Subscription(**subscription_data.model_dump())
            self.session.add(subscription)
            await self.session.commit()
            await self.session.refresh(subscription)
            return subscription
        except Exception as e:
            self.session.rollback()
            return None

    async def delete_for_subscription_id(
        self,
        subscription_id: int
    ) -> bool:
        try:
            query = (
                select(Subscription)
                .where(Subscription.id == subscription_id)
            )
            subscription = await self.session.execute(query)
            if not subscription:
                return False
            await self.session.delete(subscription)
            return True
        except Exception as e:
            pass

    async def delete_by_target(
        self,
        subscriber_id: int,
        type_sub: bool = True,
        target_user_id: Optional[int] = None,
        target_wishlist_id: Optional[int] = None
    ) -> bool:
        try:
            subscription = await self.get_subscription(
                subscriber_id=subscriber_id,
                type_sub=type_sub,
                target_user_id=target_user_id,
                target_wishlist_id=target_wishlist_id
            )
            if not subscription:
                return False
            await self.session.delet(subscription)
            return True
        except Exception as e:
            print(F"Error deleting subscription: {str(e)}")
            return False

    async def get_subscription(
        self,
        subscriber_id: int,
        type_sub: bool = True,
        target_user_id: Optional[int] = None,
        target_wishlist_id: Optional[int] = None
    ) -> Optional[Subscription]:
        conditions = [
            Subscription.subscriber_id == subscriber_id,
            Subscription.type_sub == type_sub
        ]
        if type_sub:
            conditions.append(Subscription.target_user_id == target_user_id)
        else:
            conditions.append(Subscription.target_wishlist_id == target_wishlist_id)
        query = select(Subscription).where(and_(*conditions))
        result = await self.session.execute(query)
        return result.scalar_one_or_none()

    async def get_user_subscription(
        self,
        subscriber_id: int,
        limit: int = 100
    ) -> Tuple[List[Subscription], int]:
        query = (
            select(Subscription)
            .where(Subscription.subscriber_id == subscriber_id)
            .options(
                joinedload(Subscription.target_user),
                joinedload(Subscription.target_wishlist)
            )
            .order_by(Subscription.created_at.desc())
        )
        count_query = (
            select(func.count())
            .where(Subscription.subscriber_id == subscriber_id)
        )
        count_result = await self.session.execute(count_query)
        total = count_result.scalar_one_or_none()
        
        
        query = query.limit(limit)
        result = await self.session.execute(query)
        subscriptions = list(result.scalars().all())

        return subscriptions, total

    async def get_user_subscribers(
        self,
        target_user_id: int,
        limit: int = 100
    ) -> Tuple[List[Subscription], int]:
        query = (
            select(Subscription)
            .where(
                and_(
                    Subscription.type_sub == True,
                    Subscription.target_user_id == target_user_id
                )
            )
            .options(
                joinedload(Subscription.subscriber)
            )
            .order_by(Subscription.created_at.desc())
        )

        count_query = (
            select(func.count())
            .where(
                and_(
                    Subscription.type_sub == True,
                    Subscription.target_user_id == target_user_id
                )
            )
        )

        count_result = await self.session.execute(count_query)
        total = count_result.scalar_one_or_none()

        query = query.limit(limit)
        result = await self.session.execute(query)
        subscriptions = list(result.scalars().all())

        return subscriptions, total

    async def get_wishlist_subscribers(
        self,
        wishlist_id: int,
        limit: int = 100
    ) -> Tuple[List[Subscription], int]:
        
        query = (
            select(Subscription)
            .where(
                and_(
                    Subscription.type_sub == False,
                    Subscription.target_wishlist_id == wishlist_id
                )
            )
            .options(
                joinedload(Subscription.subscriber)
            )
            .order_by(Subscription.created_at.desc())
        )

        count_query = (
            select(func.count())
            .where(
                and_(
                    Subscription.type_sub == False,
                    Subscription.target_wishlist_id == wishlist_id
                )
            )
        )

        count_result = await self.session.execute(count_query)
        total = count_result.scalar_one_or_none()

        query = query.limit(limit)
        result = await self.session.execute(query)
        subscriptions = list(result.scalars().all())

        return subscriptions, total

    async def is_subscribed(
        self,
        subscriber_id: int,
        type_sub= bool,
        target_user_id: Optional[int] = None,
        target_wishlist_id: Optional[int] = None
    ) -> bool:
        subscription = await self.get_subscription(
            subscriber_id=subscriber_id,
            type_sub=type_sub,
            target_user_id=target_user_id,
            target_wishlist_id=target_wishlist_id
        )
        return subscription is not None
