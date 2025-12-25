from sqlalchemy import BigInteger, String, ForeignKey, Boolean
from sqlalchemy.orm import Mapped, mapped_column
from app.core.base import Base


class TagForm(Base):
    __tablename__ = 'tags_forms'

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    tag_value: Mapped[str] = mapped_column(String(255), nullable=False)
    type_tags: Mapped[bool] = mapped_column(Boolean, default=True)


class UserForm(Base):
    __tablename__ = 'user_forms'

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    user_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("users.id", ondelete="CASCADE"))
    tag: Mapped[str] = mapped_column(String(255), nullable=False)
    tag_id: Mapped[int | None] = mapped_column(BigInteger, ForeignKey("tags_forms.id"), nullable=True)

    detail: Mapped[str | None] = mapped_column(String(1000), nullable=True)
    is_interest: Mapped[bool] = mapped_column(Boolean, default=True)