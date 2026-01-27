from typing import Optional, List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, func, desc, asc, update
from sqlalchemy.orm import joinedload

from app.models.subscription import Subscription
from app.models.user import User
from app.models.wishlist import Wishlist
from app.schemas.subscription import SubscribersVisitUpdate

class SubscriptionRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(
        self,
        subscription_data: dict,
    ) -> Optional[Subscription]:
        try:
            subscription = Subscription(**subscription_data)
            self.session.add(subscription)
            await self.session.commit()
            await self.session.refresh(subscription)
            return subscription
        except Exception:
            self.session.rollback()
            return None

    async def get_subscription(
        self,
        subscriber_id: int,
        type_sub: bool,
        target_user_id: Optional[int] = None,
        target_wishlist_id: Optional[int] = None
    ) -> Optional[Subscription]:
        conditions = [
            Subscription.subscriber_id == subscriber_id,
            Subscription.type_sub == type_sub
        ]
        if type_sub:
            if target_user_id is None:
                return None
            conditions.append(Subscription.target_user_id == target_user_id)
        else:
            if target_wishlist_id is None:
                return None
            conditions.append(Subscription.target_wishlist_id == target_wishlist_id)
        query = select(Subscription).where(and_(*conditions))
        result = await self.session.execute(query)
        return result.scalar_one_or_none()

    async def delete_by_target(
        self,
        subscriber_id: int,
        type_sub: bool,
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
            await self.session.delete(subscription)
            return True
        except Exception as e:
            print(F"Error deleting subscription: {str(e)}")
            return False

    async def get_user_subscription(
        self,
        subscriber_id: int,
        limit: int = 100,
        is_desc: bool = False,
        only_users: bool = False,
        only_wishlists: bool = False,
    ) -> List[Subscription]:
        query = (
            select(Subscription)
            .where(Subscription.subscriber_id == subscriber_id)
        )

        if only_users:
            query = query.where(Subscription.type_sub == True)
        elif only_wishlists:
            query = query.where(Subscription.type_sub == False)
        query = query.options(
            joinedload(Subscription.target_user),
            joinedload(Subscription.target_wishlist),
            joinedload(Subscription.target_wishlist).joinedload(Wishlist.owner)
        )
        if is_desc:
            query = query.order_by(desc(Subscription.updated_at))
        else:
            query = query.order_by(asc(Subscription.updated_at))
        query = query.limit(limit)
        result = await self.session.execute(query)
        return list(result.scalars().all())

    async def get_user_subscribers(
        self,
        user_id,
        is_desc: bool,
        limit: int = 100
    ) -> List[User]:
        query = (
            select(User)
            .join(
                Subscription,
                User.id == Subscription.subscriber_id
            )
            .where(
                and_(
                    Subscription.target_user_id == user_id,
                    Subscription.type_sub == True
                )
            )
        )
        if is_desc:
            query = query.order_by(desc(Subscription.created_at))
        else:
            query = query.order_by(asc(Subscription.created_at))
        query = query.limit(limit)
        result = await self.session.execute(query)
        return list(result.scalars().all())

    async def update(
        self,
        subscribe_id: int
    ) -> Optional[SubscribersVisitUpdate]:
        query = (
            update(Subscription)
            .where(Subscription.id == subscribe_id)
            .values(
                updated_at=func.now()
            )
            .returning(Subscription.updated_at)
        )
        
        result = await self.session.execute(query)
        await self.session.commit()
        
        updated_time = result.scalar_one_or_none()
        
        if updated_time:
            return SubscribersVisitUpdate(
                status=True,
                updated_at=updated_time
            )
        return None

    async def count_user_subscribers(
        self,
        user_id: int
    ) -> int:
        query = (
            select(func.count())
            .select_from(Subscription)
            .where(
                and_(
                    Subscription.target_user_id == user_id,
                    Subscription.type_sub == True
                )
            ))
        result = await self.session.execute(query)
        return result.scalar()

    async def count_user_subscriptions(
        self,
        subscriber_id: int,
        only_users: bool = False,
        only_wishlists: bool = False
    ) -> int:
        conditions = [Subscription.subscriber_id == subscriber_id]

        if only_users:
            conditions.append(Subscription.type_sub == True)
        elif only_wishlists:
            conditions.append(Subscription.type_sub == False)

        query = select(func.count()).where(and_(*conditions))
        result = await self.session.execute(query)
        return result.scalar_one()

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

    async def get_subscribe_id(
        self,
        subscribe_id: int
    ) -> Optional[Subscription]:
        query = select().where(Subscription.id == subscribe_id)
        result = await self.session.execute(query)
        return result.scalar_one_or_none()
