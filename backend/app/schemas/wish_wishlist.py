from pydantic import BaseModel, Field, ConfigDict
from typing import Optional
from datetime import datetime


class WishWishlistResponse(BaseModel):
    wish_id: int
    wishlist_id: str
    is_pinned: bool
    orded_position: int
    created_at: datetime
    updated_at: datetime
    wish: "WishShort"
    wishlist: "WishlistShort"

    model_config = ConfigDict(from_attributes=True)


class WishWishlistUpdate(BaseModel):
    is_pinned: Optional[bool]
    order_position: Optional[int]
