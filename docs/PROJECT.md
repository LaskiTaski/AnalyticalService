# Bond Screener Platform — Документация проекта

## Что это

Веб-платформа для скрининга облигаций Московской биржи. Пользователь задаёт параметры (доходность, купон, срок, тип бумаги) — платформа показывает подходящие облигации с детальной аналитикой. Монетизация через подписки.

Вдохновлён Snowball Income — современный дизайн, быстрый отклик, профессиональная аналитика.

## Текущее состояние

### Готово (backend)

- **MOEX Data Collector** (`src/collector/`) — забирает ~3000 облигаций через MOEX ISS API за 25 сек. Три борда: TQCB (корпоративные), TQOB (ОФЗ), TQIR (муниципальные). Bulk upsert батчами по 500.
- **PostgreSQL 16** — таблицы: `bonds`, `users`, `user_filters`, `payments`. Alembic миграции через psycopg3 (не psycopg2 — он несовместим с Windows cp1251 локалью).
- **FastAPI Backend** (`src/api/`) — REST API:
  - `GET /api/v1/bonds` — фильтрация с пагинацией (цена, доходность, купон, дни до погашения, квал. статус, тип, листинг, сортировка)
  - `GET /api/v1/bonds/{secid}` — детали одной облигации
  - `GET /api/v1/stats/market-overview` — обзор рынка (средние, распределение по типам)
- **Docker Compose** — PostgreSQL 16 + Redis 7
- **Telegram-бот** (`src/bot/`) — рабочий, но заброшен в пользу веб-интерфейса (Telegram блокируется в РФ)

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
│   └── API.md               # Документация API
├── src/
│   ├── api/                 # FastAPI backend
│   │   ├── main.py          # Точка входа: python -m src.api.main
│   │   ├── router.py        # Эндпоинты
│   │   ├── service.py       # Бизнес-логика (фильтрация, пагинация)
│   │   └── schemas.py       # Pydantic схемы
│   ├── collector/           # MOEX Data Collector
│   │   ├── main.py          # Точка входа: python -m src.collector.main
│   │   ├── moex_client.py   # Клиент MOEX ISS API
│   │   └── repository.py    # Bulk upsert в PostgreSQL
│   ├── bot/                 # Telegram-бот (legacy, заброшен)
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
# 1. Остановить локальный PostgreSQL (если установлен)
net stop postgresql-x64-16

# 2. Поднять Docker-контейнеры
docker compose up -d postgres redis

# 3. Применить миграции
alembic upgrade head

# 4. Собрать данные с MOEX
python -m src.collector.main

# 5. Запустить API
python -m src.api.main

# 6. Открыть Swagger
# http://localhost:8000/docs
```

## Важные нюансы (ловушки)

1. **Локальный PostgreSQL на Windows** — если установлен, он занимает порт 5432 раньше Docker. Перед запуском: `net stop postgresql-x64-16`
2. **psycopg2 несовместим с Windows cp1251** — используем psycopg3 (`postgresql+psycopg://` для миграций, `postgresql+asyncpg://` для приложения)
3. **API_HOST=0.0.0.0** — это адрес для прослушивания. Клиенты (бот, фронтенд) подключаются к `localhost:8000`
4. **VPN нужен** для доступа к api.telegram.org из РФ (если бот нужен)
