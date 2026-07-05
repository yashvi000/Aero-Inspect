from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from src.backend.db.session import get_db
from src.backend.zones import service
from src.shared.utils.logging import get_logger

logger = get_logger("zones")
router = APIRouter(prefix="/api/zones", tags=["Zones"])

class UpdateZoneStatusRequest(BaseModel):
    status: str

@router.get("")
def get_all_zones(db: Session = Depends(get_db)):
    zones = service.get_all_zones(db)
    return {
        "zones": [
            {
                "id": z.id,
                "code": z.zone_name,
                "zone_label": z.zone_label,
                "status": z.current_status,
                "color": z.color,
                "last_inspected": z.updated_at
            } for z in zones
        ]
    }

@router.get("/{zone_id}/history")
def get_zone_history(zone_id: str, db: Session = Depends(get_db)):
    history = service.get_zone_history(db, zone_id)
    return {
        "zone_id": zone_id,
        "history": [
            {
                "date": inspection.created_at,
                "defect_type": detection.defect_type,
                "defect": detection.defect_type,
                "severity": detection.severity
            } for inspection, detection in history
        ]
    }

@router.put("/{zone_id}")
def update_zone_status(zone_id: str, request: UpdateZoneStatusRequest, db: Session = Depends(get_db)):
    result = service.update_zone_status(db, zone_id, request.status, inspection_id=None)
    if not result:
        raise HTTPException(status_code=404, detail="Zone not found")
    logger.info(f"Zone {zone_id} status updated to {request.status}")
    return {"updated": True}