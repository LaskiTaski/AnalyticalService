"""MOEX ISS API client for bond data.

Docs: https://iss.moex.com/iss/reference/
All endpoints are public, no auth required.
"""

import asyncio
from datetime import date, datetime

import aiohttp
import structlog

logger = structlog.get_logger()

ISS_BASE = "https://iss.moex.com/iss"

# Columns we need from the 'securities' block
SECURITIES_COLUMNS = ",".join([
    "SECID",
    "SHORTNAME",
    "SECNAME",
    "ISIN",
    "PREVPRICE",
    "FACEVALUE",
    "ACCRUEDINT",
    "LOTSIZE",
    "COUPONPERCENT",
    "COUPONVALUE",
    "COUPONPERIOD",
    "MATDATE",
    "OFFERDATE",
    "LISTLEVEL",
    "SECTYPE",
    "BOARDID",
])

# Columns from the 'marketdata' block
MARKETDATA_COLUMNS = ",".join([
    "SECID",
    "YIELD",
    "DURATION",
    "VALTODAY",
])


def _parse_date(value: str | None) -> date | None:
    """Parse MOEX date string 'YYYY-MM-DD' to date object."""
    if not value:
        return None
    try:
        return datetime.strptime(value, "%Y-%m-%d").date()
    except (ValueError, TypeError):
        return None


def _safe_float(value) -> float | None:
    """Safely convert to float, return None for empty/invalid."""
    if value is None or value == "":
        return None
    try:
        return float(value)
    except (ValueError, TypeError):
        return None


def _safe_int(value) -> int | None:
    """Safely convert to int, return None for empty/invalid."""
    if value is None or value == "":
        return None
    try:
        return int(value)
    except (ValueError, TypeError):
        return None


def _classify_board(board_id: str) -> str:
    """Determine bond type from MOEX board ID."""
    board_map = {
        "TQOB": "ofz",
        "TQCB": "corp",
        "TQIR": "muni",
    }
    return board_map.get(board_id, "other")


def _calc_coupon_frequency(coupon_period: int | None) -> int | None:
    """Calculate coupons per year from coupon period in days."""
    if not coupon_period or coupon_period <= 0:
        return None
    return round(365 / coupon_period)


def _calc_days_to_maturity(mat_date: date | None) -> int | None:
    """Calculate days remaining until maturity."""
    if not mat_date:
        return None
    delta = mat_date - date.today()
    return max(0, delta.days)


def _is_qualified_only(list_level: int | None) -> bool | None:
    """Listing level 3 = qualified investors only."""
    if list_level is None:
        return None
    return list_level == 3


def _rows_to_dicts(columns: list[str], data: list[list]) -> list[dict]:
    """Convert MOEX ISS columnar format to list of dicts."""
    return [dict(zip(columns, row)) for row in data]


def _build_bond_dict(sec: dict, market: dict | None) -> dict:
    """Merge securities + marketdata into a flat dict matching Bond model fields."""
    mat_date = _parse_date(sec.get("MATDATE"))
    coupon_period = _safe_int(sec.get("COUPONPERIOD"))
    list_level = _safe_int(sec.get("LISTLEVEL"))

    return {
        "secid": sec["SECID"],
        "isin": sec.get("ISIN") or None,
        "short_name": sec.get("SHORTNAME") or None,
        "full_name": sec.get("SECNAME") or None,
        "board_id": sec.get("BOARDID") or None,
        # Price
        "prev_price": _safe_float(sec.get("PREVPRICE")),
        "face_value": _safe_float(sec.get("FACEVALUE")),
        "accrued_int": _safe_float(sec.get("ACCRUEDINT")),
        "lot_size": _safe_int(sec.get("LOTSIZE")),
        # Yield
        "yield_at_prev_wa_price": _safe_float(market.get("YIELD")) if market else None,
        "coupon_percent": _safe_float(sec.get("COUPONPERCENT")),
        "coupon_value": _safe_float(sec.get("COUPONVALUE")),
        "coupon_period": coupon_period,
        "coupon_frequency": _calc_coupon_frequency(coupon_period),
        # Dates
        "mat_date": mat_date,
        "offer_date": _parse_date(sec.get("OFFERDATE")),
        "days_to_maturity": _calc_days_to_maturity(mat_date),
        # Classification
        "list_level": list_level,
        "qualified_only": _is_qualified_only(list_level),
        "security_type": _classify_board(sec.get("BOARDID", "")),
        # Trading
        "duration": _safe_float(market.get("DURATION")) if market else None,
        "volume_today": _safe_float(market.get("VALTODAY")) if market else None,
    }


async def fetch_board_bonds(
    session: aiohttp.ClientSession,
    board: str,
) -> list[dict]:
    """Fetch ALL bonds from a single MOEX board.

    MOEX ISS board securities endpoint returns all rows at once
    (no pagination needed for per-board requests).

    Args:
        session: aiohttp session.
        board: Board ID (e.g. 'TQCB', 'TQOB', 'TQIR').

    Returns:
        List of dicts ready for Bond model upsert.
    """
    url = (
        f"{ISS_BASE}/engines/stock/markets/bonds/boards/{board}/securities.json"
        f"?iss.meta=off"
        f"&iss.only=securities,marketdata"
        f"&securities.columns={SECURITIES_COLUMNS}"
        f"&marketdata.columns={MARKETDATA_COLUMNS}"
    )

    try:
        async with session.get(url, timeout=aiohttp.ClientTimeout(total=60)) as resp:
            resp.raise_for_status()
            data = await resp.json(content_type=None)
    except Exception:
        logger.exception("moex_api_error", board=board)
        return []

    sec_block = data.get("securities", {})
    md_block = data.get("marketdata", {})

    sec_columns = sec_block.get("columns", [])
    sec_rows = sec_block.get("data", [])
    md_columns = md_block.get("columns", [])
    md_rows = md_block.get("data", [])

    securities = _rows_to_dicts(sec_columns, sec_rows)
    marketdata = _rows_to_dicts(md_columns, md_rows)

    # Index marketdata by SECID for O(1) lookup
    md_index: dict[str, dict] = {row["SECID"]: row for row in marketdata}

    # Merge securities + marketdata
    bonds = [
        _build_bond_dict(sec, md_index.get(sec["SECID"]))
        for sec in securities
    ]

    logger.info("board_fetched", board=board, bonds_count=len(bonds))
    return bonds


async def fetch_all_bonds(boards: list[str]) -> list[dict]:
    """Fetch bonds from all specified boards.

    Args:
        boards: List of board IDs, e.g. ['TQCB', 'TQOB', 'TQIR'].

    Returns:
        Combined list of bond dicts from all boards.
    """
    all_bonds: list[dict] = []

    async with aiohttp.ClientSession() as session:
        for board in boards:
            bonds = await fetch_board_bonds(session, board)
            all_bonds.extend(bonds)
            await asyncio.sleep(0.5)  # polite delay between boards

    logger.info("all_boards_fetched", boards=boards, total_bonds=len(all_bonds))
    return all_bonds