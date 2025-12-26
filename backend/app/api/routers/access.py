from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.db import get_db
from app.services.notification_service import NotificationService
from app.core.dependencies import get_current_user_id

router = APIRouter(prefix="/access", tags=["Доступ"])

@router.post("/request/{wishlist_id}")
async def request_access(
        wishlist_id: int,
        db: AsyncSession = Depends(get_db),
        user_id: int = Depends(get_current_user_id)
):
    # 1. Логика создания заявки в БД
    # ... (код сохранения заявки)


    notif_service = NotificationService(bot)
    await notif_service.notify_access_request(
        session=db,
        requester_id=user_id,
        owner_id=wishlist_owner_id,
        wishlist_name="Мой секретный список",
        request_id=new_request_id
    )

    return {"status": "request_sent"}