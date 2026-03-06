"""UserFilter model — bond screening preferences per user."""

from sqlalchemy import BigInteger, Boolean, Float, ForeignKey, Integer
from sqlalchemy.orm import Mapped, mapped_column

from src.db.models.base import Base


class UserFilter(Base):
    __tablename__ = "user_filters"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("users.id", ondelete="CASCADE"), unique=True, nullable=False
    )

    # --- Price filters ---
    price_min: Mapped[float | None] = mapped_column(Float, comment="Min bond price (%)")
    price_max: Mapped[float | None] = mapped_column(Float, comment="Max bond price (%)")

    # --- Yield filters ---
    yield_min: Mapped[float | None] = mapped_column(Float, comment="Min yield to maturity (%)")
    yield_max: Mapped[float | None] = mapped_column(Float, comment="Max yield to maturity (%)")

    # --- Coupon filters ---
    coupon_min: Mapped[float | None] = mapped_column(Float, comment="Min coupon rate (%)")
    coupon_max: Mapped[float | None] = mapped_column(Float, comment="Max coupon rate (%)")
    coupon_frequency: Mapped[int | None] = mapped_column(Integer, comment="Exact coupons per year")

    # --- Maturity filters ---
    days_min: Mapped[int | None] = mapped_column(Integer, comment="Min days to maturity")
    days_max: Mapped[int | None] = mapped_column(Integer, comment="Max days to maturity")

    # --- Classification ---
    qualified_ok: Mapped[bool] = mapped_column(Boolean, default=False, comment="Include qualified-only bonds")
    list_level_max: Mapped[int | None] = mapped_column(Integer, comment="Max listing level (1=best)")

    def __repr__(self) -> str:
        return f"<UserFilter(user_id={self.user_id})>"
