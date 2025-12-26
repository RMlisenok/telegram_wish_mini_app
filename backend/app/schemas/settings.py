from pydantic import BaseModel
from typing import Optional

class NotificationSettingsResponse(BaseModel):
    new_followers: bool
    access_requests: bool
    birt_after: bool
    birt_before: bool

    class Config:
        from_attributes = True

class NotificationSettingsUpdate(BaseModel):
    new_followers: Optional[bool] = None
    access_requests: Optional[bool] = None
    birt_after: Optional[bool] = None
    birt_before: Optional[bool] = None