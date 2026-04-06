from fastapi import APIRouter, Depends, HTTPException, status
# from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.db import get_db
from app.core.dependencies import get_current_user_id
from app.services.subscription_service import SubscriptionService
from app.schemas.subscription import (
    SubscribeToUserRequest,
    SubscribeToWishlistRequest,
    SubscriptionsResponse
)

router = APIRouter(prefix="/subscriptions", tags=["subscriptions"])


@router.post("/users")
async def subscribe_to_user(
    request: SubscribeToUserRequest,
    current_user_id: int = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db)
):
    service = SubscriptionService(db)
    success = await service.subscribe_to_user(
        current_user_id,
        request.target_user_id
    )
    if not success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot subscribe to this user"
        )
    return {"message": "Subscribed to this user successfully"}


@router.post("/wishlists")
async def subscribe_to_wishlist(
    request: SubscribeToWishlistRequest,
    current_user_id: int = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db)
):
    service = SubscriptionService(db)
    success = await service.subscribe_to_wishlist(
        current_user_id,
        request.target_wishlist_id
    )
    if not success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot subscribe to this wihslist"
        )
    return {"message": "Subscribed to thish wishlist successfully"}


@router.patch("/visit/{subscribe_id}")
async def visit_subscibe(
    subscribe_id: int,
    user_id: int = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db)
):
    service = SubscriptionService(db)
    success = await service.update_visit(
        user_id=user_id,
        subscribe_id=subscribe_id
    )
    if success is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Sunscription not found"
        )
    return success


@router.delete("/users/{target_user_id}")
async def unsubscribe_from_user(
    target_user_id: int,
    user_id: int = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db)
):
    service = SubscriptionService(db)
    success = await service.unsubscribe_from_user(
        user_id=user_id,
        target_user_id=target_user_id
    )
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Sunscription not found"
        )
    return {"message": "Unsubscribed successfully"}


@router.delete("/wishlists/{target_wishlist_id}")
async def unsubscribe_from_wishlist(
    target_wishlist_id: int,
    user_id: int = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db)
):
    service = SubscriptionService(db)
    success = await service.unsubscribe_from_wishlist(
        user_id=user_id,
        target_wishlist_id=target_wishlist_id
    )
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Sunscription not found"
        )
    return {"message": "Unsubscribed successfully"}


@router.get("/my", response_model=SubscriptionsResponse)
async def get_my_subscriptions(
    user_id: int = Depends(get_current_user_id),
    limit: int = 100,
    db: AsyncSession = Depends(get_db)
):
    service = SubscriptionService(db)
    return await service.get_my_subscription(user_id, limit)


@router.get("/my/users", response_model=SubscriptionsResponse)
async def get_my_user_subscriptions(
    user_id: int = Depends(get_current_user_id),
    limit: int = 100,
    db: AsyncSession = Depends(get_db)
):
    service = SubscriptionService(db)
    return await service.get_my_user_subscriptions(user_id, limit)


@router.get("/my/wishlists", response_model=SubscriptionsResponse)
async def get_my_wishlist_subscriptions(
    user_id: int = Depends(get_current_user_id),
    limit: int = 100,
    db: AsyncSession = Depends(get_db)
):
    service = SubscriptionService(db)
    return await service.get_my_wishlist_subscriptions(user_id, limit)


@router.get("/users/{user_id}", response_model=SubscriptionsResponse)
async def get_user_subscriptions(
    user_id: int,
    current_user_id: int = Depends(get_current_user_id),
    limit: int = 100,
    db: AsyncSession = Depends(get_db)
):
    service = SubscriptionService(db)
    try:
        return await service.get_user_subscriptions(
            user_id,
            current_user_id,
            limit
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str(e)
        )


@router.get("/check/user/{user_id}")
async def check_user_subscription(
    user_id: int,
    current_user_id: int = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db)
):
    service = SubscriptionService(db)
    is_subscribed = await service.check_user_subscription(
        current_user_id,
        user_id
    )
    return {"is_subscribed": is_subscribed}


@router.get("/check/wishlist/{wishlist_id}")
async def check_wishlist_subscription(
    wishlist_id: int,
    user_id: int = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db)
):
    service = SubscriptionService(db)
    is_subscribed = await service.check_wishlist_subscription(
        user_id,
        wishlist_id
    )
    return {"is_subscribed": is_subscribed}


@router.get("/my/subscribers")
async def get_my_subscribers(
    user_id: int = Depends(get_current_user_id),
    is_desc: bool = True,
    limit: int = 100,
    db: AsyncSession = Depends(get_db)
):
    service = SubscriptionService(db)
    subscribers = await service.get_user_subscribers(
        user_id,
        is_desc,
        limit
    )
    return subscribers
