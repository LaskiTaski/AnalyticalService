"""Bond model — all bonds from MOEX ISS."""

from datetime import date, datetime

from sqlalchemy import BigInteger, Date, DateTime, Float, Index, Integer, String, func
from sqlalchemy.orm import Mapped, mapped_column

from src.db.models.base import Base


class Bond(Base):
    __tablename__ = "bonds"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)

    # --- Identifiers ---
    secid: Mapped[str] = mapped_column(String(50), unique=True, nullable=False, comment="Ticker code")
    isin: Mapped[str | None] = mapped_column(String(20), index=True, comment="ISIN code")
    short_name: Mapped[str | None] = mapped_column(String(200), comment="Short name")
    full_name: Mapped[str | None] = mapped_column(String(500), comment="Full name")
    board_id: Mapped[str | None] = mapped_column(String(20), index=True, comment="Board: TQCB, TQOB, TQIR")

    # --- Price ---
    prev_price: Mapped[float | None] = mapped_column(Float, comment="Last close price (% of face)")
    face_value: Mapped[float | None] = mapped_column(Float, comment="Nominal value (RUB)")
    accrued_int: Mapped[float | None] = mapped_column(Float, comment="Accrued coupon income (NKD)")
    lot_size: Mapped[int | None] = mapped_column(Integer, comment="Lot size")

    # --- Yield ---
    yield_at_prev_wa_price: Mapped[float | None] = mapped_column(Float, comment="Yield to maturity (%)")
    coupon_percent: Mapped[float | None] = mapped_column(Float, comment="Coupon rate (%)")
    coupon_value: Mapped[float | None] = mapped_column(Float, comment="Coupon payment (RUB)")
    coupon_period: Mapped[int | None] = mapped_column(Integer, comment="Coupon period (days)")
    coupon_frequency: Mapped[int | None] = mapped_column(Integer, comment="Coupons per year")

    # --- Dates ---
    mat_date: Mapped[date | None] = mapped_column(Date, index=True, comment="Maturity date")
    offer_date: Mapped[date | None] = mapped_column(Date, comment="Put/call offer date")
    days_to_maturity: Mapped[int | None] = mapped_column(Integer, comment="Days to maturity")

    # --- Classification ---
    list_level: Mapped[int | None] = mapped_column(Integer, comment="Listing level (1/2/3)")
    qualified_only: Mapped[bool | None] = mapped_column(comment="Qualified investors only")
    security_type: Mapped[str | None] = mapped_column(String(50), comment="Bond type: ofz, corp, muni")

    # --- Trading ---
    duration: Mapped[float | None] = mapped_column(Float, comment="Duration (days)")
    volume_today: Mapped[float | None] = mapped_column(Float, comment="Today trading volume (RUB)")

    # --- Meta ---
    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        server_default=func.now(),
        onupdate=func.now(),
        comment="Last data update",
    )

    __table_args__ = (
        Index("ix_bonds_yield", "yield_at_prev_wa_price"),
        Index("ix_bonds_coupon", "coupon_percent"),
        Index("ix_bonds_days", "days_to_maturity"),
        Index("ix_bonds_list_level", "list_level"),
    )

    def __repr__(self) -> str:
        return f"<Bond(secid={self.secid}, name={self.short_name})>"
