from sqlalchemy import(
    String, Text, Numeric, Boolean, TIMESTAMP, ForeignKey, Enum
)
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship, Mapped, mapped_column
from typing import Optional, List
from datetime import datetime
import enum

from app.core.base import Base


class WishStatusEnum(str, enum.Enum):
    active = 'active'
    completed = 'completed'
    archived = 'archived'


class CurrencyEnum(str, enum.Enum):
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
        ForeignKey('user.id', ondelete='CASCADE'),
        nullable=False,
        index=True
    )
    name: Mapped[str] = mapped_column(
        String(100),
        nullable=False
        )
    photo: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=False
        )
    url_gift: Mapped[Optional[str]] = mapped_column(
        String(2048),
        nullable=True
        )
    price: Mapped[Optional[float]] = mapped_column(
        Numeric(2),
        nullable=True
    )
    currency: Mapped[Optional[CurrencyEnum]] = mapped_column(
        Enum(CurrencyEnum),
        nullable=True
    )
    description: Mapped[Optional[str]] = mapped_column(
        Text, nullable=True
    )
    status: Mapped(WishStatusEnum) = mapped_column(
        Enum(WishStatusEnum),
        default=WishStatusEnum.active
    )

    created_at: Mapped[datetime] = mapped_column(
        TIMESTAMP,
        server_default=func.now()
    )

    created_at: Mapped[datetime] = mapped_column(
        TIMESTAMP,
        server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        TIMESTAMP,
        server_default=func.now(),
        onupdate=func.now()
    )

    owner: Mapped['User'] = relationship(back_populates='wishes')
    wishlist_associations: Mapped[List['WishWishlist']] = relationship(
        back_populates='wish',
        cascade='all, delete-orphan'
    )

    wish_reservations: Mapped[List['WishReservation']] = relationship(
        back_populates='wish'
    )
    
    # Property для удобного доступа
    @property
    def wishlists(self):
        return [assoc.wishlist for assoc in self.wishlist_associations]