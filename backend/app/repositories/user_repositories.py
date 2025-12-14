from typing import Optional, List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update
from sqlalchemy.orm import selectinload

from app.models.user import User
from app.schemas.user import UserCreate, UserUpdate


class UserRepositories:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_user_by_id(
        self,
        user_id: int,
        load_relationships: bool = False,
    ) -> Optional[User]:
        query = select(User).where(User.id == user_id)

        if load_relationships:
            query = query.options(
                selectinload(User.wishlists),
                selectinload(User.wishes),
                selectinload(User.subscriptions),
                selectinload(User.questionnaire),
                selectinload(User.notification_settings)
            )

        result = await self.session.execute(query)
        return result.scalar_one_or_none()

    async def get_user_by_tg_id(
        self,
        telegram_id: int,
        load_relationships: bool = False,
    ) -> Optional[User]:
        query = select(User).where(User.telegram_id == telegram_id)

        if load_relationships:
            query = query.options(
                selectinload(User.wishlists),
                selectinload(User.wishes),
                selectinload(User.subscriptions),
                selectinload(User.questionnaire),
                selectinload(User.notification_settings)
            )

        result = await self.session.execute(query)
        return result.scalar_one_or_none()

    async def create(
        self,
        user_data: UserCreate
    ) -> User:
        user = User(**user_data.model_dump())
        self.session.add(user)
        await self.session.commit()
        await self.session.refresh(user)
        return user

    async def update(
        self,
        user_id: int,
        user_data: UserUpdate
    ) -> Optional[User]:
        update_data = user_data.model_dump(exclude_unset=True)

        if not update_data:
            return await self.get_user_by_id(user_id)

        stmt = (
            update(User)
            .where(User.id == user_id)
            .values(**update_data)
            .returning(User)
        )

        result = await self.session.execute(stmt)
        await self.session.commit()

        user = result.scalar_one_or_none()

        if user:
            await self.session.refresh(user)
        return user
