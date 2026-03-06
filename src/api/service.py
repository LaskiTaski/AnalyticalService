"""Bond service — filtering, sorting, pagination logic."""

import math

from sqlalchemy import Select, desc, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.db.models.bond import Bond
from src.api.schemas import BondFilterParams, BondListResponse, BondResponse, MarketOverview


def _apply_filters(query: Select, params: BondFilterParams) -> Select:
    """Apply filter conditions to a SELECT query."""

    # Price
    if params.price_min is not None:
        query = query.where(Bond.prev_price >= params.price_min)
    if params.price_max is not None:
        query = query.where(Bond.prev_price <= params.price_max)

    # Yield
    if params.yield_min is not None:
        query = query.where(Bond.yield_at_prev_wa_price >= params.yield_min)
    if params.yield_max is not None:
        query = query.where(Bond.yield_at_prev_wa_price <= params.yield_max)

    # Coupon
    if params.coupon_min is not None:
        query = query.where(Bond.coupon_percent >= params.coupon_min)
    if params.coupon_max is not None:
        query = query.where(Bond.coupon_percent <= params.coupon_max)
    if params.coupon_frequency is not None:
        query = query.where(Bond.coupon_frequency == params.coupon_frequency)

    # Maturity
    if params.days_min is not None:
        query = query.where(Bond.days_to_maturity >= params.days_min)
    if params.days_max is not None:
        query = query.where(Bond.days_to_maturity <= params.days_max)

    # Classification
    if params.qualified is not None and not params.qualified:
        query = query.where(Bond.qualified_only == False)  # noqa: E712
    if params.list_level_max is not None:
        query = query.where(Bond.list_level <= params.list_level_max)
    if params.security_type is not None:
        query = query.where(Bond.security_type == params.security_type)
    if params.board_id is not None:
        query = query.where(Bond.board_id == params.board_id)

    return query


def _apply_sorting(query: Select, params: BondFilterParams) -> Select:
    """Apply sorting to a SELECT query."""
    # Validate sort_by against actual Bond columns
    allowed_sort = {
        "secid", "prev_price", "yield_at_prev_wa_price", "coupon_percent",
        "coupon_value", "days_to_maturity", "mat_date", "duration",
        "volume_today", "face_value", "list_level", "updated_at",
    }

    sort_field = params.sort_by if params.sort_by in allowed_sort else "yield_at_prev_wa_price"
    column = getattr(Bond, sort_field)

    if params.sort_order == "desc":
        query = query.order_by(desc(column).nulls_last())
    else:
        query = query.order_by(column.nulls_last())

    return query


async def get_bonds(
    session: AsyncSession,
    params: BondFilterParams,
) -> BondListResponse:
    """Get filtered, sorted, paginated list of bonds."""

    # Count query
    count_query = select(func.count(Bond.id))
    count_query = _apply_filters(count_query, params)
    total = (await session.execute(count_query)).scalar() or 0

    # Data query
    query = select(Bond)
    query = _apply_filters(query, params)
    query = _apply_sorting(query, params)

    # Pagination
    offset = (params.page - 1) * params.per_page
    query = query.offset(offset).limit(params.per_page)

    result = await session.execute(query)
    bonds = result.scalars().all()

    pages = math.ceil(total / params.per_page) if params.per_page > 0 else 0

    return BondListResponse(
        items=[BondResponse.model_validate(b) for b in bonds],
        total=total,
        page=params.page,
        per_page=params.per_page,
        pages=pages,
    )


async def get_bond_by_secid(session: AsyncSession, secid: str) -> Bond | None:
    """Get a single bond by SECID."""
    result = await session.execute(select(Bond).where(Bond.secid == secid))
    return result.scalar_one_or_none()


async def get_market_overview(session: AsyncSession) -> MarketOverview:
    """Get aggregated market statistics."""

    # Total count
    total = (await session.execute(select(func.count(Bond.id)))).scalar() or 0

    # Count by type
    type_query = select(Bond.security_type, func.count(Bond.id)).group_by(Bond.security_type)
    type_result = await session.execute(type_query)
    by_type = {row[0] or "unknown": row[1] for row in type_result.all()}

    # Count by board
    board_query = select(Bond.board_id, func.count(Bond.id)).group_by(Bond.board_id)
    board_result = await session.execute(board_query)
    by_board = {row[0] or "unknown": row[1] for row in board_result.all()}

    # Averages
    avg_query = select(
        func.avg(Bond.yield_at_prev_wa_price),
        func.avg(Bond.coupon_percent),
        func.avg(Bond.duration),
        func.max(Bond.updated_at),
    )
    avg_result = (await session.execute(avg_query)).one()

    return MarketOverview(
        total_bonds=total,
        by_type=by_type,
        by_board=by_board,
        avg_yield=round(avg_result[0], 2) if avg_result[0] else None,
        avg_coupon=round(avg_result[1], 2) if avg_result[1] else None,
        avg_duration=round(avg_result[2], 2) if avg_result[2] else None,
        last_updated=avg_result[3],
    )
