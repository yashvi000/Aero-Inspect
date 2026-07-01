from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[3]

CONFIG_DIR = PROJECT_ROOT / "config"
CORPUS_DIR = PROJECT_ROOT / "data" / "corpus"
VECTORSTORE_DIR = PROJECT_ROOT / "data" / "vectorstore"
UPLOADS_DIR = PROJECT_ROOT / "data" / "uploads"
DEMO_IMAGES_DIR = PROJECT_ROOT / "data" / "demo_images"

WEIGHTS_DIR = PROJECT_ROOT / "artifacts" / "weights"
REPORTS_DIR = PROJECT_ROOT / "artifacts" / "reports"
METRICS_DIR = PROJECT_ROOT / "artifacts" / "metrics"
PREDICTIONS_DIR = PROJECT_ROOT / "artifacts" / "predictions"

BACKEND_LOGS_DIR = PROJECT_ROOT / "logs" / "backend"

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
