from pydantic import BaseModel, ConfigDict, Field, validator
from typing import Optional, List
from datetime import datetime


class SubscriptionBase(BaseModel):
    type_sub: bool = Field(
        default=True,
        description="True - for user subscribe, Fasle - for wishlist"
    )
    target_user_id: Optional[int] = None
    target_wishlist_id: Optional[int] = None

    @validator("target_user_id", "target_wishlist_id")
    def validate_targets(cls, v, values, **kwargs):
        field_name = kwargs["field"].name
        type_sub = values.get("type_sub", True)
        if type_sub:
            if field_name == "target_user_id" and v is None:
                raise ValueError("target_user_id must be add ot subscribe")
            if field_name == "target_wishlist_id" and v is not None:
                raise ValueError("target_wishlist_id must be None to user_sub")
        else:
            if field_name == "target_wishlist_id" and v is None:
                raise ValueError("target_wishlist_id must be add ot subscribe")
            if field_name == "target_user_id" and v is not None:
                raise ValueError("target_wishlist_id must be None to user_sub")
