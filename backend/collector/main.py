"""MOEX Data Collector — main entry point.

Replaces the old SmartLab scraper. Fetches bond data from MOEX ISS API
and upserts into PostgreSQL.

Usage:
    python -m backend.collector.main           # single run
    python -m backend.collector.main --loop    # continuous loop
"""

import asyncio
import sys
import time

import structlog

from backend.core.config import settings
from backend.core.logging import setup_logging
from backend.db.session import async_session
from backend.collector.moex_client import fetch_all_bonds
from backend.collector.repository import upsert_bonds, get_bond_count
from backend.collector.issuer_enricher import enrich_missing_inns, snapshot_listing_changes

logger = structlog.get_logger()


async def run_collection() -> int:
    """Run a single collection cycle.

    Returns:
        Number of bonds processed.
    """
    start_time = time.monotonic()

    logger.info("collection_started", boards=settings.collector_boards)

    # 1. Fetch from MOEX ISS API
    bonds_data = await fetch_all_bonds(settings.collector_boards)

    if not bonds_data:
        logger.warning("no_bonds_fetched")
        return 0

    async with async_session() as session:
        # 2. Риск-сигналы: зафиксировать смену уровня листинга ДО upsert'а,
        # пока в БД лежат прошлые значения list_level
        await snapshot_listing_changes(session, bonds_data)

        # 3. Upsert into PostgreSQL
        count = await upsert_bonds(session, bonds_data)
        total = await get_bond_count(session)

        # 4. Риск-сигналы: добрать ИНН эмитентов для новых бумаг (батчами)
        await enrich_missing_inns(session)

    elapsed = time.monotonic() - start_time

    logger.info(
        "collection_completed",
        processed=count,
        total_in_db=total,
        elapsed_seconds=round(elapsed, 2),
    )

    return count


async def run_loop() -> None:
    """Run collector in a continuous loop with configurable interval."""
    interval = settings.collector_interval_seconds
    logger.info("collector_loop_started", interval_seconds=interval)

    while True:
        try:
            await run_collection()
        except Exception:
            logger.exception("collection_cycle_failed")

        logger.debug("sleeping", seconds=interval)
        await asyncio.sleep(interval)


async def main() -> None:
    """Entry point — single run or loop based on CLI args."""
    setup_logging()

    if "--loop" in sys.argv:
        await run_loop()
    else:
        count = await run_collection()
        if count == 0:
            logger.error("no_data_collected")
            sys.exit(1)
        logger.info("single_run_done", bonds=count)


if __name__ == "__main__":
    asyncio.run(main())
