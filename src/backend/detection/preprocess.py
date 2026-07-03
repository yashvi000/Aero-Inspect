from pathlib import Path

from PIL import Image, UnidentifiedImageError

from src.backend.core.settings import get_yaml_config
from src.shared.utils.logging import get_logger

logger = get_logger("preprocessing")

CONFIG = get_yaml_config()

ALLOWED_EXTENSIONS = set(
    CONFIG["dataset_preparation"]["supported_image_extensions"]
)

MAX_IMAGE_SIZE = CONFIG["runtime_preprocessing"]["max_image_size"]


def preprocess_image(image_path: str) -> str:
    
    image_path = Path(image_path)

    logger.info(f"Processing image: {image_path.name}")

    if not image_path.exists():
        raise FileNotFoundError(f"{image_path} does not exist.")

    if image_path.suffix.lower() not in ALLOWED_EXTENSIONS:
        image_path.unlink(missing_ok=True)
        raise ValueError(
            f"Unsupported image format: {image_path.suffix}"
        )

    try:

        image = Image.open(image_path)

        if image.mode != "RGB":
            image = image.convert("RGB")

        if max(image.size) > MAX_IMAGE_SIZE:
            image.thumbnail(
                (MAX_IMAGE_SIZE, MAX_IMAGE_SIZE)
            )

        image.save(
            image_path,
            format="JPEG",
            quality=95
        )

        logger.info("Image preprocessing completed.")

        return str(image_path)

    except UnidentifiedImageError:

        image_path.unlink(missing_ok=True)

        logger.exception("Corrupted image uploaded.")

        raise ValueError(
            "Uploaded file is not a valid image."
        )

    except Exception:

        logger.exception("Image preprocessing failed.")

        raise