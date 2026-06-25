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