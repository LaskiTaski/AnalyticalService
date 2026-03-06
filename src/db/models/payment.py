"""Payment model — subscription payment history."""

from datetime import datetime

from sqlalchemy import BigInteger, DateTime, Float, ForeignKey, String, func
from sqlalchemy.orm import Mapped, mapped_column

from src.db.models.base import Base


class Payment(Base):
    __tablename__ = "payments"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )

    amount: Mapped[float] = mapped_column(Float, nullable=False, comment="Payment amount (RUB)")
    provider: Mapped[str] = mapped_column(String(50), default="yookassa", comment="Payment provider")
    status: Mapped[str] = mapped_column(String(20), default="pending", comment="pending/success/failed")
    payload: Mapped[str | None] = mapped_column(String(500), comment="Provider payload/receipt")

    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())

    def __repr__(self) -> str:
        return f"<Payment(user_id={self.user_id}, amount={self.amount}, status={self.status})>"
