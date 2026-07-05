import json

from ultralytics import YOLO

from src.backend.core.settings import get_yaml_config
from src.shared.utils.logging import get_logger
from src.shared.utils.paths import WEIGHTS_DIR, METRICS_DIR, PROJECT_ROOT

logger = get_logger("evaluate_yolo")

CONFIG = get_yaml_config()


def evaluate():

    logger.info("Loading trained YOLO model.")

    model = YOLO(str(WEIGHTS_DIR / "best.pt"))

    dataset_yaml = PROJECT_ROOT / "data" / "datasets" / "dataset.yaml"

    logger.info("Running evaluation on test dataset.")

    metrics = model.val(
        data=str(dataset_yaml),
        split="test",
        imgsz=640
    )

    results = {
        "precision": round(float(metrics.box.mp), 4),
        "recall": round(float(metrics.box.mr), 4),
        "mAP50": round(float(metrics.box.map50), 4),
        "mAP50_95": round(float(metrics.box.map), 4),
    }

    METRICS_DIR.mkdir(parents=True, exist_ok=True)

    output_file = METRICS_DIR / "evaluation_results.json"

    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=4)

    logger.info(f"Evaluation results saved to {output_file}")


if __name__ == "__main__":
    evaluate()