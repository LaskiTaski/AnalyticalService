"""Этап 1 риск-сигналов: обогащение bonds.issuer_inn и события смены листинга.

Две задачи, встроенные в цикл коллектора (см. backend/collector/main.py):

1. snapshot_listing_changes — ДО upsert'а сравнивает свежие данные MOEX
   с текущим состоянием БД и пишет issuer_events(listing_downgrade/upgrade)
   для бумаг, у которых уже известен эмитент.

2. enrich_missing_inns — ПОСЛЕ upsert'а батчами добирает ИНН для бумаг
   с issuer_inn IS NULL через /iss/securities/{secid} (по одному запросу
   на бумагу, с паузой; ~3000 бумаг обогащаются за несколько циклов).
"""

import asyncio
from datetime import date

import aiohttp
import structlog
from sqlalchemy import select
from sqlalchemy.dialects.postgresql import insert as pg_insert
from sqlalchemy.ext.asyncio import AsyncSession

from backend.core.config import settings
from backend.collector.issuer_client import derive_issuer_name, fetch_issuer_for_secid
from backend.db.models.bond import Bond
from backend.db.models.issuer import Issuer, IssuerEvent, IssuerEventType

logger = structlog.get_logger()


# ── События смены уровня листинга ───────────────────────────────

async def snapshot_listing_changes(session: AsyncSession, bonds_data: list[dict]) -> int:
    """Сравнить новые list_level с БД и записать события для известных эмитентов.

    Вызывать ДО upsert_bonds, пока в БД старые значения. Возвращает число событий.
    """
    result = await session.execute(
        select(Bond.secid, Bond.list_level, Bond.issuer_inn, Bond.short_name).where(
            Bond.issuer_inn.is_not(None)
        )
    )
    existing = {row.secid: row for row in result}
    if not existing:
        return 0

    today = date.today()
    events: list[dict] = []
    for bond in bonds_data:
        old = existing.get(bond["secid"])
        new_level = bond.get("list_level")
        if old is None or old.list_level is None or new_level is None:
            continue
        if new_level == old.list_level:
            continue
        downgrade = new_level > old.list_level  # уровень 1 лучше уровня 3
        events.append({
            "inn": old.issuer_inn,
            "type": (
                IssuerEventType.LISTING_DOWNGRADE if downgrade
                else IssuerEventType.LISTING_UPGRADE
            ).value,
            "date": today,
            "title": (
                f"{old.short_name or bond['secid']}: уровень листинга MOEX "
                f"{'понижен' if downgrade else 'повышен'} {old.list_level} → {new_level}"
            ),
            "url": f"https://www.moex.com/ru/issue.aspx?code={bond['secid']}",
            "source": "moex",
            "secid": bond["secid"],
        })

    if not events:
        return 0

    stmt = pg_insert(IssuerEvent).values(events).on_conflict_do_nothing(
        constraint="uq_issuer_event_fact"
    )
    result = await session.execute(stmt)
    await session.commit()
    inserted = result.rowcount or 0
    if inserted:
        logger.info("listing_events_recorded", count=inserted)
    return inserted


# ── Обогащение ИНН ──────────────────────────────────────────────

async def enrich_missing_inns(session: AsyncSession) -> int:
    """Добрать ИНН для бумаг без issuer_inn. Возвращает число обогащённых бумаг."""
    limit = settings.issuer_enrich_batch
    result = await session.execute(
        select(Bond.secid, Bond.full_name, Bond.short_name)
        .where(Bond.issuer_inn.is_(None))
        .order_by(Bond.id)
        .limit(limit)
    )
    pending = result.all()
    if not pending:
        return 0

    logger.info("issuer_enrichment_started", pending_batch=len(pending))

    enriched = 0
    async with aiohttp.ClientSession() as http:
        for row in pending:
            issuer_fields = await fetch_issuer_for_secid(http, row.secid)
            if issuer_fields:
                await _upsert_issuer_and_link(session, row, issuer_fields)
                enriched += 1
            await asyncio.sleep(settings.issuer_enrich_delay_seconds)

    await session.commit()
    logger.info("issuer_enrichment_completed", enriched=enriched, batch=len(pending))
    return enriched


async def _upsert_issuer_and_link(session: AsyncSession, bond_row, issuer_fields: dict) -> None:
    """Upsert эмитента (имя не затираем, если уже задано) и проставить FK у бумаги."""
    name_hint = derive_issuer_name(bond_row.full_name, bond_row.short_name)

    stmt = pg_insert(Issuer).values(
        inn=issuer_fields["inn"],
        name=name_hint,
        ogrn=issuer_fields.get("ogrn"),
        okpo=issuer_fields.get("okpo"),
    )
    # Обновляем только записи без имени: эвристика не должна перетирать
    # каноническое имя, которое появится из пресс-релизов агентств (этап 2)
    stmt = stmt.on_conflict_do_update(
        index_elements=["inn"],
        set_={"name": stmt.excluded.name, "okpo": stmt.excluded.okpo},
        where=Issuer.name.is_(None),
    )
    await session.execute(stmt)

    await session.execute(
        Bond.__table__.update()
        .where(Bond.secid == bond_row.secid)
        .values(issuer_inn=issuer_fields["inn"])
    )
