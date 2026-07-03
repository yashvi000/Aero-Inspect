from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from src.backend.inspections.routes import router as inspections_router
from src.backend.zones.routes import router as zones_router
from src.shared.utils.logging import get_logger
from src.shared.utils.paths import ensure_dirs

logger = get_logger("api-endpoints")

ensure_dirs()

app = FastAPI(
    title="Aero-Inspect API",
    description="Edge AI Aerospace Defect Detection — Tata Innovent 2026",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(inspections_router)
app.include_router(zones_router)

@app.get("/health")
def health_check():
    logger.info("Health check called")
    return {
        "status": "ok",
        "database": "connected",
        "version": "1.0.0"
    }

logger.info("Aero-Inspect backend started")