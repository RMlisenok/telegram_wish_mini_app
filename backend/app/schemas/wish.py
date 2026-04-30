from pydantic import BaseModel, ConfigDict, validator
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
    url_gift: Optional[str] = None
    price: Optional[float] = None
    currency: Optional[CurrencyEnum] = None
    description: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


class WishCreate(BaseModel):
    name: str
    photo: Optional[str] = None
    url_gift: Optional[str] = None
    price: Optional[float] = None
    currency: Optional[CurrencyEnum] = None
    description: Optional[str] = None

    @validator('price')
    def price_positive(cls, v):
        if v is not None and v <= 0:
            raise ValueError('Price must be positive')
        return v


class WishCreateDb(WishCreate):
    user_id: int


class WishUpdate(BaseModel):
    name: str
    photo: Optional[str] = None
    url_gift: Optional[str] = None
    price: Optional[float] = None
    currency: Optional[CurrencyEnum] = None
    description: Optional[str] = None
    is_booked: Optional[bool] = False
    status_is_finished: Optional[bool] = False


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
