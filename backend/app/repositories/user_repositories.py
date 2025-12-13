from typing import Optional, List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update
from sqlalchemy.orm import selectinload

from app.models.user import User


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
