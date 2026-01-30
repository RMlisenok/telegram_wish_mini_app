from pydantic import BaseModel, Field
from typing import Optional, List
from app.schemas.wishlist import TypePrivacyEnum
from datetime import datetime


class UserSubscription(BaseModel):
    id: int
    name: str
    photo: Optional[str] = None
    user_id: int


class WishlistSubscription(BaseModel):
    id: int  # ID вишлиста
    name: str
    description: Optional[str] = None
    photo: Optional[str] = None
    type_privacy: TypePrivacyEnum


class SubscriptionsResponse(BaseModel):
    subscriptions: List[dict]
    total: int


class SubscribersResponse(BaseModel):
    subscribers: List[dict]
    total: int


class SubscribersVisitUpdate(BaseModel):
    status: bool
    updated_at: datetime


class SubscribeToUserRequest(BaseModel):
    target_user_id: int = Field(..., description="ID пользователя")


class SubscribeToWishlistRequest(BaseModel):
    target_wishlist_id: int = Field(..., description="ID вишлиста")
