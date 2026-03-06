"""MOEX Data Collector — main entry point.

Replaces the old SmartLab scraper. Fetches bond data from MOEX ISS API
and upserts into PostgreSQL.

Usage:
    python -m src.collector.main           # single run
    python -m src.collector.main --loop    # continuous loop
"""

import asyncio
import sys
import time

import structlog

from src.core.config import settings
from src.core.logging import setup_logging
from src.db.session import async_session
from src.collector.moex_client import fetch_all_bonds
from src.collector.repository import upsert_bonds, get_bond_count

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

    # 2. Upsert into PostgreSQL
    async with async_session() as session:
        count = await upsert_bonds(session, bonds_data)
        total = await get_bond_count(session)

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
