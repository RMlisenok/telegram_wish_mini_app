from pydantic import BaseModel, ConfigDict
from datetime import datetime
from typing import Optional, List
from .user import UserResponse


class BlockCreate(BaseModel):
    blocked_id: int
    block_profile: Optional[bool] = True
    block_wishlists: Optional[bool] = True


class UpdateBlock(BaseModel):
    block_profile: Optional[bool] = True
    block_wishlists: Optional[bool] = True


class BlockResponse(BaseModel):
    id: int
    blocker_id: int
    blocked_id: int
    block_profile: bool
    block_wishlists: bool
    created_at: datetime
    updated_at: datetime
    model_config = ConfigDict(from_attributes=True)


class BlockStatusResponse(BaseModel):
    is_blooked: bool
    block_profile: bool
    block_wishlists: bool
    block_record: Optional[BlockResponse] = None

    model_config = ConfigDict(from_attributes=True)


class BlockListUser(BaseModel):
    blocked_user: UserResponse
    block_profile: bool
    block_wishlists: bool

    model_config = ConfigDict(from_attributes=True)


class BlockListResponse(BaseModel):
    blocked_users: List[BlockListUser]
    total: int

    class Config:
        from_attributes = True
