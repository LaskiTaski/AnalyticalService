"""Centralized configuration via environment variables."""

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    # --- Database ---
    postgres_host: str = "localhost"
    postgres_port: int = 5432
    postgres_user: str = "bond_user"
    postgres_password: str = "bond_pass"
    postgres_db: str = "bond_screener"

    @property
    def database_url(self) -> str:
        """Async URL for asyncpg — used by the app at runtime."""
        return (
            f"postgresql+asyncpg://{self.postgres_user}:{self.postgres_password}"
            f"@{self.postgres_host}:{self.postgres_port}/{self.postgres_db}"
        )

    @property
    def database_url_sync(self) -> str:
        """Sync URL for psycopg2 — used by Alembic migrations."""
        return (
            f"postgresql+psycopg://{self.postgres_user}:{self.postgres_password}"
            f"@{self.postgres_host}:{self.postgres_port}/{self.postgres_db}"
        )

    # --- Redis ---
    redis_host: str = "localhost"
    redis_port: int = 6379
    redis_db: int = 0

    @property
    def redis_url(self) -> str:
        return f"redis://{self.redis_host}:{self.redis_port}/{self.redis_db}"

    # --- MOEX Collector ---
    collector_interval_seconds: int = 300
    collector_boards: list[str] = ["TQCB", "TQOB", "TQIR"]

    # --- Issuer enrichment (риск-сигналы, этап 1) ---
    # Сколько бумаг без ИНН обогащать за один цикл коллектора
    issuer_enrich_batch: int = 200
    # Пауза между запросами описаний к MOEX ISS (сек) — щадящий rate limit
    issuer_enrich_delay_seconds: float = 0.25

    # --- API ---
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    cors_origins: list[str] = [
        "http://localhost:5173",  # Vite dev server
        "http://localhost:3000",  # Frontend в Docker (nginx)
    ]

    # --- App ---
    debug: bool = False
    log_level: str = "INFO"


settings = Settings()