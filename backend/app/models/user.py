from typing import Optional, List, TYPE_CHECKING
from sqlalchemy import String, Date, Boolean, Enum, Text, TIMESTAMP
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship, Mapped, mapped_column
import enum

from app.core.base import Base

if TYPE_CHECKING:
    from .wishlist import Wishlist
    from .wish import Wish
    from .subscription import Subscription
    from .user_form import UserForm
    from .notification_settings import NotificationSettings
    from .wishreservation import WishReservation
    from .blockeduser import BlockedUser
    from .accessrequest import AccessRequest


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
        nullable=False
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

    # Relationship

    wishlists: Mapped[List['Wishlist']] = relationship(
        'Wishlist',
        back_populates='owner'
    )
    wishes: Mapped[List['Wish']] = relationship(
        'Wish',
        back_populates='owner'
    )
    subscriptions: Mapped[List['Subscription']] = relationship(
        'Subscription',
        foreign_keys='[Subscription.target_user_id]',
        back_populates='target_user'
    )
    blocked_users: Mapped[List['BlockedUser']] = relationship(
        'BlockedUser',
        foreign_keys='[BlockedUser.blocker_id]',
        back_populates='blocker'
    )
    blocked_by: Mapped[List['BlockedUser']] = relationship(
        'BlockedUser',
        foreign_keys='[BlockedUser.blocked_id]',
        back_populates='blocker'
    )
    access_requests_sent: Mapped[List['AccessRequest']] = relationship(
        'AccessRequest',
        foreign_keys='[AccessRequest.requester_id]',
        back_populates='requester'
    )
    access_requests_received: Mapped[List['AccessRequest']] = relationship(
        'AccessRequest',
        foreign_keys='[AccessRequest.wishlist_id]',
        back_populates='wishlist',
        viewonly=True
    )
    wish_reservations: Mapped[List['WishReservation']] = relationship(
        'WishReservation',
        foreign_keys='[WishReservation.reserved_id]'
    )
    wishlist_subscribers: Mapped[List['Subscription']] = relationship(
        'Subscription',
        foreign_keys='[Subscription.target_wihslist_id]',
        back_populates='target_wihslist_id',
        viewonly=True
    )
    questionnaire: Mapped['UserForm'] = relationship(
        'UserForm',
        back_populates='user'
    )
    notification_settings: Mapped['NotificationSettings'] = relationship(
        'NotificationSettings',
        back_populates='user',
        uselist=False
    )
