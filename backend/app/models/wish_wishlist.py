from sqlalchemy import Boolean, TIMESTAMP, BigInteger, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import mapped_column, Mapped, relationship
from app.core.base import Base
from typing import List


class WishWishlist(Base):
    __tablename__ = 'wish_wishlist'

    id: Mapped[int] = mapped_column(primary_key=True)

    wish_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey("wishes.id", ondelete="CASCADE"),
        nullable=False
    )

    wishlist_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey("wishlists.id"),
        nullable=False
    )

    is_pinned: Mapped[bool] = mapped_column(Boolean, default=False)
    order_position: Mapped[int] = mapped_column(default=0)

    created_at: Mapped[TIMESTAMP] = mapped_column(
        TIMESTAMP,
        server_default=func.now()
    )
    updated_at: Mapped[TIMESTAMP] = mapped_column(
        TIMESTAMP,
        server_default=func.now(),
        onupdate=func.now()
    )

    wish: Mapped["Wish"] = relationship(
        "Wish",
        back_populates="wish_associations"
    )

    wishlist: Mapped["Wishlist"] = relationship(
        "Wishlist",
        back_populates="wish_associations"
    )

    reservations: Mapped[List["WishReservation"]] = relationship(
        "WishReservation",
        back_populates="wish_wishlist",
        cascade="all, delete-orphan"
    )
