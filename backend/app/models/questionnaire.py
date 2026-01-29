from datetime import datetime
from typing import Optional
from sqlalchemy import BigInteger, String, ForeignKey, Boolean, DateTime, func, Text
from sqlalchemy.orm import Mapped, mapped_column
from app.core.base import Base


class TagForm(Base):
    __tablename__ = 'tags_forms'

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    tag_value: Mapped[str] = mapped_column(String(255), nullable=False)
    type_tags: Mapped[bool] = mapped_column(Boolean, default=True)


class UserForm(Base):
    __tablename__ = 'user_forms'

    id: Mapped[int] = mapped_column(
        BigInteger,
        primary_key=True,
        autoincrement=True
    )
    user_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey("users.id", ondelete="CASCADE"))
    tag: Mapped[str] = mapped_column(String(255), nullable=False)
    detail: Mapped[Optional[str]] = mapped_column(String(1000), nullable=True)
    type_tag: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        server_default=func.now(),
        onupdate=func.now()
    )
