"""Pydantic schemas for bonds API."""

from datetime import date, datetime

from pydantic import BaseModel, Field


# ── Response schemas ────────────────────────────────────────────

class BondResponse(BaseModel):
    """Single bond in API responses."""

    id: int
    secid: str
    isin: str | None = None
    short_name: str | None = None
    full_name: str | None = None
    board_id: str | None = None

    # Price
    prev_price: float | None = None
    face_value: float | None = None
    accrued_int: float | None = None
    lot_size: int | None = None

    # Yield
    yield_at_prev_wa_price: float | None = None
    coupon_percent: float | None = None
    coupon_value: float | None = None
    coupon_period: int | None = None
    coupon_frequency: int | None = None

    # Dates
    mat_date: date | None = None
    offer_date: date | None = None
    days_to_maturity: int | None = None

    # Classification
    list_level: int | None = None
    qualified_only: bool | None = None
    security_type: str | None = None

    # Trading
    duration: float | None = None
    volume_today: float | None = None

    updated_at: datetime

    model_config = {"from_attributes": True}


class BondListResponse(BaseModel):
    """Paginated list of bonds."""

    items: list[BondResponse]
    total: int
    page: int
    per_page: int
    pages: int


# ── Filter/query schemas ───────────────────────────────────────

class BondFilterParams(BaseModel):
    """Query parameters for bond filtering."""

    # Pagination
    page: int = Field(default=1, ge=1, description="Page number")
    per_page: int = Field(default=20, ge=1, le=100, description="Items per page")

    # Price filters
    price_min: float | None = Field(default=None, description="Min price (% of face)")
    price_max: float | None = Field(default=None, description="Max price (% of face)")

    # Yield filters
    yield_min: float | None = Field(default=None, description="Min yield to maturity (%)")
    yield_max: float | None = Field(default=None, description="Max yield to maturity (%)")

    # Coupon filters
    coupon_min: float | None = Field(default=None, description="Min coupon rate (%)")
    coupon_max: float | None = Field(default=None, description="Max coupon rate (%)")
    coupon_frequency: int | None = Field(default=None, description="Exact coupons per year")

    # Maturity filters
    days_min: int | None = Field(default=None, ge=0, description="Min days to maturity")
    days_max: int | None = Field(default=None, ge=0, description="Max days to maturity")

    # Classification
    qualified: bool | None = Field(default=None, description="Include qualified-only bonds")
    list_level_max: int | None = Field(default=None, ge=1, le=3, description="Max listing level")
    security_type: str | None = Field(default=None, description="Bond type: ofz, corp, muni")
    board_id: str | None = Field(default=None, description="Board: TQCB, TQOB, TQIR")

    # Sorting
    sort_by: str = Field(default="yield_at_prev_wa_price", description="Sort field")
    sort_order: str = Field(default="desc", pattern="^(asc|desc)$", description="Sort direction")


# ── Market overview ────────────────────────────────────────────

class MarketOverview(BaseModel):
    """Aggregated market statistics."""

    total_bonds: int
    by_type: dict[str, int]
    by_board: dict[str, int]
    avg_yield: float | None
    avg_coupon: float | None
    avg_duration: float | None
    last_updated: datetime | None
