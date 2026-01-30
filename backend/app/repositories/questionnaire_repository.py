from sqlalchemy import select, delete, and_
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.questionnaire import UserForm, TagForm
from typing import Optional, List, Dict, Any

class QuestionnaireRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_user_questinnaire(
        self,
        user_id: int
    ) -> Optional[List[UserForm]]:
        query = select(UserForm).where(UserForm.user_id == user_id)
        result = await self.session.execute(query)
        if not result:
            return None
        return result.scalars().all()

    async def get_standart_tags(
        self,
        user_id: int,
        is_interest: bool = True
    ) -> Optional[List[TagForm]]:
        query = select(TagForm).where(TagForm.type_tags == is_interest)
        result = await self.session.execute(query)
        return result.scalars().all()

    async def delete_user_questionnaire(self, user_id: int) -> None:
        await self.session.execute(
            delete(UserForm).where(UserForm.user_id == user_id)
        )

    async def create_questionnaire(
        self,
        user_id: int,
        interests: List[Dict[str, Any]], 
        avoid_gifts: List[Dict[str, Any]]
    ):
        new_items = []

        for item in interests:
            new_items.append(UserForm(
                user_id=user_id,
                tag=item["tag"],
                detail=item.get("details"),
                type_tag=1
            ))

        for item in avoid_gifts:
            new_items.append(UserForm(
                user_id=user_id,
                tag=item["tag"],
                detail=item.get("details"),
                type_tag=0
            ))

        if new_items:
            self.session.add_all(new_items)
            self.session.commit()

        return new_items

    async def get_tag(
        self,
        tag_value: str,
        is_interest: bool
    ):
        query = select(TagForm).where(
            and_(
                TagForm.tag_value == tag_value,
                TagForm.type_tags == is_interest
            )
        )
        result = await self.session.execute(query)
        return result.scalar_one_or_none()

    async def get_tag_user(
        self,
        user_id: int,
        tag_value: str,
        is_interest: bool
    ):
        query = select(UserForm).where(
            and_(
                UserForm.user_id == user_id,
                UserForm.tag == tag_value,
                UserForm.type_tag == is_interest
            )
        )
        result = await self.session.execute(query)
        return result.scalar_one_or_none()

    async def create_tag(
        self,
        user_id: int,
        tag_value: str,
        detail: str,
        is_interest: bool
    ) -> Optional[UserForm]:
        tag_add = UserForm(
            user_id=user_id,
            tag=tag_value,
            detail=detail,
            type_tag=is_interest
        )
        self.session.add(tag_add)
        await self.session.commit()
        await self.session.refresh(tag_add)
        return tag_add
