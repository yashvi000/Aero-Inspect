from src.backend.core.settings import get_yaml_config
from src.shared.utils.logging import get_logger

logger = get_logger("severity")

CONFIG = get_yaml_config()

LOW_THRESHOLD = CONFIG["severity"]["low_threshold"]
MEDIUM_THRESHOLD = CONFIG["severity"]["medium_threshold"]


def calculate_severity(
    detections: list,
    image_width: int,
    image_height: int,
) -> list:
    
    logger.info("Calculating defect severity.")

    image_area = image_width * image_height

    if image_area == 0:
        raise ValueError("Invalid image dimensions.")

    for detection in detections:

        x1, y1, x2, y2 = detection["bbox"]

        bbox_area = max(0, (x2 - x1)) * max(0, (y2 - y1))

        damage_percent = round(
            (bbox_area / image_area) * 100,
            2,
        )

        if damage_percent < LOW_THRESHOLD:
            severity = "LOW"

        elif damage_percent < MEDIUM_THRESHOLD:
            severity = "MEDIUM"

        else:
            severity = "HIGH"

        detection["damage_percent"] = damage_percent
        detection["severity"] = severity

    logger.info("Severity calculation completed.")

    return detections