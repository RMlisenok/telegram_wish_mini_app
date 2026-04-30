from pydantic import BaseModel, ConfigDict
from typing import Optional
from datetime import datetime
from .wish import CurrencyEnum

class WishWishlistBase(BaseModel):
    is_pinned: bool
    order_position: int


class WishWishlistResponse(BaseModel):
    id: int
    wish_id: int
    wishlist_id: int
    is_pinned: Optional[bool]
    order_position: Optional[int]
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class WishWishlistCreate(WishWishlistBase):
    wish_id: int
    wishlist_id: int


class WishWishlistUpdate(BaseModel):
    is_pinned: Optional[bool]
    order_position: Optional[int]


class WishInWishlistResponse(BaseModel):
    """Схема для ответа с информацией о желании в вишлисте"""

    id: int
    name: str
    photo: Optional[str] = None
    url_gift: Optional[str] = None
    price: Optional[float] = None
    currency: Optional[CurrencyEnum] = None
    description: Optional[str] = None
    is_booked: bool
    status_is_finished: bool
    created_at: datetime
    updated_at: datetime

    connection_id: int
    is_pinned: bool
    order_position: int
    added_at: datetime

    model_config = ConfigDict(from_attributes=True)
