from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
from src.backend.inspections.routes import router as inspections_router
from src.backend.zones.routes import router as zones_router
from src.backend.intelligence.routes import router as intelligence_router
from src.backend.detection.routes import router as detection_router
from src.backend.reports.routes import router as reports_router
from src.backend.auth.routes import router as auth_router
from src.backend.core.exceptions import http_exception_handler, validation_exception_handler, generic_exception_handler
from src.backend.core.middleware import RequestLoggingMiddleware
from src.shared.utils.logging import get_logger
from src.shared.utils.paths import ensure_dirs

logger = get_logger("api-endpoints")

ensure_dirs()

app = FastAPI(
    title="Aero-Inspect API",
    description="Edge AI Aerospace Defect Detection — Tata Innovent 2026",
    version="1.0.0"
)

# Middleware
app.add_middleware(RequestLoggingMiddleware)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Exception handlers
app.add_exception_handler(StarletteHTTPException, http_exception_handler)
app.add_exception_handler(RequestValidationError, validation_exception_handler)
app.add_exception_handler(Exception, generic_exception_handler)

# Routers
app.include_router(auth_router)
app.include_router(inspections_router)
app.include_router(zones_router)
app.include_router(intelligence_router)
app.include_router(detection_router)
app.include_router(reports_router)

@app.get("/health")
def health_check():
    logger.info("Health check called")
    return {
        "status": "ok",
        "database": "connected",
        "version": "1.0.0"
    }

logger.info("Aero-Inspect backend started")