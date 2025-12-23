from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

from app.core.db import get_db
from app.schemas.questionnaire import (
    QuestionnaireCreate,
    QuestionnaireResponse,
    TagResponse
)
from app.service.questionnaire_service import QuestionnaireService
from app.core.dependencies import get_current_user_id

router = APIRouter(
    prefix="/questionnaire",
    tags=["Анкета"]
)

@router.get("", response_model=QuestionnaireResponse)
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

@router.post("", status_code=status.HTTP_200_OK)
async def save_questionnaire(
    data: QuestionnaireCreate,
    db: AsyncSession = Depends(get_db),
    user_id: int = Depends(get_current_user_id)
):
    """
    Сохранить или полностью обновить анкету пользователя.
    """
    service = QuestionnaireService(db)
    return await service.update_questionnaire(user_id, data)

@router.get("/{user_id}", response_model=QuestionnaireResponse)
async def get_user_questionnaire(
    user_id: int,
    db: AsyncSession = Depends(get_db)
):
    """
    Получить анкету другого пользователя (для алгоритма рекомендаций другу).
    """
    service = QuestionnaireService(db)
    questionnaire = await service.get_user_questionnaire(user_id)
    if not questionnaire:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Анкета пользователя не заполнена"
        )
    return questionnaire

@router.get("/tags/available", response_model=List[TagResponse])
async def get_available_tags(
    is_interest: bool = True,
    db: AsyncSession = Depends(get_db)
):
    """
    Получить список всех доступных тегов из tags_forms для выбора в приложении.
    """
    service = QuestionnaireService(db)
    return await service.get_all_tags(is_interest)