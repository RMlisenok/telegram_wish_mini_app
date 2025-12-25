from sqlalchemy import select, delete
from app.models.questionnaire import UserForm, TagForm
from app.schemas.questionnaire import QuestionnaireCreate


class QuestionnaireService:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def update_questionnaire(self, user_id: int, data: QuestionnaireCreate):
        await self.session.execute(delete(UserForm).where(UserForm.user_id == user_id))

        res = await self.session.execute(select(TagForm))
        tags_map = {t.tag_value.lower(): t.id for t in res.scalars().all()}

        new_items = []

        for item in data.interests:
            new_items.append(UserForm(
                user_id=user_id,
                tag=item.tag,
                tag_id=tags_map.get(item.tag.lower()),
                detail=item.details,
                is_interest=True
            ))

        # Обработка того, что не дарить
        for item in data.avoid_gifts:
            new_items.append(UserForm(
                user_id=user_id,
                tag=item.tag,
                tag_id=tags_map.get(item.tag.lower()),
                detail=item.details,
                is_interest=False
            ))

        self.session.add_all(new_items)
        await self.session.commit()
        return {"success": True}

    async def get_all_tags(self, is_interest: bool):
        query = select(TagForm).where(TagForm.type_tags == is_interest)
        result = await self.session.execute(query)
        return result.scalars().all()