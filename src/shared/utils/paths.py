from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[3]

CONFIG_DIR = PROJECT_ROOT / "config"
CORPUS_DIR = PROJECT_ROOT / "data" / "corpus"
VECTORSTORE_DIR = PROJECT_ROOT / "data" / "vectorstore"
UPLOADS_DIR = PROJECT_ROOT / "data" / "uploads"
WEIGHTS_DIR = PROJECT_ROOT / "artifacts" / "weights"
REPORTS_DIR = PROJECT_ROOT / "artifacts" / "reports"
METRICS_DIR = PROJECT_ROOT / "artifacts" / "metrics"
LOGS_DIR = PROJECT_ROOT / "logs"

# Added by Person 3 — creates required directories on startup
def ensure_dirs():
    dirs = [UPLOADS_DIR, REPORTS_DIR, METRICS_DIR, LOGS_DIR / "backend"]
    for d in dirs:
        d.mkdir(parents=True, exist_ok=True)