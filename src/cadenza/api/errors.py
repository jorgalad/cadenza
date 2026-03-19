"""API error types, error codes, and FastAPI exception handlers."""

from __future__ import annotations

from fastapi import FastAPI
from fastapi.requests import Request
from fastapi.responses import JSONResponse

from cadenza.cn.errors import ParseError

# --- Error code constants ---

INVALID_CN = "INVALID_CN"
INVALID_PITCH = "INVALID_PITCH"
INVALID_INTERVAL = "INVALID_INTERVAL"
INVALID_SCALE_NAME = "INVALID_SCALE_NAME"
INVALID_CHORD_SYMBOL = "INVALID_CHORD_SYMBOL"
TRANSPOSE_OUT_OF_RANGE = "TRANSPOSE_OUT_OF_RANGE"
NOT_IMPLEMENTED = "NOT_IMPLEMENTED"
INVALID_INPUT = "INVALID_INPUT"


class CadenzaAPIError(Exception):
    """Structured API error with error code, message, and optional input value."""

    def __init__(self, error_code: str, message: str, input_value: str = "") -> None:
        self.error_code = error_code
        self.message = message
        self.input_value = input_value
        super().__init__(message)


async def cadenza_error_handler(request: Request, exc: CadenzaAPIError) -> JSONResponse:
    """Handle CadenzaAPIError -> 422 JSON with error code and message."""
    body: dict[str, str] = {"error": exc.error_code, "message": exc.message}
    if exc.input_value:
        body["input"] = exc.input_value
    return JSONResponse(status_code=422, content=body)


async def parse_error_handler(request: Request, exc: ParseError) -> JSONResponse:
    """Handle CN ParseError -> 422 JSON with INVALID_CN error code."""
    return JSONResponse(
        status_code=422,
        content={"error": INVALID_CN, "message": str(exc)},
    )


async def value_error_handler(request: Request, exc: ValueError) -> JSONResponse:
    """Handle generic ValueError -> 422 JSON with INVALID_INPUT error code."""
    return JSONResponse(
        status_code=422,
        content={"error": INVALID_INPUT, "message": str(exc)},
    )


def register_exception_handlers(app: FastAPI) -> None:
    """Register all Cadenza exception handlers on the FastAPI app."""
    app.add_exception_handler(CadenzaAPIError, cadenza_error_handler)  # type: ignore[arg-type]
    app.add_exception_handler(ParseError, parse_error_handler)  # type: ignore[arg-type]
    app.add_exception_handler(ValueError, value_error_handler)  # type: ignore[arg-type]
