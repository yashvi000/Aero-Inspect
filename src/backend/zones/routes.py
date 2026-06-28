from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from src.backend.db.session import get_db
from src.backend.zones import service

router = APIRouter(prefix="/zones", tags=["Zones"])

# 11. Get all zones
@router.get("")
def get_all_zones(db: Session = Depends(get_db)):
    zones = service.get_all_zones(db)
    return {
        "zones": [
            {
                "zone_id": z.id,
                "zone_name": z.zone_name,
                "zone_label": z.zone_label,
                "current_status": z.current_status,
                "color": z.color,
                "updated_at": z.updated_at
            } for z in zones
        ]
    }

# 12. Get zone history
@router.get("/{zone_id}/history")
def get_zone_history(zone_id: str, db: Session = Depends(get_db)):
    history = service.get_zone_history(db, zone_id)
    return {
        "zone_id": zone_id,
        "history": [
            {
                "inspection_id": inspection.id,
                "date": inspection.created_at,
                "defect_type": detection.defect_type,
                "severity": detection.severity,
                "airworthiness_status": inspection.status
            } for inspection, detection in history
        ]
    }