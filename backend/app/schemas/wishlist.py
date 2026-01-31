from pydantic import BaseModel, ConfigDict
from typing import Optional
from datetime import datetime
from enum import Enum


class TypePrivacyEnum(str, Enum):
    public = 'public'
    private = 'private'
    protected = 'protected'


class WishlistBase(BaseModel):
    user_id: int
    name: str
    description: Optional[str] = None
    photo: Optional[str] = None
    typeprivacy: TypePrivacyEnum = TypePrivacyEnum.public

    # model_config = ConfigDict(from_attributes=True)


class WishlistCreate(BaseModel):
    name: str
    description: Optional[str] = None
    photo: Optional[str] = None
    typeprivacy: TypePrivacyEnum = TypePrivacyEnum.public


class WishlistCreateDb(WishlistCreate):
    user_id: int


class WishlistUpdate(BaseModel):
    name: str
    description: Optional[str] = None
    photo: Optional[str] = None
    typeprivacy: TypePrivacyEnum = TypePrivacyEnum.public


class WishlistResponse(WishlistBase):
    id: int
    created_at: datetime
    updated_at: datetime
    wishes_count: int = 0

    model_config = ConfigDict(from_attributes=True)


class WishlistShort(BaseModel):
    id: int
    name: str
    photo: Optional[str] = None
    privacy: TypePrivacyEnum
    wishes_count: int = 0

    model_config = ConfigDict(from_attributes=True)
