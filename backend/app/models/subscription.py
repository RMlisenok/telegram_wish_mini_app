from typing import Optional
from sqlalchemy import Boolean, TIMESTAMP, BigInteger, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.base import Base


class Subscription(Base):
    __tablename__ = "subscriptions"

    id: Mapped[int] = mapped_column(
        BigInteger,
        primary_key=True
    )

    subscriber_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )

    type_sub: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=True  # To subscribe to a user
    )
    target_user_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=True,
        index=True
    )
    target_wishlist_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey("wishlists.id", ondelete="CASCADE"),
        nullable=True,
        index=True
    )
    created_at: Mapped[TIMESTAMP] = mapped_column(
        TIMESTAMP,
        server_default=func.now()
    )

    subscriber: Mapped[Optional["User"]] = relationship(
        "User",
        foreign_keys=[subscriber_id],
        back_populates="my_subscriptions"
    )
    target_user: Mapped[Optional["User"]] = relationship(
        "User",
        foreign_keys=[target_user_id],
        back_populates="subscribers_to_me"
    )
    target_wishlist: Mapped[Optional["Wishlist"]] = relationship(
        "Wishlist",
        foreign_keys=[target_wishlist_id],
        back_populates="subscribers"
    )
