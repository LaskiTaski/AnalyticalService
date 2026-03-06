# Git Branching Strategy

## Ветки

| Ветка | Назначение | Деплой |
|-------|-----------|--------|
| `main` | Стабильный production-код | → Production сервер |
| `develop` | Интеграционная ветка | → Staging (опционально) |
| `feature/*` | Новые фичи | Локально / PR → develop |
| `fix/*` | Баг-фиксы | PR → develop |
| `hotfix/*` | Срочные фиксы прода | PR → main + develop |
| `release/*` | Подготовка релиза | develop → main |

## Workflow

1. Новая фича: `git checkout -b feature/moex-collector develop`
2. Работа → коммиты → push
3. PR в `develop` → code review → merge
4. Когда `develop` стабилен: `release/v1.0.0` → тесты → merge в `main`
5. Tag: `git tag v1.0.0`

## Локальное тестирование

```bash
docker compose up -d          # поднять всё
docker compose run --rm test  # запустить тесты
docker compose down            # остановить
```
