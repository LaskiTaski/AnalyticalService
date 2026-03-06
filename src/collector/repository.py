"""Repository for bulk upserting bonds into PostgreSQL."""

from datetime import datetime

from sqlalchemy import text
from sqlalchemy.dialects.postgresql import insert as pg_insert
from sqlalchemy.ext.asyncio import AsyncSession

import structlog

from src.db.models.bond import Bond

logger = structlog.get_logger()

# All Bond columns that come from MOEX data (exclude id, updated_at)
UPSERT_COLUMNS = [
    "secid", "isin", "short_name", "full_name", "board_id",
    "prev_price", "face_value", "accrued_int", "lot_size",
    "yield_at_prev_wa_price", "coupon_percent", "coupon_value",
    "coupon_period", "coupon_frequency",
    "mat_date", "offer_date", "days_to_maturity",
    "list_level", "qualified_only", "security_type",
    "duration", "volume_today",
]

# PostgreSQL has a limit of ~32767 parameters per query.
# Each bond has ~22 columns, so max ~1400 rows per batch.
BATCH_SIZE = 500


async def upsert_bonds(session: AsyncSession, bonds_data: list[dict]) -> int:
    """Bulk upsert bonds using PostgreSQL ON CONFLICT, in batches.

    Returns count of processed rows.
    """
    if not bonds_data:
        return 0

    total = 0

    for i in range(0, len(bonds_data), BATCH_SIZE):
        batch = bonds_data[i : i + BATCH_SIZE]

        stmt = pg_insert(Bond).values(batch)

        update_columns = {
            col: stmt.excluded[col] for col in UPSERT_COLUMNS if col != "secid"
        }
        update_columns["updated_at"] = datetime.utcnow()

        stmt = stmt.on_conflict_do_update(
            index_elements=["secid"],
            set_=update_columns,
        )

        await session.execute(stmt)
        total += len(batch)

        logger.debug("batch_upserted", batch_num=i // BATCH_SIZE + 1, rows=len(batch))

    await session.commit()

    logger.info("bonds_upserted", count=total)
    return total


async def get_bond_count(session: AsyncSession) -> int:
    """Get total number of bonds in the database."""
    result = await session.execute(text("SELECT COUNT(*) FROM bonds"))
    return result.scalar() or 0