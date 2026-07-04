"""Seed the database with realistic demo bonds.

For offline development / demos when MOEX ISS is unreachable.
In production the collector (backend/collector) fills the same table
with live data — this script uses the exact same upsert path.

Usage:
    python -m scripts.seed_demo_data
"""

import asyncio
import random
from datetime import date, timedelta

import structlog

from backend.core.logging import setup_logging
from backend.db.session import async_session
from backend.collector.repository import upsert_bonds, get_bond_count

logger = structlog.get_logger()

rnd = random.Random(42)

TODAY = date.today()

CORP_ISSUERS = [
    "Магнит", "Сбер", "ГазпромК", "РЖД", "МТС", "Самолет", "Северсталь",
    "Европлан", "Сегежа", "Делимобиль", "ВУШ", "Селектел", "X5 Финанс",
    "КАМАЗ", "Аэрофлот", "Ростел", "АФК Система", "ПИК", "Балт.Лизинг",
    "ГТЛК", "ЕвроТранс", "Инарктика", "М.Видео", "Новотранс", "О'КЕЙ",
    "Позитив", "Роснано", "СТМ", "ТГК-14", "Уралкалий", "ХКФ Банк", "ЯТЭК",
]
MUNI_ISSUERS = [
    "Мос.Обл", "СПб Гор", "Новосиб", "Якутия", "Башкорт", "Краснояр",
    "Свердлов", "Томск.Обл",
]
OFZ_NUMBERS = [26207, 26212, 26218, 26221, 26224, 26228, 26230, 26233,
               26238, 26240, 26241, 26243, 26244, 26245, 26246, 26247,
               26248, 29014, 29016, 29020, 52002, 52003, 52004, 52005]


def _bond(secid: str, short_name: str, full_name: str, board: str, stype: str,
          *, price_base: float, price_spread: float, yield_base: float,
          yield_spread: float, coupon_base: float, coupon_spread: float,
          days_min: int, days_max: int, freq_choices: list[int],
          levels: list[int], vol_base: float, vol_spread: float) -> dict:
    days = rnd.randint(days_min, days_max)
    mat = TODAY + timedelta(days=days)
    coupon = round(coupon_base + rnd.random() * coupon_spread, 2)
    freq = rnd.choice(freq_choices)
    period = round(365 / freq)
    level = rnd.choice(levels)
    coupon_value = round((coupon / freq) * 10, 2)
    return {
        "secid": secid,
        "isin": secid if secid.startswith("RU") else f"RU000{secid[-7:]}",
        "short_name": short_name,
        "full_name": full_name,
        "board_id": board,
        "prev_price": round(price_base + rnd.random() * price_spread, 2),
        "face_value": 1000.0,
        "accrued_int": round(coupon_value * rnd.random(), 2),
        "lot_size": 1,
        "yield_at_prev_wa_price": round(
            yield_base + rnd.random() * yield_spread + (level - 1) * 1.5, 2
        ),
        "coupon_percent": coupon,
        "coupon_value": coupon_value,
        "coupon_period": period,
        "coupon_frequency": freq,
        "mat_date": mat,
        "offer_date": (TODAY + timedelta(days=rnd.randint(90, days))
                       if stype == "corp" and rnd.random() > 0.75 and days > 180
                       else None),
        "days_to_maturity": days,
        "list_level": level,
        "qualified_only": level == 3 and rnd.random() > 0.5,
        "security_type": stype,
        "duration": round(days * (0.6 + rnd.random() * 0.3), 1),
        "volume_today": round(vol_base + rnd.random() * vol_spread, 0),
    }


def make_bonds() -> list[dict]:
    bonds: list[dict] = []

    # ОФЗ (TQOB)
    for num in OFZ_NUMBERS:
        bonds.append(_bond(
            f"SU{num}RMFS", f"ОФЗ {num}",
            f"ОФЗ-ПД выпуск {num}", "TQOB", "ofz",
            price_base=64, price_spread=38, yield_base=12.3, yield_spread=3.4,
            coupon_base=6.5, coupon_spread=6, days_min=200, days_max=5500,
            freq_choices=[2], levels=[1], vol_base=8e7, vol_spread=9e8,
        ))

    # Корпоративные (TQCB) — несколько выпусков на эмитента
    seq = 0
    for issuer in CORP_ISSUERS:
        for _ in range(rnd.randint(2, 5)):
            seq += 1
            series = f"{rnd.randint(1, 4)}P{rnd.randint(1, 12):02d}"
            bonds.append(_bond(
                f"RU000A1{seq:04d}{rnd.choice('ZKMRWX')}{rnd.randint(1, 9)}",
                f"{issuer}{series}",
                f"{issuer} ПАО БО-00{series}", "TQCB", "corp",
                price_base=85, price_spread=21, yield_base=13, yield_spread=12,
                coupon_base=9.5, coupon_spread=11, days_min=60, days_max=2500,
                freq_choices=[2, 4, 12], levels=[1, 1, 2, 2, 3],
                vol_base=5e5, vol_spread=6e7,
            ))

    # Муниципальные (TQIR)
    for i, issuer in enumerate(MUNI_ISSUERS):
        for j in range(rnd.randint(1, 3)):
            bonds.append(_bond(
                f"RU000A0M{i}{j}X{i + 1}",
                f"{issuer}.{34010 + i * 3 + j}",
                f"{issuer} обл. {34010 + i * 3 + j}", "TQIR", "muni",
                price_base=89, price_spread=13, yield_base=13.5, yield_spread=4.2,
                coupon_base=8.5, coupon_spread=5.5, days_min=200, days_max=1900,
                freq_choices=[4], levels=[1, 2], vol_base=3e5, vol_spread=8e6,
            ))

    return bonds


async def seed_issuers_and_events(session) -> None:
    """Демо риск-сигналов: несколько эмитентов с ИНН и событиями,
    чтобы бейджи, фильтр risk_only и вкладка «Эмитент» были видны офлайн."""
    from sqlalchemy import select
    from sqlalchemy.dialects.postgresql import insert as pg_insert

    from backend.db.models.bond import Bond
    from backend.db.models.issuer import Issuer, IssuerEvent

    # Эмитенты с «историей»: (имя из CORP_ISSUERS, демо-ИНН, события)
    risky = {
        "Сегежа":     ("7704447429", ["listing_downgrade", "restructuring"]),
        "М.Видео":    ("7707602010", ["listing_downgrade"]),
        "Роснано":    ("7728131587", ["tech_default", "state_support_request"]),
        "ЯТЭК":       ("1435032049", ["default"]),
        "ТГК-14":     ("7534018889", ["listing_downgrade"]),
        "О'КЕЙ":      ("7826087713", ["offer"]),
    }
    # Остальным корпоратам — ИНН без событий (детерминированные фейковые)
    plain_inn = {name: f"77{i:02d}00{i:04d}" for i, name in enumerate(CORP_ISSUERS, 1)
                 if name not in risky}

    all_issuers = {**{n: (inn, evs) for n, (inn, evs) in risky.items()},
                   **{n: (inn, []) for n, inn in plain_inn.items()}}

    issuer_rows = [{"inn": inn, "name": f"{name} ПАО", "ogrn": None, "okpo": None}
                   for name, (inn, _) in all_issuers.items()]
    stmt = pg_insert(Issuer).values(issuer_rows).on_conflict_do_nothing(index_elements=["inn"])
    await session.execute(stmt)

    # Привязать бумаги к эмитентам по префиксу short_name
    result = await session.execute(select(Bond.secid, Bond.short_name).where(Bond.board_id == "TQCB"))
    for row in result:
        for name, (inn, _) in all_issuers.items():
            if row.short_name and row.short_name.startswith(name):
                await session.execute(
                    Bond.__table__.update().where(Bond.secid == row.secid).values(issuer_inn=inn)
                )
                break

    # События
    event_rows = []
    for name, (inn, types) in risky.items():
        for k, etype in enumerate(types):
            event_rows.append({
                "inn": inn, "type": etype,
                "date": TODAY - timedelta(days=30 * (k + 1) + hash(name) % 20),
                "title": f"{name}: демо-событие «{etype}» (сгенерировано seed-скриптом)",
                "url": None, "source": "moex", "secid": None,
            })
    stmt = pg_insert(IssuerEvent).values(event_rows).on_conflict_do_nothing(
        constraint="uq_issuer_event_fact"
    )
    await session.execute(stmt)
    await session.commit()
    logger.info("demo_issuers_seeded", issuers=len(issuer_rows), events=len(event_rows))


async def main() -> None:
    setup_logging()
    bonds = make_bonds()
    async with async_session() as session:
        count = await upsert_bonds(session, bonds)
        await seed_issuers_and_events(session)
        total = await get_bond_count(session)
    logger.info("demo_data_seeded", processed=count, total_in_db=total)


if __name__ == "__main__":
    asyncio.run(main())
