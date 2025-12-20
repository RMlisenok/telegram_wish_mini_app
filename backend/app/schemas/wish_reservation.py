from pydantic import BaseModel, ConfigDict
from datetime import datetime


class ReservationResponse(BaseModel):
    wish_wishlist_id: int
    reserved_by_id: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class ReservationCreate(BaseModel):
    wish_wishlist_id: int
