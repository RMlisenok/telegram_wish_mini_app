from pydantic import BaseModel, ConfigDict
from typing import Optional, List
from datetime import date, datetime
from enum import Enum


class TypePrivacyEnum(str, Enum):
    public = 'public'
    private = 'private'
    protected = 'protected'


class WishlistBase(BaseModel):
    user_id: int
    name: str
    description: str
    photo: Optional[str] = None
    typeprivacy: TypePrivacyEnum = TypePrivacyEnum.public

    model_config = ConfigDict(from_attributes=True)


class WishlistCreate(WishlistBase):
    pass


class WishlistUpdate(BaseModel):
    name: str
    description: str
    photo: Optional[str] = None
    typeprivacy: TypePrivacyEnum = TypePrivacyEnum.public


class WishlistResponse(WishlistBase):
    id: int
    created_at: datetime
    updated_at: datetime
    wishes: List["WishShort"] = []
    wishes_count: int = 0

    model_config = ConfigDict(from_attributes=True)


class WishlistShort(BaseModel):
    id: int
    name: str
    photo: Optional[str] = None
    privacy: TypePrivacyEnum

    model_config = ConfigDict(from_attributes=True)
