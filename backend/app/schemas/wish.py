from pydantic import BaseModel, ConfigDict
from typing import Optional, List
from datetime import date, datetime
from enum import Enum


class CurrencyEnum(str, Enum):
    RUB = "RUB"
    BYN = "BYN"
    USD = "USD"
    EUR = "EUR"
    UAH = "UAH"
    KZT = "KZT"


class WishBase(BaseModel):
    name: str
    photo: Optional[str] = None
    usrl_gift: str
    price: float
    currency: CurrencyEnum = CurrencyEnum.RUB
    description: str

    model_config = ConfigDict(from_attributes=True)


class WishCreate(WishBase):
    pass


class WishUpdate(BaseModel):
    name: str
    photo: Optional[str] = None
    usrl_gift: str
    price: float
    currency: CurrencyEnum = CurrencyEnum.RUB
    description: str


class WishResponse(WishBase):
    id: int
    created_at: datetime
    updated_at: datetime
    wishlists: List["WishlistShort"] = []

    model_config = ConfigDict(from_attributes=True)


class WishShort(BaseModel):
    id: int
    name: str
    photo: Optional[str] = None
    url_gift: str
    currency: CurrencyEnum
    price: int
    is_booked: bool

    model_config = ConfigDict(from_attributes=True)
