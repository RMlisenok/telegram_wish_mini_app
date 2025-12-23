from sqlalchemy import select, delete
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.questionnaire import UserForm, TagForm

class QuestionnaireRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_tags_by_type(self, is_interest: bool):
        query = select(TagForm).where(TagForm.type_tags == is_interest)
        result = await self.session.execute(query)
        return result.scalars().all()

    async def save_user_forms(self, user_id: int, items: list[UserForm]):
        # Сначала очищаем старую анкету, затем пишем новую
        await self.session.execute(delete(UserForm).where(UserForm.user_id == user_id))
        self.session.add_all(items)
        await self.session.commit()