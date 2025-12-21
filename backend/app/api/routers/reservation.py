from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.db import get_db
from app.models.wish_reservation import WishReservation
from app.services.wish_reservation_service import ReservationService
from app.schemas.wish_reservation import ReservationCreate, ReservationResponse

router = APIRouter(prefix="/reservations", tags=["reservations"])


@router.get("/", response_model=List[ReservationResponse])
async def get_user_reservation(
    user_id: int,
    limit: int = 10,
    db: AsyncSession = Depends(get_db)
):
    service = ReservationService(db)
    return await service.get_user_reservation(user_id, limit)


@router.post("/",
             response_model=ReservationResponse,
             status_code=status.HTTP_201_CREATED)
async def create_reservation(
    user_id: int,
    reservation_data: ReservationCreate,
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
            detail="Failed to create reservation"
        )
    return reservation


@router.delete("/{reservation_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_reservation(
    reservation_id: int,
    db: AsyncSession = Depends(get_db)
):
    service = ReservationService(db)
    succes = await service.remove_reservation(reservation_id)
    if not succes:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Not found reservetion"
        )

# @router.get("/wish/{wish_wishlist_id}", response_model=List[ReservationResponse])
# async def get_wish_reservations(
#     wish_wishlist_id: int,
#     limit: int = Query(100, ge=1, le=200),
#     db: AsyncSession = Depends(get_db)
# ):
#     service = ReservationService(db)
#     return await service.get_wish_reservations(wish_wishlist_id, limit)