"""Cadenza REST API -- FastAPI application factory and entry point."""

from __future__ import annotations

import importlib

from fastapi import FastAPI

from cadenza.api.errors import register_exception_handlers
from cadenza.api.routes.health import router as health_router
from cadenza.api.routes.theory import router as theory_router
from cadenza.api.routes.transforms import router as transforms_router

# Phase 13 route modules -- discovered lazily in create_app() to avoid
# circular import issues (e.g. cadenza.analysis -> cadenza.api -> analysis route)
_PHASE_13_MODULES = [
    ("cadenza.api.routes.analysis", "router"),
    ("cadenza.api.routes.batch_ops", "router"),
    ("cadenza.api.routes.counterpoint", "router"),
    ("cadenza.api.routes.settheory", "router"),
    ("cadenza.api.routes.patterns", "router"),
    ("cadenza.api.routes.composition", "router"),
    ("cadenza.api.routes.io", "router"),
    ("cadenza.api.routes.jobs", "router"),
    ("cadenza.api.routes.batch", "router"),
]


def _discover_phase13_routers() -> list:
    """Import Phase 13 route modules and return their routers."""
    routers = []
    for mod_name, attr in _PHASE_13_MODULES:
        try:
            mod = importlib.import_module(mod_name)
            routers.append(getattr(mod, attr))
        except (ImportError, ModuleNotFoundError):
            pass
    return routers


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
    for _router in _discover_phase13_routers():
        app.include_router(_router)
    return app


app = create_app()


def run_server() -> None:
    """Run the Cadenza API server (entry point for cadenza-server script)."""
    import uvicorn

    uvicorn.run("cadenza.api:app", host="127.0.0.1", port=8000, reload=False)
