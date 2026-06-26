from sqlalchemy.orm import Session
from src.backend.db.models.zone import Zone
from src.backend.db.models.detection import DetectionFinding
from src.backend.db.models.inspection import Inspection
import uuid

def get_all_zones(db: Session):
    return db.query(Zone).all()

def get_zone(db: Session, zone_id: str):
    return db.query(Zone).filter(Zone.id == zone_id).first()

def update_zone_status(db: Session, zone_id: str, status: str, color: str, inspection_id: str):
    zone = get_zone(db, zone_id)
    if zone:
        zone.current_status = status
        zone.color = color
        zone.last_inspection_id = inspection_id
        db.commit()
        db.refresh(zone)
    return zone

def get_zone_history(db: Session, zone_id: str):
    return db.query(
        Inspection, DetectionFinding
    ).join(
        DetectionFinding, DetectionFinding.inspection_id == Inspection.id
    ).filter(
        DetectionFinding.zone == zone_id
    ).order_by(
        Inspection.created_at.desc()
    ).all()