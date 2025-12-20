from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.db import get_db
from app.models.wishlist import Wishlist
from app.services.wishlist_service import WishlistService
from app.schemas.wishlist import WishlistCreate, WishlistResponse, WishlistUpdate
from app.schemas.wish_wishlist import WishWishlistCreate, WishWishlistResponse, WishWishlistUpdate

router = APIRouter(prefix="/wishlists", tags=["wishlists"])


@router.get("/",
            response_model=List[WishlistResponse])
async def get_user_wishlists(
    user_id: int,
    limit: int = 10,
    db: AsyncSession = Depends(get_db)
) -> List[WishlistResponse]:
    service = WishlistService(db)
    return await service.get_user_wishlist(user_id, limit)


@router.get("/{wishlist_id}",
            response_model=WishlistResponse)
async def get_wishlist(
    wishlist_id: int,
    db: AsyncSession = Depends(get_db)
):
    service = WishlistService(db)
    wishlist = await service.get_wishlist(wishlist_id)
    if not wishlist:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Wishlist not found"
        )
    return wishlist


@router.post("/",
             response_model=WishlistResponse,
             status_code=status.HTTP_201_CREATED)
async def create_wishlist(
    user_id: int,
    wishlist_data: WishlistCreate,
    db: AsyncSession = Depends(get_db)
):
    service = WishlistService(db)
    return await service.create_wishlist(user_id, wishlist_data)


@router.put("/{wishlist_id}",
            response_model=WishlistResponse)
async def update_wishlist(
    wishlist_id: int,
    wishlist_data: WishlistUpdate,
    db: AsyncSession = Depends(get_db)
):
    service = WishlistService(db)
    wishlist = await service.update_wishlist(wishlist_id, wishlist_data)
    if not wishlist:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Wishlist not found"
        )
    return wishlist


@router.delete("/{wishlist_id}",
               status_code=status.HTTP_204_NO_CONTENT)
async def delete_wishlist(
    wishlist_id: int,
    db: AsyncSession = Depends(get_db)
):
    async with db.begin():
        service = WishlistService(db)
        delete_status = await service.delete(wishlist_id)
    if not delete_status:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Wishlist not found"
        )


@router.post("/{wishlist_id}/wishes",
             response_model=WishWishlistResponse,
             status_code=status.HTTP_201_CREATED)
async def add_wish_to_wishlist(
    wishlist_id: int,
    connect_data: WishWishlistCreate,
    db: AsyncSession = Depends(get_db)
):
    service = WishlistService(db)
    if connect_data.wishlist_id != wishlist_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Wishlist ID mismatch"
        )
    connection = service.add_wish_to_wishlist(connect_data)
    if not connection:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Failed to add wish to wishlist. Check if wish exists or already in wishlist."
        )

    return connection

@router.put("/connections/{connection_id}",
            response_model=WishWishlistResponse)
async def update_wish_to_wishlist(
    connection_id: int,
    update_data: WishWishlistUpdate,
    db: AsyncSession = Depends(get_db)
):
    service = WishlistService(db)
    connection = await service.update_wihs_in_wishlits(
        connection_id,
        update_data
    )

    if not connection:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Connection not found"
        )
    return connection


@router.delete("/{wishlist_id}/wishes/{wish_id}",
               status_code=status.HTTP_204_NO_CONTENT)
async def delete_wish_to_wishlist(
    wish_id: int,
    wishlist_id: int,
    db: AsyncSession = Depends(get_db)
):
    service = WishlistService(db)
    succes = service.remove_wish_from_wishlist(
        wish_id,
        wishlist_id
    )
    if not succes:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Wish not found in wishlist"
        )
