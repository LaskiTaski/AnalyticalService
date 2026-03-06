"""FastAPI application — Bond Screener API."""

import uvicorn
from fastapi import FastAPI

from src.core.config import settings
from src.core.logging import setup_logging
from src.api.router import router


def create_app() -> FastAPI:
    """Create and configure FastAPI application."""
    setup_logging()

    app = FastAPI(
        title="Bond Screener API",
        description="REST API для скрининга облигаций MOEX",
        version="0.1.0",
        docs_url="/docs",
        redoc_url="/redoc",
    )

    app.include_router(router)

    @app.get("/health", tags=["system"])
    async def health() -> dict:
        return {"status": "ok"}

    return app


app = create_app()


if __name__ == "__main__":
    uvicorn.run(
        "src.api.main:app",
        host=settings.api_host,
        port=settings.api_port,
        reload=settings.debug,
    )
