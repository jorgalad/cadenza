"""Cadenza REST API -- FastAPI application factory and entry point."""

from __future__ import annotations

from fastapi import FastAPI

from cadenza.api.errors import register_exception_handlers
from cadenza.api.routes.health import router as health_router


def create_app() -> FastAPI:
    """Create and configure the Cadenza FastAPI application."""
    app = FastAPI(
        title="Cadenza API",
        description=(
            "Music analysis, transformation, and generation over HTTP. "
            "CN (Cadenza Notation) strings are the primary wire format."
        ),
        version="1",
    )
    register_exception_handlers(app)
    app.include_router(health_router)
    return app


app = create_app()


def run_server() -> None:
    """Run the Cadenza API server (entry point for cadenza-server script)."""
    import uvicorn

    uvicorn.run("cadenza.api:app", host="127.0.0.1", port=8000, reload=False)
