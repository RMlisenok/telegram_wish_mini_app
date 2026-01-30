from sqlalchemy import BigInteger, Boolean, ForeignKey, DateTime, func
from sqlalchemy.orm import Mapped, mapped_column
from app.core.base import Base
from datetime import datetime


class NotificationSettings(Base):
    __tablename__ = 'notification_settings'

    id: Mapped[int] = mapped_column(
        BigInteger,
        primary_key=True,
        autoincrement=True
    )
    user_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey("users.id", ondelete="CASCADE"),
        unique=True
    )

    new_followers: Mapped[bool] = mapped_column(Boolean, default=False)
    access_requests: Mapped[bool] = mapped_column(Boolean, default=False)
    birt_after: Mapped[bool] = mapped_column(Boolean, default=False)
    birt_before: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        server_default=func.now(),
        onupdate=func.now()
    )
