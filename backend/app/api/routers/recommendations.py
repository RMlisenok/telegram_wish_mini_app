from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.db import get_session
from app.services.recommendations_service import RecommendationService
from app.schemas.recommendations import GiftResponse

router = APIRouter(prefix="/recommendations", tags=["Recommendations"])

@router.get("/{user_id}", response_model=list[GiftResponse])
async def get_gift_recommendations(user_id: int, session: AsyncSession = Depends(get_session)):
    gifts = await RecommendationService.get_recommendations(session, user_id)
    if not gifts:
        raise HTTPException(status_code=404, detail="Не удалось подобрать подарки. Заполните анкету!")
    return gifts