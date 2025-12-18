from pydantic import BaseModel, ConfigDict
from datetime import datetime


class ReservationResponse(BaseModel):
    id: int
    wish_wishlist_id: int
    reserved_by_id: int
    created_at: datetime
    reserved_by: "UserShort"

    model_config = ConfigDict(from_attributes=True)
