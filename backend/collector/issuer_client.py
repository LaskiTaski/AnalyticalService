"""MOEX ISS: описание бумаги → данные эмитента (ИНН, ОКПО и т.д.).

Эндпоинт: /iss/securities/{secid}.json?iss.meta=off&iss.only=description
Блок description — пары name/title/value, среди которых для облигаций
есть INN эмитента (а также OKPO, REGNUMBER и др.).

Запросы идут по одному на бумагу, поэтому обогащение выполняется батчами
с паузой между запросами (см. settings.issuer_enrich_*), чтобы не
нагружать ISS: ~3000 бумаг размажутся на несколько циклов коллектора.
"""

import asyncio
import re

import aiohttp
import structlog

from backend.collector.moex_client import ISS_BASE

logger = structlog.get_logger()

DESCRIPTION_URL = (
    ISS_BASE + "/securities/{secid}.json"
    "?iss.meta=off&iss.only=description&description.columns=name,value"
)

# Валидация ИНН юрлица (10 цифр) или ИП (12 цифр) — MOEX иногда отдаёт мусор/пустоту
_INN_RE = re.compile(r"^\d{10}(\d{2})?$")

# Хвосты серий выпусков, отрезаемые при выводе имени эмитента из имени бумаги.
# Это эвристика этапа 1: каноническое имя появится на этапе 2 из пресс-релизов агентств.
_SERIES_TAIL_RE = re.compile(
    r"\s+(БО|Б0|BO|об|обл|выпуск|сери[ия]|ПБО|КО|001Р|002Р|00\dP|ИОС)[-\s.].*$",
    re.IGNORECASE,
)


def parse_description(payload: dict) -> dict[str, str]:
    """Разобрать блок description в плоский dict {NAME: value}."""
    block = payload.get("description") or {}
    columns: list[str] = block.get("columns") or []
    data: list[list] = block.get("data") or []
    try:
        name_i, value_i = columns.index("name"), columns.index("value")
    except ValueError:
        return {}
    return {
        str(row[name_i]).upper(): str(row[value_i])
        for row in data
        if row[name_i] is not None and row[value_i] is not None
    }


def extract_issuer_fields(description: dict[str, str]) -> dict | None:
    """Достать поля эмитента из описания. None, если валидного ИНН нет
    (например, для ОФЗ эмитент — Минфин без ИНН в ISS)."""
    inn = (description.get("INN") or "").strip()
    if not _INN_RE.match(inn):
        return None
    return {
        "inn": inn,
        "okpo": (description.get("OKPO") or "").strip() or None,
        # ОГРН в ISS description не отдаётся; появится из других источников (этапы 2-4)
        "ogrn": None,
    }


def derive_issuer_name(bond_full_name: str | None, bond_short_name: str | None) -> str | None:
    """Эвристика имени эмитента из имени бумаги: отрезаем хвост серии выпуска.

    'Сегежа Групп ПАО БО-002P 01R' → 'Сегежа Групп ПАО'. Не идеально, но лучше
    пустоты в UI; будет заменено каноническим именем на этапе 2.
    """
    base = bond_full_name or bond_short_name
    if not base:
        return None
    name = _SERIES_TAIL_RE.sub("", base).strip(" -–—")
    return name or base


async def fetch_issuer_for_secid(
    session: aiohttp.ClientSession, secid: str
) -> dict | None:
    """Получить данные эмитента для бумаги. None = ИНН недоступен или ошибка."""
    url = DESCRIPTION_URL.format(secid=secid)
    try:
        async with session.get(url, timeout=aiohttp.ClientTimeout(total=15)) as resp:
            if resp.status != 200:
                logger.warning("issuer_description_http_error", secid=secid, status=resp.status)
                return None
            payload = await resp.json()
    except (aiohttp.ClientError, asyncio.TimeoutError) as exc:
        logger.warning("issuer_description_fetch_failed", secid=secid, error=str(exc))
        return None

    description = parse_description(payload)
    return extract_issuer_fields(description)
