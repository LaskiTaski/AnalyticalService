"""Alembic migrations environment.

Uses SYNCHRONOUS psycopg2 for migrations to avoid asyncpg + Windows issues.
The app itself still runs on asyncpg at runtime.
"""

from logging.config import fileConfig

from sqlalchemy import engine_from_config, pool
from sqlalchemy.engine import Connection

from alembic import context

from src.core.config import settings
from src.db.models import Base  # noqa — registers all models with metadata

# ── Alembic Config ──────────────────────────────────────────────
config = context.config

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Override the dummy URL from alembic.ini with the real one from .env.
# Using SYNC driver (psycopg2) — migrations don't need async.
config.set_main_option("sqlalchemy.url", settings.database_url_sync)

target_metadata = Base.metadata


# ── Offline (generate SQL script without DB connection) ─────────
def run_migrations_offline() -> None:
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )
    with context.begin_transaction():
        context.run_migrations()


# ── Online (connect to DB and run) ──────────────────────────────
def run_migrations_online() -> None:
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
        )
        with context.begin_transaction():
            context.run_migrations()

    connectable.dispose()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
