FROM python:3.12-slim

WORKDIR /app

# Python deps — отдельным слоем для кэширования
COPY pyproject.toml ./
RUN pip install --no-cache-dir -e ".[dev]"

# App code
COPY alembic.ini ./
COPY backend ./backend
COPY scripts ./scripts
COPY tests ./tests