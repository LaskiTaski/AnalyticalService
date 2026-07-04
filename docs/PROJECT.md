# Bond Screener Platform — Документация проекта

## Что это

Веб-платформа для скрининга облигаций Московской биржи. Пользователь задаёт параметры (доходность, купон, срок, тип бумаги) — платформа показывает подходящие облигации с детальной аналитикой. Монетизация через подписки (веб; схема пользователей будет спроектирована на этапе авторизации).

Вдохновлён Snowball Income — современный дизайн, быстрый отклик, профессиональная аналитика.

## Текущее состояние

### Готово (backend)

- **MOEX Data Collector** (`backend/collector/`) — забирает ~3000 облигаций через MOEX ISS API за 25 сек. Три борда: TQCB (корпоративные), TQOB (ОФЗ), TQIR (муниципальные). Bulk upsert батчами по 500.
- **PostgreSQL 16** — таблицы: `bonds`, `issuers`, `issuer_events`. Alembic миграции через psycopg3 (не psycopg2 — он несовместим с Windows cp1251 локалью).
- **FastAPI Backend** (`backend/api/`) — REST API:
  - `GET /api/v1/bonds` — фильтрация с пагинацией (цена, доходность, купон, дни до погашения, квал. статус, тип, листинг, сортировка)
  - `GET /api/v1/bonds/{secid}` — детали одной облигации
  - `GET /api/v1/stats/market-overview` — обзор рынка (средние, распределение по типам)
  - `GET /api/v1/issuers/{inn}` — карточка эмитента, `GET /api/v1/issuers/{inn}/events` — риск-события
- **Риск-сигналы эмитента, этап 1** (`backend/collector/issuer_client.py`, `issuer_enricher.py`) — маппинг SECID→ИНН через MOEX ISS, события смены уровня листинга, бейдж риска в скринере, вкладка «Эмитент». План этапов 2-4 (рейтинги АКРА/Эксперт РА, e-disclosure, Федресурс, ГИР БО): `docs/RISK_SIGNALS_PLAN.md`
- **Docker Compose** — PostgreSQL 16 + Redis 7

> Telegram-бот удалён из проекта (был legacy). Таблицы `users`/`user_filters`/`payments` были завязаны на telegram_id и снесены миграцией `a1b2c3d4e5f6`; веб-авторизация и подписки будут спроектированы заново.

### В разработке

- **Веб-интерфейс** (React + TypeScript) — см. `docs/FRONTEND.md`

### Запланировано

- Redis-кэш для API
- Авторизация и подписки
- CI/CD pipeline
- Kubernetes деплой

## Структура проекта

```
AnalyticalService/
├── docs/                    # Документация (этот файл и другие)
│   ├── PROJECT.md           # Обзор проекта (этот файл)
│   ├── ARCHITECTURE.md      # Архитектура системы
│   ├── STACK.md             # Стек технологий и обоснование
│   ├── FEATURES.md          # Фичи с статусами
│   ├── FRONTEND.md          # Архитектура фронтенда
│   ├── API.md               # Документация API
│   └── RISK_SIGNALS_PLAN.md # План фичи «Риск-сигналы эмитента»
├── backend/
│   ├── api/                 # FastAPI backend
│   │   ├── main.py          # Точка входа: python -m backend.api.main
│   │   ├── router.py        # Эндпоинты (bonds, issuers, stats)
│   │   ├── service.py       # Бизнес-логика (фильтрация, пагинация, риск-агрегат)
│   │   └── schemas.py       # Pydantic схемы
│   ├── collector/           # MOEX Data Collector + обогащение эмитентов
│   │   ├── main.py          # Точка входа: python -m backend.collector.main
│   │   ├── moex_client.py   # Клиент MOEX ISS API (котировки)
│   │   ├── issuer_client.py # Клиент MOEX ISS: описание бумаги → ИНН эмитента
│   │   ├── issuer_enricher.py # Обогащение ИНН + события смены листинга
│   │   └── repository.py    # Bulk upsert в PostgreSQL
│   ├── core/                # Конфигурация, логирование
│   │   ├── config.py        # Pydantic Settings (.env)
│   │   └── logging.py       # Structlog
│   └── db/                  # База данных
│       ├── models/          # SQLAlchemy 2.0 модели
│       ├── migrations/      # Alembic миграции
│       └── session.py       # Async session factory
├── frontend/                # React приложение (в разработке)
├── docker/
│   └── Dockerfile
├── docker-compose.yml
├── pyproject.toml
├── alembic.ini
└── .env                     # Секреты (не в git)
```

## Как запустить

```bash
# Всё в Docker (рекомендуется)
cp .env.example .env
docker compose up -d --build

# Фронтенд:  http://localhost:3000
# Swagger:   http://localhost:8000/docs
```

Порядок старта в compose: postgres/redis → migrations (alembic upgrade head) → api + collector (цикл, сразу забирает данные с MOEX) → frontend.

Локальная разработка без Docker — см. README.md.

## Важные нюансы (ловушки)

1. **Локальный PostgreSQL на Windows** — если установлен, он занимает порт 5432 раньше Docker. Перед запуском: `net stop postgresql-x64-16`
2. **psycopg2 несовместим с Windows cp1251** — используем psycopg3 (`postgresql+psycopg://` для миграций, `postgresql+asyncpg://` для приложения)
3. **API_HOST=0.0.0.0** — это адрес для прослушивания. Клиенты (фронтенд) подключаются к `localhost:8000`
