from fastapi import APIRouter, Depends, HTTPException, status, logger
from sqlalchemy import select, delete
from sqlalchemy.ext.asyncio import AsyncSession
from app.services.user_service import UserService
from typing import List, Optional
from app.core.db import get_db
from app.schemas.questionnaire import (
    QuestionnaireCreate,
    QuestionnaireResponse,
    TagResponse,
    TagCreate
)
from app.services.questionnaire_service import QuestionnaireService
from app.core.dependencies import get_current_user_id
from app.models.questionnaire import TagForm, UserForm

router = APIRouter(
    prefix="/questionnaire",
    tags=["Questionnaire"]
)


@router.get("/")
async def get_my_questionnaire(
    db: AsyncSession = Depends(get_db),
    user_id: int = Depends(get_current_user_id)
):

    service = QuestionnaireService(db)
    questionnaire = await service.get_user_questionnaire(user_id)
    if not questionnaire:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Анкета не найдена"
        )
    return questionnaire


@router.get("/tags/available")
async def get_available_tags(
    is_interest: bool = True,
    user_id: int = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db)
):
    service = QuestionnaireService(db)
    tags = await service.get_available(user_id, is_interest)
    return {"tags": tags}


@router.post("/")
async def save_full_questionnaire(
    data: QuestionnaireCreate,
    user_id: int = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db)
):
    service = QuestionnaireService(db)
    return await service.create_questionnaire(data, user_id)


@router.get("/{user_id}")
async def get_user_questionnaire(
    user_id: int,
    db: AsyncSession = Depends(get_db)
):    
    user_service = UserService(db)
    user = await user_service.get_user(user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    service_quest = QuestionnaireService(db)
    questionnaire = await service_quest.get_user_questionnaire(user_id)
    if not questionnaire:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Questionnaire not found"
        )
    return questionnaire


@router.post("/answer")
async def save_answer(
        data: TagCreate,
        db: AsyncSession = Depends(get_db),
        user_id: int = Depends(get_current_user_id)
):

    service = QuestionnaireService(db)
    new_tag = await service.create_tags(data, user_id)
    if not new_tag:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Error to create"
        )
    return {"status": "success", "tag": new_tag}


# @router.get("/{user_id}", response_model=QuestionnaireResponse)
# async def get_user_questionnaire(
#         user_id: int,
#         db: AsyncSession = Depends(get_db)
# ):
#     service = QuestionnaireService(db)
#     questionnaire = await service.get_user_questionnaire(user_id)
#     if not questionnaire:
#         raise HTTPException(
#             status_code=status.HTTP_404_NOT_FOUND,
#             detail="Анкета пользователя не найдена"
#         )
#     return questionnaire

# # @router.get("/tags")
# # async def get_all_tags(db: AsyncSession = Depends(get_db)):
# #     result = await db.execute(select(TagForm))
# #     return result.scalars().all()