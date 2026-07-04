"""Bond service — filtering, sorting, pagination logic."""

import math

from sqlalchemy import Select, desc, func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.db.models.bond import Bond
from backend.db.models.issuer import SEVERE_EVENT_TYPES, Issuer, IssuerEvent
from backend.api.schemas import (
    BondFilterParams,
    BondListResponse,
    BondResponse,
    IssuerEventResponse,
    IssuerEventsResponse,
    IssuerResponse,
    MarketOverview,
)


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
        # Comma-separated list is allowed: security_type=corp,muni
        types = [t.strip() for t in params.security_type.split(",") if t.strip()]
        if len(types) == 1:
            query = query.where(Bond.security_type == types[0])
        elif types:
            query = query.where(Bond.security_type.in_(types))
    if params.board_id is not None:
        query = query.where(Bond.board_id == params.board_id)

    # Search by name / SECID / ISIN (case-insensitive substring)
    if params.search:
        pattern = f"%{params.search.strip()}%"
        query = query.where(
            or_(
                Bond.short_name.ilike(pattern),
                Bond.full_name.ilike(pattern),
                Bond.secid.ilike(pattern),
                Bond.isin.ilike(pattern),
            )
        )

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


def _risk_agg_subquery():
    """Агрегат риск-событий по эмитенту: count + флаг «тяжёлых» событий.

    Один GROUP BY по issuer_events (индекс по inn), outerjoin к bonds —
    дёшево на наших объёмах (~3000 бумаг).
    """
    severe = [t.value for t in SEVERE_EVENT_TYPES]
    return (
        select(
            IssuerEvent.inn.label("inn"),
            func.count(IssuerEvent.id).label("risk_events_count"),
            func.bool_or(IssuerEvent.type.in_(severe)).label("has_severe_events"),
        )
        .group_by(IssuerEvent.inn)
        .subquery()
    )


def _bond_to_response(bond: Bond, risk_count: int | None, severe: bool | None) -> BondResponse:
    resp = BondResponse.model_validate(bond)
    resp.risk_events_count = int(risk_count or 0)
    resp.has_severe_events = bool(severe)
    return resp


async def get_bonds(
    session: AsyncSession,
    params: BondFilterParams,
) -> BondListResponse:
    """Get filtered, sorted, paginated list of bonds (+ риск-агрегат эмитента)."""
    risk = _risk_agg_subquery()

    # Count query
    count_query = select(func.count(Bond.id)).outerjoin(risk, Bond.issuer_inn == risk.c.inn)
    count_query = _apply_filters(count_query, params)
    if params.risk_only:
        count_query = count_query.where(risk.c.inn.is_not(None))
    total = (await session.execute(count_query)).scalar() or 0

    # Data query
    query = select(Bond, risk.c.risk_events_count, risk.c.has_severe_events).outerjoin(
        risk, Bond.issuer_inn == risk.c.inn
    )
    query = _apply_filters(query, params)
    if params.risk_only:
        query = query.where(risk.c.inn.is_not(None))
    query = _apply_sorting(query, params)

    # Pagination
    offset = (params.page - 1) * params.per_page
    query = query.offset(offset).limit(params.per_page)

    rows = (await session.execute(query)).all()

    pages = math.ceil(total / params.per_page) if params.per_page > 0 else 0

    return BondListResponse(
        items=[_bond_to_response(b, cnt, sev) for b, cnt, sev in rows],
        total=total,
        page=params.page,
        per_page=params.per_page,
        pages=pages,
    )


async def get_bond_by_secid(session: AsyncSession, secid: str) -> BondResponse | None:
    """Get a single bond by SECID (+ риск-агрегат эмитента)."""
    risk = _risk_agg_subquery()
    query = (
        select(Bond, risk.c.risk_events_count, risk.c.has_severe_events)
        .outerjoin(risk, Bond.issuer_inn == risk.c.inn)
        .where(Bond.secid == secid)
    )
    row = (await session.execute(query)).one_or_none()
    if row is None:
        return None
    bond, cnt, sev = row
    return _bond_to_response(bond, cnt, sev)


# ── Issuers (риск-сигналы) ─────────────────────────────────────

async def get_issuer(session: AsyncSession, inn: str) -> IssuerResponse | None:
    """Карточка эмитента с количеством бумаг и событий."""
    result = await session.execute(select(Issuer).where(Issuer.inn == inn))
    issuer = result.scalar_one_or_none()
    if issuer is None:
        return None

    bonds_count = (
        await session.execute(select(func.count(Bond.id)).where(Bond.issuer_inn == inn))
    ).scalar() or 0
    events_count = (
        await session.execute(
            select(func.count(IssuerEvent.id)).where(IssuerEvent.inn == inn)
        )
    ).scalar() or 0

    resp = IssuerResponse.model_validate(issuer)
    resp.bonds_count = bonds_count
    resp.events_count = events_count
    return resp


async def get_issuer_events(session: AsyncSession, inn: str) -> IssuerEventsResponse:
    """Лента риск-событий эмитента, новые сверху."""
    result = await session.execute(
        select(IssuerEvent)
        .where(IssuerEvent.inn == inn)
        .order_by(IssuerEvent.date.desc(), IssuerEvent.id.desc())
    )
    events = result.scalars().all()
    return IssuerEventsResponse(
        inn=inn,
        items=[IssuerEventResponse.model_validate(e) for e in events],
        total=len(events),
    )


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
