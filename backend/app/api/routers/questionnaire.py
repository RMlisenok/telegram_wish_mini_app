from fastapi import APIRouter, Depends, HTTPException, status, logger
from sqlalchemy import select, delete
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional
from app.core.db import get_db
from app.schemas.questionnaire import (
    QuestionnaireCreate,
    QuestionnaireResponse,
    TagResponse
)
from app.services.questionnaire_service import QuestionnaireService
from app.core.dependencies import get_current_user_id
from app.models.questionnaire import TagForm, UserForm

router = APIRouter(
    prefix="/questionnaire",
    tags=["Questionnaire"]
)


@router.get("/", response_model=QuestionnaireResponse)
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


@router.post("/")
async def save_full_questionnaire(
    data: QuestionnaireCreate,
    db: AsyncSession = Depends(get_db),
    user_id: int = Depends(get_current_user_id)
):
    service = QuestionnaireService(db)
    return await service.update_questionnaire(user_id, data)
# @router.post("")
# async def save_full_questionnaire(
#         payload: dict,
#         db: AsyncSession = Depends(get_db),
#         user_id: int = Depends(get_current_user_id)
# ):
#     try:
#         await db.execute(delete(UserForm).where(UserForm.user_id == user_id))
#         async def process_items(items, is_interest: bool):
#             for item in items:
#                 tag_text = item.get("tag")
#                 detail_text = item.get("details")  # Из фронта берем 'details'
#
#                 if not tag_text:
#                     continue
#
#                 tag_stmt = select(TagForm).where(TagForm.tag_value == tag_text)
#                 tag_obj = (await db.execute(tag_stmt)).scalar_one_or_none()
#
#                 if tag_obj:
#                     db.add(UserForm(
#                         user_id=user_id,
#                         tag_id=tag_obj.id,  # Сохраняем ID из справочника
#                         detail=detail_text,  # Сохраняем в колонку 'detail'
#                         type_tag=is_interest
#                     ))
#                 else:
#                     logger.warning(f"Tag '{tag_text}' noy found in the directory")
#
#         await process_items(payload.get("interests", []), True)
#         await process_items(payload.get("avoid_gifts", []), False)
#
#         await db.commit()
#         return {"status": "ok", "message": "Анкета успешно сохранена через ID"}
#     except Exception as e:
#         await db.rollback()
#         logger.error(f"Ошибка при сохранении анкеты: {e}", exc_info=True)
#         raise HTTPException(
#             status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
#             detail=f"Ошибка базы данных: {str(e)}"
#         )


@router.get("/tags/available")
async def get_available_tags(
    is_interest: bool,
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(
        select(TagForm).where(TagForm.type_tags == is_interest)
    )
    tags = result.scalars().all()
    return [{"tag_value": t.tag_value} for t in tags]


@router.get("/my-answers")
async def get_my_answers(
        db: AsyncSession = Depends(get_db),
        user_id: int = Depends(get_current_user_id)
):
    stmt = select(UserForm, TagForm.tag_value).join(TagForm).where(UserForm.user_id == user_id)
    result = await db.execute(stmt)

    answers = []
    for row in result.all():
        answers.append({
            "tag_id": row.UserForm.tag_id,
            "tag_name": row.tag_value,
            "detail": row.UserForm.detail
        })

    return answers


@router.post("/answer")
async def save_answer(
        data: dict,
        db: AsyncSession = Depends(get_db),
        user_id: int = Depends(get_current_user_id)
):
    tag_id = data.get("tag_id")
    detail_text = data.get("details", "")

    if not tag_id:
        raise HTTPException(status_code=400, detail="tag_id is required")

    tag_exists = await db.execute(select(TagForm).where(TagForm.id == tag_id))
    if not tag_exists.scalar_one_or_none():
        raise HTTPException(status_code=404, detail="Тег не найден")

    stmt = select(UserForm).where(
        UserForm.user_id == user_id,
        UserForm.tag_id == tag_id
    )
    result = await db.execute(stmt)
    user_answer = result.scalar_one_or_none()

    if user_answer:
        user_answer.detail = detail_text  # Исправлено на detail
    else:
        db.add(UserForm(
            user_id=user_id,
            tag_id=tag_id,
            detail=detail_text  # Исправлено на detail
        ))

    await db.commit()
    return {"status": "success", "message": "Ответ сохранен"}


@router.get("/{user_id}", response_model=QuestionnaireResponse)
async def get_user_questionnaire(
        user_id: int,
        db: AsyncSession = Depends(get_db)
):
    service = QuestionnaireService(db)
    questionnaire = await service.get_user_questionnaire(user_id)
    if not questionnaire:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Анкета пользователя не найдена"
        )
    return questionnaire

# @router.get("/tags")
# async def get_all_tags(db: AsyncSession = Depends(get_db)):
#     result = await db.execute(select(TagForm))
#     return result.scalars().all()