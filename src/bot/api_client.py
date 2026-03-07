"""HTTP client for the FastAPI backend.

The bot communicates with the database ONLY through the API layer,
never directly. This allows scaling bot and API independently.
"""

from typing import Any

import httpx
import structlog

from src.core.config import settings

logger = structlog.get_logger()


def _api_base() -> str:
    return f"http://localhost:{settings.api_port}"


async def fetch_bonds(params: dict[str, Any]) -> dict:
    """GET /api/v1/bonds with filter parameters.

    Returns parsed JSON response with items, total, page, pages.
    """
    # Remove None values
    clean_params = {k: v for k, v in params.items() if v is not None}

    async with httpx.AsyncClient(timeout=15) as client:
        resp = await client.get(f"{_api_base()}/api/v1/bonds", params=clean_params)
        resp.raise_for_status()
        return resp.json()


async def fetch_bond(secid: str) -> dict | None:
    """GET /api/v1/bonds/{secid}.

    Returns bond dict or None if not found.
    """
    async with httpx.AsyncClient(timeout=10) as client:
        resp = await client.get(f"{_api_base()}/api/v1/bonds/{secid}")
        if resp.status_code == 404:
            return None
        resp.raise_for_status()
        return resp.json()


async def fetch_market_overview() -> dict:
    """GET /api/v1/stats/market-overview."""
    async with httpx.AsyncClient(timeout=10) as client:
        resp = await client.get(f"{_api_base()}/api/v1/stats/market-overview")
        resp.raise_for_status()
        return resp.json()
