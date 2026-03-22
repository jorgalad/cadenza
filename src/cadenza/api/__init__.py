"""Cadenza REST API -- FastAPI application factory and entry point."""

from __future__ import annotations

import importlib

from fastapi import FastAPI

from cadenza.api.errors import register_exception_handlers
from cadenza.api.routes.health import router as health_router
from cadenza.api.routes.theory import router as theory_router
from cadenza.api.routes.transforms import router as transforms_router

# Phase 13 routers -- imported conditionally during incremental build
_PHASE_13_ROUTERS = []
for _mod_name, _attr in [
    ("cadenza.api.routes.analysis", "router"),
    ("cadenza.api.routes.batch_ops", "router"),
    ("cadenza.api.routes.counterpoint", "router"),
    ("cadenza.api.routes.settheory", "router"),
    ("cadenza.api.routes.patterns", "router"),
    ("cadenza.api.routes.composition", "router"),
    ("cadenza.api.routes.io", "router"),
    ("cadenza.api.routes.jobs", "router"),
    ("cadenza.api.routes.batch", "router"),
]:
    try:
        _mod = importlib.import_module(_mod_name)
        _PHASE_13_ROUTERS.append(getattr(_mod, _attr))
    except (ImportError, ModuleNotFoundError):
        pass


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
    app.include_router(transforms_router)
    app.include_router(theory_router)
    for _router in _PHASE_13_ROUTERS:
        app.include_router(_router)
    return app


app = create_app()


def run_server() -> None:
    """Run the Cadenza API server (entry point for cadenza-server script)."""
    import uvicorn

    uvicorn.run("cadenza.api:app", host="127.0.0.1", port=8000, reload=False)
