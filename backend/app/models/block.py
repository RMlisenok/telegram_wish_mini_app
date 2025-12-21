from typing import Optional, List
from sqlalchemy import ForeignKey, TIMESTAMP, BigInteger
from sqlalchemy.sql import func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.core.base import Base


class BlockedUser(Base):
    __tablename__ = "blocked_user"

    id: Mapped[int] = mapped_column(primary_key=True)

    blocker_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False
    )

    blocked_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False
    )

    created_at: Mapped[TIMESTAMP] = mapped_column(
        TIMESTAMP,
        server_default=func.now()
    )

    blocker: Mapped["User"] = relationship(
        "User",
        foreign_keys=[blocker_id],
        back_populates="blocked_users"
    )
    blocked: Mapped["User"] = relationship(
        "User",
        foreign_keys=[blocked_id],
        back_populates="blocked_by_users"
    )
