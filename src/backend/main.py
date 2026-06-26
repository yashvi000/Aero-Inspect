from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
from src.backend.db.session import engine
from src.backend.db.base import Base
from src.backend.inspections.routes import router as inspections_router
from src.backend.zones.routes import router as zones_router

load_dotenv()

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

# Include routers
app.include_router(inspections_router)
app.include_router(zones_router)

@app.get("/health")
def health_check():
    return {
        "status": "ok",
        "database": "connected",
        "version": "1.0.0"
    }