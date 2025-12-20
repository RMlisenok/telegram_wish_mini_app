from pydantic import BaseModel, ConfigDict
from typing import Optional
from datetime import datetime


class WishWishlistBase(BaseModel):
    is_pinned: bool
    orded_position: int


class WishWishlistResponse(BaseModel):
    id: int
    wish_id: int
    wishlist_id: str
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class WishWishlistCreate(WishWishlistBase):
    wish_id: int
    wishlist_id: int


class WishWishlistUpdate(BaseModel):
    is_pinned: Optional[bool]
    order_position: Optional[int]
