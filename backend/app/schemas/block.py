from pydantic import BaseModel, ConfigDict
from datetime import datetime
from typing import Optional, List
from .user import UserPublicResponse


class BlockCreate(BaseModel):
    blocked_id: int


class BlockResponse(BaseModel):
    id: int
    blocker_id: int
    blocked_id: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class BlockStatusResponse(BaseModel):
    is_blooked: bool
    block_record: Optional[BlockResponse] = None

    model_config = ConfigDict(from_attributes=True)


class BlockListResponse(BaseModel):
    blocked_users: List[UserPublicResponse]
    total: int

    class Config:
        from_attributes = True
