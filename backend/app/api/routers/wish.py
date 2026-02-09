from fastapi import APIRouter, Depends, File, HTTPException, status, UploadFile
from pydantic import Json
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from app.core.db import get_db
from app.models.wish import Wish
from app.core.dependencies import get_current_user_id
from app.services.wish_service import WishService
from app.schemas.wish import (
    WishCreate,
    WishResponse,
    WishUpdate,
    WishResponseMoreInfo
    )


router = APIRouter(prefix="/wishes", tags=["wishes"])


@router.get("/", response_model=List[WishResponse])
async def get_wishes(
    user_id: int = Depends(get_current_user_id),
    is_desc: bool = True,
    limit: int = 10,
    db: AsyncSession = Depends(get_db)
):
    service = WishService(db)
    return await service.get_user_wish(user_id, is_desc, limit)


@router.get("/finish", response_model=List[WishResponse])
async def get_wishes_sorted(
    user_id: int = Depends(get_current_user_id),
    is_finish: bool = True,
    limit: int = 10,
    db: AsyncSession = Depends(get_db)
):
    service = WishService(db)
    return await service.get_user_wish_sorted(user_id, is_finish, limit)


@router.get("/{wish_id}", response_model=WishResponseMoreInfo)
async def get_wish(
    wish_id: int,
    db: AsyncSession = Depends(get_db)
):
    service = WishService(db)
    wish = await service.get_wish_with_wishlists_info(wish_id)
    if not wish:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Wish not found"
        )
    return wish


@router.post("/",
             response_model=WishResponse,
             status_code=status.HTTP_201_CREATED)
async def create_wish(
    wish_data: WishCreate,
    user_id: int = Depends(get_current_user_id),
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


@router.delete("/{wish_id}",
               status_code=status.HTTP_204_NO_CONTENT)
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


@router.delete("/wishlists/{wish_id}")
async def connect_wishlist_with_wish(
    wish_id: int,
    db: AsyncSession = Depends(get_db)
    # user_id: int = Depends(get_current_user_id)
):
    async with db.begin():
        service = WishService(db)
        delete_status = await service.delete_wish_in_wishlists(
            wish_id,
            # user_id
        )
        if not delete_status:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Wish not found"
            )
