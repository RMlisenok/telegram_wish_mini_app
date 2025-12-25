from typing import Optional, List
from sqlalchemy import (
    String,
    Date,
    Boolean,
    Enum,
    Text,
    TIMESTAMP,
    BigInteger,
    ForeignKey
) 
from sqlalchemy.sql import func
from sqlalchemy.orm import Mapped, mapped_column, relationship
import enum

from app.core.base import Base


class AccessRequestStatus(str, enum.Enum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"


class AccessRequest(Base):
    __tablename__ = 'access_requests'

    id: Mapped[int] = mapped_column(
        BigInteger,
        primary_key=True
    )
    wishlist_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey("wishlists.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    requester_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    status: Mapped[AccessRequestStatus] = mapped_column(
        Enum(AccessRequestStatus),
        default=AccessRequestStatus.PENDING,
        nullable=False
    )
    created_at: Mapped[TIMESTAMP] = mapped_column(
        TIMESTAMP,
        server_default=func.now()
    )
    processed_at: Mapped[Optional[TIMESTAMP]] = mapped_column(
        TIMESTAMP,
        nullable=True
    )

    wishlist: Mapped["Wishlist"] = relationship(
        "Wishlist",
        back_populates="access_requests"
    )
    requester: Mapped["User"] = relationship(
        "User",
        foreign_keys=[requester_id],
        back_populates="access_requests_made"
    )
