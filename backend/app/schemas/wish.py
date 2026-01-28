from pydantic import BaseModel, ConfigDict
from typing import Optional, List
from datetime import datetime
from enum import Enum


class CurrencyEnum(str, Enum):
    RUB = "RUB"
    BYN = "BYN"
    USD = "USD"
    EUR = "EUR"
    UAH = "UAH"
    KZT = "KZT"


class WishBase(BaseModel):
    user_id: int
    name: str
    photo: Optional[str] = None
    url_gift: str
    price: float
    currency: CurrencyEnum = CurrencyEnum.RUB
    description: str

    model_config = ConfigDict(from_attributes=True)


class WishCreate(BaseModel):
    name: str
    photo: Optional[str] = None
    url_gift: str
    price: float
    currency: CurrencyEnum = CurrencyEnum.RUB
    description: str


class WishCreateDb(WishCreate):
    user_id: int


class WishUpdate(BaseModel):
    name: str
    photo: Optional[str] = None
    url_gift: str
    price: float
    currency: CurrencyEnum = CurrencyEnum.RUB
    description: str
    is_booked: bool
    status_is_finished: bool


class WishResponse(WishBase):
    id: int
    user_id: int
    is_booked: bool
    status_is_finished: bool
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class WishResponseMoreInfo(WishResponse):
    wishlists: List[dict]
    model_config = ConfigDict(from_attributes=True)


class WishShort(BaseModel):
    id: int
    name: str
    photo: Optional[str] = None
    price: int
    url_gift: str
    currency: CurrencyEnum
    is_booked: bool

    model_config = ConfigDict(from_attributes=True)
