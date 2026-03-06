"""User model — Telegram users."""

from datetime import datetime

from sqlalchemy import BigInteger, Boolean, DateTime, String, func
from sqlalchemy.orm import Mapped, mapped_column

from src.db.models.base import Base


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    telegram_id: Mapped[int] = mapped_column(BigInteger, unique=True, nullable=False, index=True)
    username: Mapped[str | None] = mapped_column(String(100))
    first_name: Mapped[str | None] = mapped_column(String(100))
    is_admin: Mapped[bool] = mapped_column(Boolean, default=False)
    is_qualified: Mapped[bool] = mapped_column(Boolean, default=False, comment="Qualified investor status")

    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    subscription_until: Mapped[datetime | None] = mapped_column(DateTime, comment="Subscription end date")

    def __repr__(self) -> str:
        return f"<User(tg_id={self.telegram_id}, name={self.first_name})>"

    @property
    def is_subscribed(self) -> bool:
        if self.is_admin:
            return True
        if self.subscription_until is None:
            return False
        return self.subscription_until > datetime.now()
