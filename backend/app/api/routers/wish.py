from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from app.core.db import get_db
from app.models.wish import Wish
from app.services.wish_service import WishService
from app.schemas.wish import WishCreate, WishResponse, WishShort, WishUpdate


router = APIRouter(prefix="/wishes", tags=["wishes"])


@router.get("/", response_model=List[WishShort])
async def get_wishes(
    user_id: int,
    limit: int = Query(100, ge=1, le=200),
    db: AsyncSession = Depends(get_db)
):
    service = WishService(db)
    return await service.get_user_wish(user_id, limit)


@router.get("/{wish_id}", response_model=WishResponse)
async def get_wish(
    wish_id: int,
    db: AsyncSession = Depends(get_db)
):
    service = WishService(db)
    wish = await service.get_wish(wish_id)
    if not wish:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Wish not found"
        )
    return wish


@router.post("/", response_model=WishResponse, status_code=status.HTTP_201_CREATED)
async def create_wish(
    wish_data: WishCreate,
    user_id: int,
    db: AsyncSession = Depends(get_db)
):
    service = WishService(db)
    return await service.create_wish(user_id, wish_data)


@router.put("/{wish_id}", response_model=WishResponse)
async def update_wish(
    wish_id: int,
    wish_data: WishUpdate,
    db: AsyncSession = Depends(get_db)
):
    service = WishService(db)
    wish = await service.update_wish(wish_id, wish_data)
    if not wish:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Wish not found"
        )
    return wish


@router.delete("/{wish_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_wish(
    wish_id: int,
    db: AsyncSession = Depends(get_db)
):
    async with db.begin():
        service = WishService(db)
        delete_status = await service.delete_wish(wish_id)
        if not delete_status:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Wish not found"
            )
