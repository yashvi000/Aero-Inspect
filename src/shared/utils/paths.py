import os
from pathlib import Path

# Root directory of the project
ROOT_DIR = Path(__file__).resolve().parent.parent.parent.parent

# Data directories
UPLOADS_DIR = ROOT_DIR / "data" / "uploads"
VECTORSTORE_DIR = ROOT_DIR / "data" / "vectorstore"
CORPUS_DIR = ROOT_DIR / "data" / "corpus"
DEMO_IMAGES_DIR = ROOT_DIR / "data" / "demo_images"

# Artifacts directories
REPORTS_DIR = ROOT_DIR / "artifacts" / "reports"
WEIGHTS_DIR = ROOT_DIR / "artifacts" / "weights"
PREDICTIONS_DIR = ROOT_DIR / "artifacts" / "predictions"
METRICS_DIR = ROOT_DIR / "artifacts" / "metrics"

# Logs
LOGS_DIR = ROOT_DIR / "logs"
BACKEND_LOGS_DIR = LOGS_DIR / "backend"

# Create directories if they don't exist
def ensure_dirs():
    dirs = [
        UPLOADS_DIR,
        VECTORSTORE_DIR,
        CORPUS_DIR,
        DEMO_IMAGES_DIR,
        REPORTS_DIR,
        WEIGHTS_DIR,
        PREDICTIONS_DIR,
        METRICS_DIR,
        BACKEND_LOGS_DIR,
    ]
    for d in dirs:
        d.mkdir(parents=True, exist_ok=True)