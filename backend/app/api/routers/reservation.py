from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.db import get_db
from app.core.dependencies import get_current_user_id
from app.models.wish_reservation import WishReservation
from app.services.wish_reservation_service import ReservationService
from app.schemas.wish_reservation import ReservationCreate, ReservationResponse

router = APIRouter(prefix="/reservations", tags=["reservations"])


@router.get("/", response_model=List[ReservationResponse])
async def get_user_reservation(
    user_id: int = Depends(get_current_user_id),
    limit: int = 10,
    db: AsyncSession = Depends(get_db)
):
    service = ReservationService(db)
    return await service.get_user_reservation(user_id, limit)


@router.post("/",
             response_model=ReservationResponse,
             status_code=status.HTTP_201_CREATED)
async def create_reservation(
    reservation_data: ReservationCreate,
    user_id: int = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db)
):
    service = ReservationService(db)
    reservation = await service.create_reservation(
        user_id,
        reservation_data
    )
    if not reservation:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Failed TO create reservation"
        )
    return reservation


@router.delete("/delete/")
async def delete_reservation(
    wish_wishlist_id: int,
    reserved_by_id: int = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db)
):
    async with db.begin():
        service = ReservationService(db)
        success = await service.remove_reservation(
            wish_wishlist_id,
            reserved_by_id
        )
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Reservation not found"
            )
    return
