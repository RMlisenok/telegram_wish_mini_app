from typing import Optional, List
from sqlalchemy import BigInteger, String, ForeignKey, Boolean, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.core.base import Base
from app.models.user import User


class TagForm(Base):
    __tablename__ = 'tags_forms'

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    tag_value: Mapped[str] = mapped_column(String(255), nullable=False)
    # True для интересов, False для ограничений (FS-10.4)
    type_tags: Mapped[bool] = mapped_column(Boolean, default=True)

    user_forms: Mapped[List["UserForm"]] = relationship("UserForm", back_populates="tag_ref")


class UserForm(Base):
    __tablename__ = 'user_forms'

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    user_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("users.id", ondelete="CASCADE"))
    tag_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("tags_forms.id"))
    detail: Mapped[Optional[str]] = mapped_column(String(1000), nullable=True)

    owner: Mapped["User"] = relationship("User")
    tag_ref: Mapped["TagForm"] = relationship("TagForm", back_populates="user_forms")