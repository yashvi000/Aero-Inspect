import base64
import cv2

from src.shared.utils.logging import get_logger
from src.shared.utils.paths import PREDICTIONS_DIR

logger = get_logger("postprocessing")


def postprocess_results(
    image_path: str,
    detections: list,
) -> dict:
    
    logger.info("Starting postprocessing.")

    image = cv2.imread(image_path)

    if image is None:
        raise FileNotFoundError(f"Unable to read image: {image_path}")

    for detection in detections:

        x1, y1, x2, y2 = map(int, detection["bbox"])

        label = (
            f'{detection["class_name"]} '
            f'{detection["confidence"]:.2f}'
        )

        severity = detection["severity"]

        cv2.rectangle(
            image,
            (x1, y1),
            (x2, y2),
            (0, 255, 0),
            2,
        )

        cv2.putText(
            image,
            label,
            (x1, max(20, y1 - 10)),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.6,
            (0, 255, 0),
            2,
        )

        cv2.putText(
            image,
            severity,
            (x1, y2 + 25),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.6,
            (0, 0, 255),
            2,
        )

    # Save annotated image
    output_path = (
        PREDICTIONS_DIR /
        f"{image_path.split('/')[-1].split('\\')[-1]}"
    )

    cv2.imwrite(str(output_path), image)

    success, encoded_image = cv2.imencode(".jpg", image)

    if not success:
        raise RuntimeError("Image encoding failed.")

    image_base64 = base64.b64encode(
        encoded_image.tobytes()
    ).decode("utf-8")

    logger.info("Postprocessing completed.")

    return {
        "annotated_image": image_base64,
        "annotated_image_path": str(output_path),
        "detections": detections,
    }