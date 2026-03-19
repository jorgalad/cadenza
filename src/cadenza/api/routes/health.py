"""Health check endpoint for DAW integration probing."""

from __future__ import annotations

from fastapi import APIRouter

from cadenza.api.schemas import HealthResponse

router = APIRouter(prefix="/v1", tags=["health"])


@router.get("/health", response_model=HealthResponse, summary="Health check for DAW integration probing")
def health() -> dict:
    """Return service health status and version info."""
    return {"status": "ok", "version": "1", "cadenza_version": "0.1.0"}
