from typing import Optional, List
from sqlalchemy import String, Enum, Text, TIMESTAMP, BigInteger, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import Mapped, mapped_column, relationship
import enum

from app.core.base import Base


class TypePrivacyEnum(enum.Enum):
    public = 'public'
    private = 'private'
    protected = 'protected'


class Wishlist(Base):
    __tablename__ = 'wishlists'

    id: Mapped[int] = mapped_column(
        primary_key=True
    )
    user_id = Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey('users.id'),
        nullable=False
    )
    name: Mapped[str] = mapped_column(
        String(50),
        nullable=False
    )
    description: Mapped[str] = mapped_column(
        String(250),
        nullable=True
    )
    photo: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True
    )
    typeprivacy: Mapped[TypePrivacyEnum] = mapped_column(
        Enum(TypePrivacyEnum),
        default=TypePrivacyEnum.public
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

    owner: Mapped['User'] = relationship(
        back_populates='wishlists'
    )
    wishes: Mapped[List['WishWishlist']] = relationship(
        back_populates='wishlists',
        cascade='all, delete-orphan'
    )
