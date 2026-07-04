"""Bond API endpoints."""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from backend.db.session import get_session
from backend.api.schemas import (
    BondFilterParams,
    BondListResponse,
    BondResponse,
    IssuerEventsResponse,
    IssuerResponse,
    MarketOverview,
)
from backend.api.service import (
    get_bond_by_secid,
    get_bonds,
    get_issuer,
    get_issuer_events,
    get_market_overview,
)

router = APIRouter(prefix="/api/v1", tags=["bonds"])


@router.get("/bonds", response_model=BondListResponse)
async def list_bonds(
    # Pagination
    page: int = Query(1, ge=1, description="Номер страницы"),
    per_page: int = Query(20, ge=1, le=100, description="Записей на странице"),
    # Price
    price_min: float | None = Query(None, description="Мин. цена (% от номинала)"),
    price_max: float | None = Query(None, description="Макс. цена (% от номинала)"),
    # Yield
    yield_min: float | None = Query(None, description="Мин. доходность к погашению (%)"),
    yield_max: float | None = Query(None, description="Макс. доходность к погашению (%)"),
    # Coupon
    coupon_min: float | None = Query(None, description="Мин. ставка купона (%)"),
    coupon_max: float | None = Query(None, description="Макс. ставка купона (%)"),
    coupon_frequency: int | None = Query(None, description="Частота купона (раз в год)"),
    # Maturity
    days_min: int | None = Query(None, ge=0, description="Мин. дней до погашения"),
    days_max: int | None = Query(None, ge=0, description="Макс. дней до погашения"),
    # Classification
    qualified: bool | None = Query(None, description="Показывать бумаги для квал. инвесторов"),
    list_level_max: int | None = Query(None, ge=1, le=3, description="Макс. уровень листинга"),
    security_type: str | None = Query(None, description="Тип(ы) через запятую: ofz,corp,muni"),
    board_id: str | None = Query(None, description="Борд: TQCB, TQOB, TQIR"),
    search: str | None = Query(None, max_length=100, description="Поиск: название / SECID / ISIN"),
    # Risk signals
    risk_only: bool = Query(False, description="Только бумаги эмитентов с риск-сигналами"),
    # Sorting
    sort_by: str = Query("yield_at_prev_wa_price", description="Поле сортировки"),
    sort_order: str = Query("desc", pattern="^(asc|desc)$", description="Направление"),
    # DB session
    session: AsyncSession = Depends(get_session),
) -> BondListResponse:
    """Получить отфильтрованный список облигаций с пагинацией."""
    params = BondFilterParams(
        page=page, per_page=per_page,
        price_min=price_min, price_max=price_max,
        yield_min=yield_min, yield_max=yield_max,
        coupon_min=coupon_min, coupon_max=coupon_max,
        coupon_frequency=coupon_frequency,
        days_min=days_min, days_max=days_max,
        qualified=qualified, list_level_max=list_level_max,
        security_type=security_type, board_id=board_id,
        search=search,
        risk_only=risk_only,
        sort_by=sort_by, sort_order=sort_order,
    )
    return await get_bonds(session, params)


@router.get("/bonds/{secid}", response_model=BondResponse)
async def get_bond(
    secid: str,
    session: AsyncSession = Depends(get_session),
) -> BondResponse:
    """Получить данные по конкретной облигации (включая риск-агрегат эмитента)."""
    bond = await get_bond_by_secid(session, secid.upper())
    if not bond:
        raise HTTPException(status_code=404, detail=f"Облигация {secid} не найдена")
    return bond


@router.get("/issuers/{inn}", response_model=IssuerResponse, tags=["issuers"])
async def issuer_card(
    inn: str,
    session: AsyncSession = Depends(get_session),
) -> IssuerResponse:
    """Карточка эмитента: название, ИНН, число бумаг и риск-событий."""
    issuer = await get_issuer(session, inn)
    if not issuer:
        raise HTTPException(status_code=404, detail=f"Эмитент с ИНН {inn} не найден")
    return issuer


@router.get("/issuers/{inn}/events", response_model=IssuerEventsResponse, tags=["issuers"])
async def issuer_events(
    inn: str,
    session: AsyncSession = Depends(get_session),
) -> IssuerEventsResponse:
    """Лента риск-событий эмитента (новые сверху) со ссылками на первоисточники."""
    return await get_issuer_events(session, inn)


@router.get("/stats/market-overview", response_model=MarketOverview)
async def market_overview(
    session: AsyncSession = Depends(get_session),
) -> MarketOverview:
    """Обзор рынка облигаций: статистика, средние значения."""
    return await get_market_overview(session)
