from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session
from src.backend.db.session import get_db
from src.shared.utils.logging import get_logger

logger = get_logger("detection")
router = APIRouter(prefix="/api/detection", tags=["Detection"])

@router.post("/predict")
async def predict(
    inspection_id: str,
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    """
    Placeholder endpoint for YOLO inference.
    Person 1 will integrate their model here.
    Currently returns mock response.
    """
    try:
        logger.info(f"Detection requested for inspection {inspection_id}")
        # TODO: Person 1 integrates YOLO here
        # from src.backend.detection.infer import run_inference
        # result = run_inference(file)
        return {
            "inspection_id": inspection_id,
            "defect_type": "crack",
            "confidence": 0.87,
            "severity": "HIGH",
            "bounding_box": {"x": 120, "y": 340, "width": 45, "height": 12},
            "zone_id": "zone_08",
            "zone_label": "Fuselage Skin / Plate",
            "message": "Mock response — YOLO integration pending"
        }
    except Exception as e:
        logger.error(f"Detection error: {e}")
        raise HTTPException(status_code=500, detail=str(e))