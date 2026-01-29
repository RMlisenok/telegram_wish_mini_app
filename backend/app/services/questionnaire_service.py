from sqlalchemy import select, delete
from app.models.questionnaire import UserForm, TagForm
from app.schemas.questionnaire import QuestionnaireCreate, TagCreate, TagForm
from app.repositories.questionnaire_repository import QuestionnaireRepository
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.user import User
from fastapi import APIRouter, Depends, HTTPException, status, logger


class QuestionnaireService:
    def __init__(self, session: AsyncSession):
        self.session = session
        self.rep_questin = QuestionnaireRepository(session)

    async def get_user_questionnaire(self, user_id: int):
        rows = await self.rep_questin.get_user_questinnaire(user_id)
        interests = []
        avoid_gifts = []

        for row in rows:
            item = {
                "id": row.id,
                "tag": row.tag,
                "details": row.detail
            }
            if row.type_tag == 1:
                interests.append(item)
            else:
                avoid_gifts.append(item)

        return {"interests": interests, "avoid_gifts": avoid_gifts}

    async def get_available(
        self,
        user_id: int,
        is_interest: bool = True
    ):
        tags = await self.rep_questin.get_standart_tags(user_id, is_interest)
        result = [{"tag_value": t.tag_value} for t in tags]
        return result

    async def create_questionnaire(
        self,
        data: QuestionnaireCreate,
        user_id: int,
    ):
        old_questinnaire = await self.rep_questin.get_user_questinnaire(user_id)
        if old_questinnaire:
            await self.rep_questin.delete_user_questionnaire(user_id)
        interests_data = [item.model_dump() for item in data.interests]
        avoid_data = [item.model_dump() for item in data.avoid_gifts]

        new_items = await self.rep_questin.create_questionnaire(
            user_id,
            interests_data,
            avoid_data
        )
        message = {
            "success": True,
            "items_count": len(new_items)
        }
        return message

    async def create_tags(
        self,
        data: TagCreate,
        user_id: int
    ):
        tag_value = data.tag_value
        type_tag = data.type_tag
        detail_text = data.detail

        tag_exist_standart = await self.rep_questin.get_tag(
            tag_value,
            type_tag
        )

        if tag_exist_standart:
            # return None
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Error to create = tag_exist_standart"
            )

        tag_exist_user = await self.rep_questin.get_tag_user(
            user_id,
            tag_value,
            type_tag
        )

        if tag_exist_user:
            # return None
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Error to create = tag_exist_user"
            )

        tag_create = await self.rep_questin.create_tag(
            user_id,
            tag_value,
            detail_text,
            type_tag
        )
        if not tag_create:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Error to create = tag_create"
            )
            return None
        return TagForm.model_validate(tag_create)
