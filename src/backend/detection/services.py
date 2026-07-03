import cv2

from src.backend.detection.preprocess import preprocess_image
from src.backend.detection.infer import run_inference
from src.backend.detection.severity import calculate_severity
from src.backend.detection.postprocess import postprocess_results

from src.shared.utils.logging import get_logger

logger = get_logger("detection_service")


def detection_service(image_path: str) -> dict:

    logger.info("Starting detection pipeline.")

    # Runtime preprocessing
    processed_path = preprocess_image(image_path)

    # YOLO inference
    detections = run_inference(processed_path)

    image = cv2.imread(processed_path)

    if image is None:
        raise FileNotFoundError(
            f"Unable to read image: {processed_path}"
        )

    height, width = image.shape[:2]

    # Calculate severity only if detections exist
    if detections:
        detections = calculate_severity(
            detections,
            width,
            height,
        )

    result = postprocess_results(
        processed_path,
        detections,
    )

    logger.info("Detection pipeline completed.")

    return result