from typing import Optional
from sqlalchemy import String, Date, Boolean, Enum, Text, TIMESTAMP, BigInteger
from sqlalchemy.sql import func
from sqlalchemy.orm import Mapped, mapped_column
import enum

from app.core.base import Base


class ThemeEnum(enum.Enum):
    light = 'light'
    dark = 'dark'
    system = 'system'


class TextSizeEnum(enum.Enum):
    small = 'small'
    medium = 'medium'
    large = 'large'



class User(Base):
    __tablename__ = 'users'

    id: Mapped[int] = mapped_column(
        primary_key=True
    )
    telegram_id: Mapped[int] = mapped_column(
        BigInteger,
        nullable=False,
        unique=True,
        index=True
    )
    name: Mapped[str] = mapped_column(
        String(100),
        nullable=False
    )
    birth_date: Mapped[Date] = mapped_column(
        Date,
        nullable=True
    )
    photo: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True
    )
    theme: Mapped[ThemeEnum] = mapped_column(
        Enum(ThemeEnum),
        default=ThemeEnum.light
    )
    text_size: Mapped[TextSizeEnum] = mapped_column(
        Enum(TextSizeEnum),
        default=TextSizeEnum.medium
    )
    show_sub: Mapped[bool] = mapped_column(
        Boolean,
        default=False
    )
    created_at: Mapped[TIMESTAMP] = mapped_column(
        TIMESTAMP,
        server_default=func.now()
    )
    updated_at: Mapped[TIMESTAMP] = mapped_column(
        TIMESTAMP,
        server_default=func.now(),
        onupdate=func.now()
    )
