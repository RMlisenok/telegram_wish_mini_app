from pydantic import BaseModel, ConfigDict
from typing import Optional, List
from datetime import date, datetime
from enum import Enum


class ThemeEnum(str, Enum):
    light = 'light'
    dark = 'dark'
    system = 'system'


class TextSizeEnum(str, Enum):
    small = 'small'
    medium = 'medium'
    large = 'large'


class UserBase(BaseModel):
    telegram_id: int
    name: str
    birth_date: Optional[date] = None
    photo: Optional[str] = None
    theme: ThemeEnum = ThemeEnum.light
    text_size: TextSizeEnum = TextSizeEnum.medium
    show_sub: bool = False

    model_config = ConfigDict(from_attributes=True)


class UserCreate(UserBase):
    pass


class UserUpdate(BaseModel):
    name: Optional[str] = None
    birth_date: Optional[date] = None
    photo: Optional[str] = None
    theme: Optional[ThemeEnum] = None
    text_size: Optional[TextSizeEnum] = None
    show_sub: Optional[bool] = None


class UserResponse(UserBase):
    id: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class UserPublicResponse(BaseModel):
    id: int
    name: str
    photo: Optional[str] = None

    class Config:
        from_attributes = True


class UserListResponse(BaseModel):
    users: List[UserPublicResponse]
    total: int

    class Config:
        from_attributes = True


class TelegramAuthReques(BaseModel):
    initData: str
    user: dict


class AuthRespones(BaseModel):
    success: bool
    token: str
    user: UserResponse


class Usershort(BaseModel):
    id: int
    telegram_id: int
    name: str
    photo: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)
