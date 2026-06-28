import logging
import sys
from pathlib import Path
from src.shared.utils.paths import LOGS_DIR

_initialized_loggers = {}

def get_logger(file_name: str, level: str = "INFO") -> logging.Logger:
    
    if file_name in _initialized_loggers:
        return _initialized_loggers[file_name]

    # Ensuring log directory exists
    backend_log_dir = LOGS_DIR / "backend"
    backend_log_dir.mkdir(parents=True, exist_ok=True)

    log_file = backend_log_dir / f"{file_name}.log"

    logger = logging.getLogger(file_name)
    logger.setLevel(getattr(logging, level.upper(), logging.INFO))
    logger.propagate = False   

    if logger.handlers:
        _initialized_loggers[file_name] = logger
        return logger

    formatter = logging.Formatter(
        fmt="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
        datefmt="%d-%m-%Y %H:%M:%S",
    )

    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)

    # File handler
    file_handler = logging.FileHandler(log_file, encoding="utf-8")
    file_handler.setFormatter(formatter)
    
    logger.addHandler(console_handler)
    logger.addHandler(file_handler)

    # Suppressing third-party loggers
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("urllib3").setLevel(logging.WARNING)
    logging.getLogger("chromadb").setLevel(logging.WARNING)
    logging.getLogger("sentence_transformers").setLevel(logging.WARNING)

    logger.info(f"Logger initialized : logs/backend/{file_name}.log")
    _initialized_loggers[file_name] = logger
    return logger