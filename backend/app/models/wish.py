from typing import Optional, List
from sqlalchemy import String, Enum, Text, TIMESTAMP, BigInteger, ForeignKey, Numeric, Boolean
from sqlalchemy.sql import func
from sqlalchemy.orm import Mapped, mapped_column, relationship
import enum
from app.core.base import Base

class CurrencyEnum(enum.Enum):
    RUB = "RUB"
    BYN = "BYN"
    USD = "USD"
    EUR = "EUR"
    UAH = "UAH"
    KZT = "KZT"


class Wish(Base):
    __tablename__ = 'wishes'

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey("users.id"),
        nullable=False
    )
    name: Mapped[str] = mapped_column(String(50), nullable=False)
    photo: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    url_gift: Mapped[Optional[str]] = mapped_column(String(2048), nullable=True)
    price: Mapped[Optional[float]] = mapped_column(Numeric(12, 2), nullable=True)
    currency: Mapped[CurrencyEnum] = mapped_column(
        Enum(CurrencyEnum),
        default=CurrencyEnum.RUB
    )
    description: Mapped[Optional[str]] = mapped_column(String(250), nullable=True)
    is_booked: Mapped[bool] = mapped_column(Boolean, default=False)
    status_is_finished: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[TIMESTAMP] = mapped_column(
        TIMESTAMP,
        server_default=func.now()
    )
    updated_at: Mapped[TIMESTAMP] = mapped_column(
        TIMESTAMP,
        server_default=func.now(),
        onupdate=func.now()
    )

    owner: Mapped["User"] = relationship("User", back_populates="wishes")

    wish_associations: Mapped[List["WishWishlist"]] = relationship(
        "WishWishlist",
        back_populates="wish",
        cascade="all, delete-orphan"
    )
