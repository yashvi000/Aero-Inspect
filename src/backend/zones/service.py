from sqlalchemy.orm import Session
from src.backend.zones import repository

def get_all_zones(db: Session):
    return repository.get_all_zones(db)

def get_zone_history(db: Session, zone_id: str):
    return repository.get_zone_history(db, zone_id)

def update_zone_status(db: Session, zone_id: str, status: str, inspection_id: str):
    color_map = {
        "NORMAL": "GREEN",
        "WARNING": "AMBER",
        "DEFECT_FOUND": "RED",
        "NOT_INSPECTED": "GRAY"
    }
    color = color_map.get(status, "GRAY")
    return repository.update_zone_status(db, zone_id, status, color, inspection_id)