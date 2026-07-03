from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from src.shared.utils.logging import get_logger
import time

logger = get_logger("api-endpoints")

class RequestLoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        start_time = time.time()
        response = await call_next(request)
        duration = round((time.time() - start_time) * 1000, 2)
        logger.info(f"{request.method} {request.url.path} — {response.status_code} — {duration}ms")
        return response