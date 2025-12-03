from pydantic import BaseModel, ConfigDict
from typing import Optional
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
    name: str
    birth_date: date
    photo: Optional[str] = None
    theme: ThemeEnum = ThemeEnum.light
    text_size: TextSizeEnum = TextSizeEnum.medium
    show_sub: bool = False

    model_config = ConfigDict(from_attributes=True)


class UserCreate(BaseModel):
    telegram_id: int
    name: str
    birth_date: date
    photo: Optional[str] = None
    theme: ThemeEnum = ThemeEnum.light
    text_size: TextSizeEnum = TextSizeEnum.medium
    show_sub: bool = False


class UserUpdate(BaseModel):
    name: Optional[str] = None
    birth_date: Optional[date] = None
    photo: Optional[str] = None
    theme: Optional[ThemeEnum] = None
    text_size: Optional[TextSizeEnum] = None
    show_sub: Optional[bool] = None


class UserResponse(UserBase):
    id: int
    telegram_id: int
    name: str
    birth_date: date
    photo: Optional[str] = None
    theme: ThemeEnum
    text_size: TextSizeEnum
    show_sub: bool
    created_at: datetime
    updated_at: datetime


class TelegramAuthReques(BaseModel):
    initData: str
    user: dict


class AuthRespones(BaseModel):
    success: bool
    token: str
    user: UserResponse
