from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session
from src.backend.db.session import get_db
from src.backend.inspections import repository
from src.shared.utils.paths import UPLOADS_DIR, PREDICTIONS_DIR
from src.shared.utils.logging import get_logger
from fastapi.responses import FileResponse
import shutil
import uuid

try:
    from src.backend.detection.services import detection_service
    DETECTION_READY = True
except ImportError:
    DETECTION_READY = False
    detection_service = None

logger = get_logger("detection")
router = APIRouter(prefix="/api/detections", tags=["Detection"])

@router.post("/run")
async def run_detection(
    inspection_id: str,
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    try:
        # Save uploaded image
        image_filename = f"{uuid.uuid4()}.jpg"
        image_path = str(UPLOADS_DIR / image_filename)
        with open(image_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        logger.info(f"Running detection for inspection {inspection_id}")

        # Call Person 1's detection service
        if not DETECTION_READY or detection_service is None:
            raise HTTPException(status_code=503, detail="Detection service not ready yet")
        result = detection_service(image_path=image_path)

        # Save first detection to DB
        if result["detections"]:
            first = result["detections"][0]
            bbox = first["bbox"]  # [x1, y1, x2, y2]
            repository.save_detection(
                db, inspection_id,
                defect_type=first["class_name"],
                confidence=first["confidence"],
                severity=first["severity"],
                bbox={
                    "x": bbox[0], "y": bbox[1],
                    "width": bbox[2] - bbox[0],
                    "height": bbox[3] - bbox[1]
                },
                zone=None
            )
            repository.update_inspection_status(db, inspection_id, "DETECTION_COMPLETE")

        return {
            "inspection_id": inspection_id,
            "annotated_image": result["annotated_image"],
            "annotated_image_path": result["annotated_image_path"],
            "detections": result["detections"],
            "total_defects": len(result["detections"])
        }

    except FileNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Detection error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{inspection_id}/annotated-image")
def get_annotated_image(inspection_id: str):
    """Optional: serve annotated image file directly"""
    matches = list(PREDICTIONS_DIR.glob(f"*{inspection_id}*"))
    if not matches:
        raise HTTPException(status_code=404, detail="Annotated image not found")
    return FileResponse(str(matches[0]), media_type="image/jpeg")