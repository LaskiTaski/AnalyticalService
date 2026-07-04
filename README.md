# Bond Screener

Платформа для скрининга облигаций Московской биржи: MOEX-коллектор + FastAPI + React-фронтенд.

## Архитектура

```
Браузер ──► frontend (nginx :3000) ──► /api ──► api (FastAPI :8000) ──► PostgreSQL 16
                                                                          ▲
MOEX ISS API ──► collector (цикл, каждые 5 мин) ──────────────────────────┘
                 └─ котировки бумаг + риск-сигналы эмитентов (ИНН, листинг)
```

- **frontend** — React 18 + TypeScript + Vite + Tailwind + TanStack Query. nginx раздаёт статику и проксирует `/api` на бэкенд (same-origin, CORS не нужен).
- **api** — REST API: скрининг с фильтрами/поиском/сортировкой/пагинацией, детали бумаги, обзор рынка, карточка эмитента и его риск-события. Swagger: `/docs`.
- **collector** — забирает ~3000 облигаций с MOEX ISS (борды TQCB/TQOB/TQIR) и обновляет БД каждые `COLLECTOR_INTERVAL_SECONDS`. Дополнительно ведёт риск-сигналы эмитентов: фиксирует смену уровня листинга и батчами обогащает ИНН эмитентов (`/iss/securities/{secid}` → description.INN), см. `docs/RISK_SIGNALS_PLAN.md`.
- **migrations** — одноразовый шаг `alembic upgrade head`; api и collector стартуют только после его успешного завершения.

## Быстрый старт (Docker)

```bash
cp .env.example .env

docker compose up -d --build
```

Что произойдёт: поднимутся PostgreSQL и Redis → выполнятся миграции → стартуют API и коллектор → коллектор сразу заберёт реальные данные с MOEX → соберётся и поднимется фронтенд.

| Сервис    | URL                              |
|-----------|----------------------------------|
| Фронтенд  | http://localhost:3000            |
| API       | http://localhost:8000            |
| Swagger   | http://localhost:8000/docs       |

Проверка, что данные пришли:

```bash
curl http://localhost:8000/api/v1/stats/market-overview
```

Первые данные появляются через ~30 сек после старта коллектора. Если MOEX недоступен (нет интернета / файрвол), можно засеять демо-данные:

```bash
docker compose run --rm seed
```

## Разработка без Docker (только инфраструктура в контейнерах)

```bash
docker compose up -d postgres redis
pip install -e ".[dev]"
alembic upgrade head

python -m backend.collector.main        # разовый сбор с MOEX
python -m backend.api.main              # API на :8000

cd frontend
npm install
npm run dev                         # Vite на :5173, /api проксируется на :8000
```

## Полезные команды

```bash
docker compose logs -f collector          # логи сбора данных
docker compose run --rm test              # тесты
docker compose down                       # остановить (данные БД сохраняются в volume)
docker compose down -v                    # остановить и удалить данные
```

## Структура

```
AnalyticalService/
├── frontend/              # React SPA (см. docs/FRONTEND.md)
│   ├── src/
│   ├── Dockerfile         # node build → nginx
│   └── nginx.conf
├── backend/
│   ├── api/               # FastAPI: бумаги, эмитенты, риск-события
│   ├── collector/         # MOEX ISS: котировки + обогащение эмитентов
│   ├── core/              # Конфигурация, логирование
│   └── db/                # Модели, миграции, сессии
├── scripts/
│   └── seed_demo_data.py  # демо-данные без доступа к MOEX
├── docker/Dockerfile      # образ Python-сервисов
├── docker-compose.yml
└── docs/                  # PROJECT, ARCHITECTURE, API, RISK_SIGNALS_PLAN, ...
```

## Git Workflow

См. [BRANCHING.md](BRANCHING.md)
