from typing import Optional
from sqlalchemy import String, Text, TIMESTAMP, BigInteger, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.base import Base


class WishReservation(Base):
    __tablename__ = "wish_reservations"
    
    id: Mapped[int] = mapped_column(
        BigInteger,
        primary_key=True,
        index=True
    )
    wish_wishlist_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey("wish_wishlist.id", ondelete="CASCADE"),
        nullable=False
    )
    reserved_by_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey("users.id"),
        nullable=False
    )
    created_at: Mapped[TIMESTAMP] = mapped_column(
        TIMESTAMP,
        server_default=func.now()
    )


    wish_wishlist: Mapped['WishWishlist'] = relationship(
        back_populates='reservations'
    )
    reserved_by: Mapped["User"] = relationship(
        back_populates="reserved_wishes"
    )
