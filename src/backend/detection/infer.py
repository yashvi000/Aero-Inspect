from ultralytics import YOLO

from src.shared.utils.logging import get_logger
from src.shared.utils.paths import WEIGHTS_DIR

logger = get_logger("inference")

MODEL_PATH = WEIGHTS_DIR / "best.pt"

_model = None


def get_model() -> YOLO:
        
    global _model

    if _model is None:
        logger.info(f"Loading YOLO model from {MODEL_PATH}")
        _model = YOLO(str(MODEL_PATH))
        logger.info("YOLO model loaded successfully.")

    return _model


def run_inference(
    image_path: str,
    confidence: float = 0.25
) -> list:
   
    logger.info(f"Running inference on {image_path}")

    model = get_model()

    results = model.predict(
        source=image_path,
        conf=confidence,
        verbose=False
    )

    detections = []

    for box in results[0].boxes:

        detections.append(
            {
                "class_id": int(box.cls.item()),
                "class_name": model.names[int(box.cls.item())],
                "confidence": round(float(box.conf.item()), 4),
                "bbox": [
                    float(value)
                    for value in box.xyxy[0].tolist()
                ],
            }
        )

    logger.info(f"{len(detections)} detection(s) found.")

    return detections