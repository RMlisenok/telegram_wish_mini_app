from typing import Optional, List
from pydantic import BaseModel, ConfigDict
from datetime import datetime
import enum


class AccessRequestStatus(str, enum.Enum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"


class AccessRequestCreate(BaseModel):
    wishlist_id: int


class AccessRequestResponse(BaseModel):
    id: int
    wishlist_id: int
    requester_id: int
    status: AccessRequestStatus
    created_at: datetime
    processed_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)


class AccessRequestWithDetails(AccessRequestResponse):
    wishlist_name: Optional[str] = None
    wishlist_photo: Optional[str] = None
    requester_name: Optional[str] = None
    requester_photo: Optional[str] = None
    owner_id: Optional[int] = None
    owner_name: Optional[str] = None


class AccessRequestsResponse(BaseModel):
    requests: List[AccessRequestWithDetails]
    total: int


class UpdateAccessRequest(BaseModel):
    status: AccessRequestStatus
