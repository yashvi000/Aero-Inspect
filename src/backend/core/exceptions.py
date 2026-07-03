from fastapi import Request
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
from src.shared.utils.logging import get_logger

logger = get_logger("api-endpoints")

async def http_exception_handler(request: Request, exc: StarletteHTTPException):
    logger.error(f"HTTP error {exc.status_code}: {exc.detail} — {request.url}")
    return JSONResponse(
        status_code=exc.status_code,
        content={"error": True, "message": exc.detail, "code": exc.status_code}
    )

async def validation_exception_handler(request: Request, exc: RequestValidationError):
    logger.error(f"Validation error: {exc.errors()} — {request.url}")
    return JSONResponse(
        status_code=422,
        content={"error": True, "message": "Validation error", "details": exc.errors(), "code": 422}
    )

async def generic_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unexpected error: {str(exc)} — {request.url}")
    return JSONResponse(
        status_code=500,
        content={"error": True, "message": "Internal server error", "code": 500}
    )