from sqlalchemy import select, delete
from app.models.questionnaire import UserForm, TagForm
from app.schemas.questionnaire import QuestionnaireCreate
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.user import User

class QuestionnaireService:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def update_questionnaire(self, user_id: int, data: QuestionnaireCreate):
        stmt_user = select(User).where(User.telegram_id == user_id)
        user_result = await self.session.execute(stmt_user)
        user_obj = user_result.scalar_one_or_none()

        if not user_obj:

            user_obj = User(
                telegram_id=user_id,
                name=f"User_{user_id}"
            )
            self.session.add(user_obj)

            await self.session.flush()

        await self.session.execute(delete(UserForm).where(UserForm.user_id == user_id))

        new_items = []

        for item in data.interests:
            new_items.append(UserForm(
                user_id=user_id,
                tag=item.tag,
                detail=item.details,
                type_tag=1
            ))

        for item in data.avoid_gifts:
            new_items.append(UserForm(
                user_id=user_id,
                tag=item.tag,
                detail=item.details,
                type_tag=0
            ))

        if new_items:
            self.session.add_all(new_items)

        await self.session.commit()
        return {"success": True}

    async def get_user_questionnaire(self, user_id: int):
        stmt = select(UserForm).where(UserForm.user_id == user_id)
        result = await self.session.execute(stmt)
        rows = result.scalars().all()

        interests = []
        avoid_gifts = []

        for row in rows:
            item = {"tag": row.tag, "details": row.detail}
            if row.type_tag == 1:
                interests.append(item)
            else:
                avoid_gifts.append(item)

        return {"interests": interests, "avoid_gifts": avoid_gifts}