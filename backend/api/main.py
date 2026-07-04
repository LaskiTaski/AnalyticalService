"""FastAPI application — Bond Screener API."""

import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.core.config import settings
from backend.core.logging import setup_logging
from backend.api.router import router


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

    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.include_router(router)

    @app.get("/health", tags=["system"])
    async def health() -> dict:
        return {"status": "ok"}

    return app


app = create_app()


if __name__ == "__main__":
    uvicorn.run(
        "backend.api.main:app",
        host=settings.api_host,
        port=settings.api_port,
        reload=settings.debug,
    )
