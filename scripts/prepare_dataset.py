"""
Dataset preparation script - runs once before training

Reads raw datasets from data/datasets/raw/, cleans them,
remaps class IDs, balances classes, and outputs to
data/datasets/processed/

"""

import shutil
import uuid
from collections import Counter, defaultdict
from pathlib import Path
from PIL import Image

import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.shared.utils.logging import get_logger
from src.shared.utils.paths import (
    RAW_DATASET_DIR,
    PROCESSED_DATASET_DIR,
)
from src.backend.core.settings import get_yaml_config

logger = get_logger("dataset_prep")


def _get_prep_config() -> dict:
    config = get_yaml_config()
    return config["dataset_preparation"]


def _get_class_mapping() -> dict:
    return _get_prep_config()["class_mapping"]


def _get_source_datasets() -> dict:
    return _get_prep_config()["source_datasets"]


def _get_max_samples() -> dict:
    return _get_prep_config()["max_samples_per_class"]


def _get_supported_extensions() -> set:
    return set(_get_prep_config()["supported_image_extensions"])


def _get_split_name_map() -> dict:
    return _get_prep_config()["split_name_map"]


def _ensure_output_dirs() -> None:
    # Output directory structure

    for split in ["train", "val", "test"]:
        (PROCESSED_DATASET_DIR / split / "images").mkdir(
            parents=True, exist_ok=True
        )
        (PROCESSED_DATASET_DIR / split / "labels").mkdir(
            parents=True, exist_ok=True
        )


def _validate_and_convert_image(
    src_path: Path,
    dst_path: Path,
) -> bool:
    """
    Validates image and convert to RGB

    Returns -
        True : image successfully processed
        False : image is corrupted or unreadable
    """

    try:
        with Image.open(src_path) as img:
            img.verify()

        with Image.open(src_path) as img:
            if img.mode != "RGB":
                img = img.convert("RGB")
                img.save(dst_path, "JPEG", quality=95)
            else:
                shutil.copy2(src_path, dst_path)

        return True

    except Exception as e:
        logger.warning(f"Skipping corrupted image {src_path.name}: {e}")
        return False


def _remap_label_file(
    src_label_path: Path,
    dst_label_path: Path,
    source_class_map: dict,
    discard_classes: set,
    unified_class_ids: dict,
) -> Counter:
    """
    Remapping class IDs to unified mapping

    Returns: Counter of remapped class annotations
    """
    counts = Counter()

    if not src_label_path.exists():
        return counts

    output_lines = []

    with open(src_label_path, "r") as f:
        for line in f:
            parts = line.strip().split()

            if len(parts) < 5:
                continue

            original_class_id = int(parts[0])

            if original_class_id in discard_classes:
                continue

            if original_class_id not in source_class_map:
                continue

            unified_class_name = source_class_map[original_class_id]

            if unified_class_name not in unified_class_ids:
                continue

            new_class_id = unified_class_ids[unified_class_name]
            parts[0] = str(new_class_id)
            output_lines.append(" ".join(parts))
            counts[unified_class_name] += 1

    if output_lines:
        with open(dst_label_path, "w") as f:
            f.write("\n".join(output_lines) + "\n")

    return counts


def _get_primary_class_for_image(label_path: Path) -> str:
    # Gets primary class in image based on the class with most annotations
    
    if not label_path.exists():
        return "unknown"

    class_counts = Counter()

    with open(label_path, "r") as f:
        for line in f:
            parts = line.strip().split()
            if parts:
                try:
                    class_counts[int(parts[0])] += 1
                except ValueError:
                    continue

    if not class_counts:
        return "unknown"

    return str(class_counts.most_common(1)[0][0])


def _process_dataset_split(
    dataset_name: str,
    dataset_config: dict,
    split_source: str,
    split_target: str,
    supported_extensions: set
) -> tuple[int, Counter]:
    """
    Processes one split of one source dataset

    Returns:
        (number of images processed, Counter of class annotations)
    """

    unified_class_ids = _get_class_mapping()
    source_class_map = dataset_config["class_map"]
    discard_classes = set(dataset_config.get("discard_classes", []))

    dataset_folder = RAW_DATASET_DIR / dataset_config["folder"]
    src_images_dir = dataset_folder / split_source / "images"
    src_labels_dir = dataset_folder / split_source / "labels"

    if not src_images_dir.exists():
        logger.warning(
            f"{dataset_name} : {split_source}/images not found | Skipping"
        )
        return 0, Counter()

    dst_images_dir = PROCESSED_DATASET_DIR / split_target / "images"
    dst_labels_dir = PROCESSED_DATASET_DIR / split_target / "labels"

    image_files = sorted([
        f for f in src_images_dir.iterdir()
        if f.is_file() and f.suffix.lower() in supported_extensions
    ])

    processed_count = 0
    total_counts = Counter()

    for img_file in image_files:
        
        # Processing labels - if not valid, skips image
        src_label_path = src_labels_dir / f"{img_file.stem}.txt"
        temp_label_path = dst_images_dir / f"_temp_{uuid.uuid4().hex}.txt"

        label_counts = _remap_label_file(
            src_label_path,
            temp_label_path,
            source_class_map,
            discard_classes,
            unified_class_ids,
        )

        if not label_counts:
            if temp_label_path.exists():
                temp_label_path.unlink()
            continue
        
        # Generating unique filename with primary class name
        primary_class_name = label_counts.most_common(1)[0][0]

        unique_id = uuid.uuid4().hex[:8]
        new_name = f"{primary_class_name.lower()}_{unique_id}{img_file.suffix.lower()}"

        dst_img_path = dst_images_dir / new_name
        dst_label_path = dst_labels_dir / f"{Path(new_name).stem}.txt"

        temp_label_path.rename(dst_label_path)

        # Validating and copying image
        if not _validate_and_convert_image(img_file, dst_img_path):
            # Removes label if image failed
            
            if dst_label_path.exists():
                dst_label_path.unlink()
            continue

        total_counts.update(label_counts)
        processed_count += 1

    logger.info(
        f"{dataset_name}/{split_source} to {split_target} | "
        f"{processed_count:,} images processed"
    )
    return processed_count, total_counts


def _balance_split(split: str, max_samples: int) -> None:
    # Removes excess images and their labels for over-represented classes
    
    images_dir = PROCESSED_DATASET_DIR / split / "images"
    labels_dir = PROCESSED_DATASET_DIR / split / "labels"

    if not images_dir.exists():
        return

    # Grouping images by their primary class
    class_to_images = defaultdict(list)

    for img_file in images_dir.iterdir():
        if not img_file.is_file():
            continue

        label_file = labels_dir / f"{img_file.stem}.txt"
        primary_class = _get_primary_class_for_image(label_file)
        class_to_images[primary_class].append(img_file)

    # Caps each class at max_samples
    removed_count = 0
    for class_id, images in class_to_images.items():
        if len(images) <= max_samples:
            continue

        images.sort()
        to_remove = images[max_samples:]

        for img_file in to_remove:
            label_file = labels_dir / f"{img_file.stem}.txt"

            if img_file.exists():
                img_file.unlink()
            if label_file.exists():
                label_file.unlink()

            removed_count += 1

        logger.info(
            f"Balanced {split} : class {class_id} capped at {max_samples} | "
            f"(removed {len(to_remove):,})"
        )

    if removed_count == 0:
        logger.info(f"Balanced {split} : no removal needed")


def _print_final_summary() -> None:

    unified_class_ids = _get_class_mapping()
    id_to_name = {v: k for k, v in unified_class_ids.items()}

    logger.info("Final Dataset Summary")

    for split in ["train", "val", "test"]:
        labels_dir = PROCESSED_DATASET_DIR / split / "labels"

        if not labels_dir.exists():
            continue

        images_dir = PROCESSED_DATASET_DIR / split / "images"
        image_count = len(list(images_dir.iterdir())) if images_dir.exists() else 0

        class_counts = Counter()

        for label_file in labels_dir.iterdir():
            if not label_file.is_file():
                continue

            with open(label_file, "r") as f:
                for line in f:
                    parts = line.strip().split()
                    if parts:
                        try:
                            class_counts[int(parts[0])] += 1
                        except ValueError:
                            continue

        logger.info(f"{split} : {image_count:,} images")
        for cid in sorted(class_counts.keys()):
            name = id_to_name.get(cid, f"unknown_{cid}")
            logger.info(f"{cid} ({name}) : {class_counts[cid]:,}")


def prepare_dataset() -> None:
    
    logger.info("Starting dataset preparation")
    _ensure_output_dirs()

    source_datasets = _get_source_datasets()
    supported_extensions = _get_supported_extensions()

    total_processed = 0
    total_counts_by_split = defaultdict(Counter)

    # Processing each source dataset
    for dataset_name, dataset_config in source_datasets.items():
        logger.info(f"Processing dataset: {dataset_name}")

        for split_source, split_target in _get_split_name_map().items():
            count, counts = _process_dataset_split(
                dataset_name,
                dataset_config,
                split_source,
                split_target,
                supported_extensions,
            )
            total_processed += count
            total_counts_by_split[split_target].update(counts)

    logger.info(f"Total images processed: {total_processed:,}")

    # Balancing splits
    logger.info("Balancing classes")

    max_samples_config = _get_max_samples()
    for split, max_samples in max_samples_config.items():
        _balance_split(split, max_samples)

    _print_final_summary()

    logger.info("Dataset preparation complete")
    logger.info(f"Output : {PROCESSED_DATASET_DIR}")


if __name__ == "__main__":
    prepare_dataset()