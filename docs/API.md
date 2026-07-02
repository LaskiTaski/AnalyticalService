# API Документация

Base URL: `http://localhost:8000`
Swagger UI: `http://localhost:8000/docs`

## Эндпоинты

### GET /api/v1/bonds

Фильтрация облигаций с пагинацией.

**Query Parameters:**

| Параметр | Тип | По умолчанию | Описание |
|----------|-----|-------------|----------|
| page | int | 1 | Номер страницы (≥1) |
| per_page | int | 20 | Записей на странице (1-100) |
| price_min | float | — | Мин. цена (% от номинала) |
| price_max | float | — | Макс. цена |
| yield_min | float | — | Мин. доходность к погашению (%) |
| yield_max | float | — | Макс. доходность |
| coupon_min | float | — | Мин. ставка купона (%) |
| coupon_max | float | — | Макс. ставка купона |
| coupon_frequency | int | — | Частота купона (раз/год) |
| days_min | int | — | Мин. дней до погашения |
| days_max | int | — | Макс. дней до погашения |
| qualified | bool | — | false = только неквал., true = все |
| list_level_max | int | — | Макс. уровень листинга (1-3) |
| security_type | string | — | ofz / corp / muni |
| board_id | string | — | TQCB / TQOB / TQIR |
| sort_by | string | yield_at_prev_wa_price | Поле сортировки |
| sort_order | string | desc | asc / desc |

**Допустимые sort_by:** secid, prev_price, yield_at_prev_wa_price, coupon_percent, coupon_value, days_to_maturity, mat_date, duration, volume_today, face_value, list_level, updated_at

**Response (200):**
```json
{
  "items": [
    {
      "id": 1,
      "secid": "RU000A10A9Z1",
      "isin": "RU000A10A9Z1",
      "short_name": "Магнит4P05",
      "full_name": "Магнит ПАО БО-004P-05",
      "board_id": "TQCB",
      "prev_price": 98.92,
      "face_value": 1000.0,
      "accrued_int": 7.625,
      "lot_size": 1,
      "yield_at_prev_wa_price": 16.85,
      "coupon_percent": 12.5,
      "coupon_value": 38.01,
      "coupon_period": 182,
      "coupon_frequency": 2,
      "mat_date": "2027-06-29",
      "offer_date": null,
      "days_to_maturity": 480,
      "list_level": 1,
      "qualified_only": false,
      "security_type": "corp",
      "duration": 420.5,
      "volume_today": 15000000.0,
      "updated_at": "2026-03-06T16:29:10"
    }
  ],
  "total": 571,
  "page": 1,
  "per_page": 20,
  "pages": 29
}
```

### GET /api/v1/bonds/{secid}

Детальная информация по одной облигации.

**Response (200):** Один объект Bond (как в items выше).
**Response (404):** `{"detail": "Облигация {secid} не найдена"}`

### GET /api/v1/stats/market-overview

Агрегированная статистика рынка.

**Response (200):**
```json
{
  "total_bonds": 2961,
  "by_type": {
    "corp": 2498,
    "ofz": 67,
    "muni": 396
  },
  "by_board": {
    "TQCB": 2498,
    "TQOB": 67,
    "TQIR": 396
  },
  "avg_yield": 14.52,
  "avg_coupon": 11.38,
  "avg_duration": 845.2,
  "last_updated": "2026-03-06T16:29:10"
}
```

### GET /health

Health check.

**Response (200):** `{"status": "ok"}`

## Модель данных Bond

| Поле | Тип | Описание |
|------|-----|----------|
| id | int | Первичный ключ (auto) |
| secid | string | Код бумаги (уникальный) |
| isin | string? | Международный код |
| short_name | string? | Короткое название |
| full_name | string? | Полное название |
| board_id | string? | Борд MOEX (TQCB/TQOB/TQIR) |
| prev_price | float? | Цена закрытия (% от номинала) |
| face_value | float? | Номинал (руб.) |
| accrued_int | float? | НКД (руб.) |
| lot_size | int? | Размер лота |
| yield_at_prev_wa_price | float? | Доходность к погашению (%) |
| coupon_percent | float? | Ставка купона (%) |
| coupon_value | float? | Размер купона (руб.) |
| coupon_period | int? | Период купона (дней) |
| coupon_frequency | int? | Купонов в год (расчётное) |
| mat_date | date? | Дата погашения |
| offer_date | date? | Дата оферты |
| days_to_maturity | int? | Дней до погашения (расчётное) |
| list_level | int? | Уровень листинга (1/2/3) |
| qualified_only | bool? | Только для квал. инвесторов |
| security_type | string? | Тип: ofz / corp / muni |
| duration | float? | Дюрация |
| volume_today | float? | Объём торгов за день (руб.) |
| updated_at | datetime | Время последнего обновления |
