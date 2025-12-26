from fastapi import APIRouter, Depends, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.db import get_db
from app.services.recommendation_service import RecommendationService

from app.core.dependencies import get_current_user_id

router = APIRouter(prefix="/recommendations", tags=["Рекомендации"])


@router.post("/trigger/{target_user_id}")
async def trigger_recommendations(
        target_user_id: int,
        background_tasks: BackgroundTasks,
        db: AsyncSession = Depends(get_db),
        current_user_id: int = Depends(get_current_user_id)
):
    background_tasks.add_task(
        RecommendationService.generate_and_send_via_bot,
        db_factory=get_db,
        requester_id=current_user_id,
        target_id=target_user_id
    )

    return {"message": "📨 Отправили вам подборку в личные сообщения"}