from repositories.questionnaire_repository import QuestionnaireRepository
from models.questionnaire import UserForm
from sqlalchemy.ext.asyncio import AsyncSession

from telegram_wish_mini_app.backend.app.schemas.questionnaire import QuestionnaireCreate


class QuestionnaireService:
    def __init__(self, session: AsyncSession):
        self.repo = QuestionnaireRepository(session)

    async def update_questionnaire(self, user_id: int, data: QuestionnaireCreate):
        new_items = []
        for item in data.interests:
            new_items.append(UserForm(user_id=user_id, tag_id=item.tag_id, detail=item.detail))
        for item in data.avoid_gifts:
            new_items.append(UserForm(user_id=user_id, tag_id=item.tag_id, detail=item.detail))

        await self.repo.save_user_forms(user_id, new_items)
        return {"success": True, "message": "Анкета сохранена"}