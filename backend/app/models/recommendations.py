from sqlalchemy import BigInteger, String, Text
from datetime import datetime
from sqlalchemy.orm import Mapped, mapped_column
from app.core.base import Base
from sqlalchemy import Column, Integer, BigInteger, DateTime, func
from app.core.db import Base

class GiftSuggestion(Base):
    __tablename__ = 'gift_suggestions'

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    url: Mapped[str] = mapped_column(String(1000), nullable=False)
    tag_value: Mapped[str] = mapped_column(String(255), nullable=False)
    category: Mapped[str] = mapped_column(String(100), nullable=False)

class RecommendationLog(Base):
    __tablename__ = "recommendation_logs"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(BigInteger, index=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now()
    )