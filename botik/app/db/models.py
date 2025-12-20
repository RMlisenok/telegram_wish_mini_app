from sqlalchemy import (
    Column,
    Integer,
    BigInteger,
    String,
    Date,
    DateTime,
    ForeignKey,
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.sql import func

from app.db.database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    telegram_id = Column(BigInteger, unique=True, nullable=False)
    name = Column(String(255))
    birthday = Column(Date)
    created_at = Column(DateTime, server_default=func.now())


class NotificationSettings(Base):
    __tablename__ = "notification_settings"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True)
    birthday_reminders = Column(Integer, default=1)
    new_followers = Column(Integer, default=1)
    post_birthday = Column(Integer, default=1)
    access_requests = Column(Integer, default=1)


class RecommendationCache(Base):
    __tablename__ = "recommendation_cache"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    tag = Column(String, nullable=False)
    payload = Column(JSONB, nullable=False)
    created_at = Column(DateTime, server_default=func.now())
