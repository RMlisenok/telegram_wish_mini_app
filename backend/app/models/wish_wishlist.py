from typing import Optional, List
from sqlalchemy import Boolean, TIMESTAMP, BigInteger, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import mapped_column, Mapped, relationship

from app.core.base import Base


class WishWishlist(Base):
    __tablename__ = 'wish_wishlist'

    id: Mapped[int] = mapped_column(
        primary_key=True
    )
    wish_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey('wishes.id', ondelete='CASCADE'),
        nullable=False
    )
    wishlist_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey()
    )
    is_pinned: Mapped[bool] = mapped_column(
        Boolean,
        default=False
    )
    order_position: Mapped[int] = mapped_column(
        default=0
    )

    wish: Mapped['Wish'] = relationship(
        back_populates='wishlists'
    )
    wishlist: Mapped['Wishlist'] = relationship(
        back_populates='wishes'
    )
    reservations: Mapped[List["WishReservation"]] = relationship(
        back_populates="wish_wishlist",
        cascade="all, delete-orphan"
    )
