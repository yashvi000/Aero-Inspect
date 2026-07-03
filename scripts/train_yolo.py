"""
train_yolo.py

Train YOLO11n model on the prepared dataset.
"""

from ultralytics import YOLO

from src.backend.core.settings import get_yaml_config
from src.shared.utils.logging import get_logger
from src.shared.utils.paths import PROJECT_ROOT

logger = get_logger("train_yolo")

CONFIG = get_yaml_config()
TRAINING_CONFIG = CONFIG["training"]

DATASET_YAML = PROJECT_ROOT / "data" / "datasets" / "dataset.yaml"


def train():
    """
    Train YOLO model using configuration
    from config.yaml.
    """

    logger.info("Loading YOLO model.")

    model = YOLO(TRAINING_CONFIG["model"])

    logger.info("Starting YOLO training.")

    results = model.train(
        data=str(DATASET_YAML),
        epochs=TRAINING_CONFIG["epochs"],
        imgsz=TRAINING_CONFIG["image_size"],
        batch=TRAINING_CONFIG["batch_size"],
        patience=TRAINING_CONFIG["patience"],
        device=TRAINING_CONFIG["device"],
        save=True,
        plots=True,
        name=TRAINING_CONFIG["run_name"],
    )

    logger.info("Training completed successfully.")
    logger.info(
        f"Best model saved at: {results.save_dir}/weights/best.pt"
    )


if __name__ == "__main__":
    train()