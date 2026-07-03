import shutil
from sqlalchemy.orm import Session
from src.backend.inspections import repository
from src.shared.utils.paths import UPLOADS_DIR, ensure_dirs
from src.shared.constants.defect_classes import DefectClass
from src.shared.constants.severity_levels import SeverityLevel
from src.shared.constants.airworthiness_statuses import AirworthinessStatus

ensure_dirs()
UPLOAD_DIR = UPLOADS_DIR

def create_inspection(db: Session, aircraft_type: str, notes: str = None, zone_id: str = None, inspection_type: str = None):
    return repository.create_inspection(db, aircraft_type, notes, zone_id, inspection_type)

def get_inspection(db: Session, inspection_id: str):
    return repository.get_inspection(db, inspection_id)

def get_all_inspections(db: Session, page: int = 1, per_page: int = 20):
    return repository.get_all_inspections(db, page, per_page)

def save_image(inspection_id: str, file):
    file_path = str(UPLOAD_DIR / f"{inspection_id}_{file.filename}")
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    return file_path

def update_status(db: Session, inspection_id: str, status: str):
    return repository.update_inspection_status(db, inspection_id, status)

def get_mock_detection():
    return {
        "defect_type": DefectClass.CRACK,
        "confidence": 0.87,
        "severity": SeverityLevel.HIGH,
        "bounding_box": {"x": 120, "y": 340, "width": 45, "height": 12},
        "zone": "zone_08"
    }

def get_mock_agent_result():
    return {
        "probable_causes": ["Metal fatigue", "Impact damage"],
        "regulation_refs": ["CAR-M Section 2.1.1", "FAA AD 2024-15-03"],
        "airworthiness_status": AirworthinessStatus.UNAIRWORTHY,
        "recommended_action": "Ground aircraft immediately",
        "repair_steps": ["Remove panel", "Perform NDT", "Consult licensed AME"]
    }

def save_detection(db: Session, inspection_id: str, detection: dict):
    return repository.save_detection(
        db, inspection_id,
        defect_type=detection["defect_type"],
        confidence=detection["confidence"],
        severity=detection["severity"],
        bbox=detection["bounding_box"],
        zone=detection["zone"]
    )

def get_detection(db: Session, inspection_id: str):
    return repository.get_detection(db, inspection_id)

def save_agent_finding(db: Session, inspection_id: str, data: dict):
    return repository.save_agent_finding(db, inspection_id, data)

def get_agent_finding(db: Session, inspection_id: str):
    return repository.get_agent_finding(db, inspection_id)

def save_report(db: Session, inspection_id: str, defect_path: str, work_order_path: str):
    return repository.save_report(db, inspection_id, defect_path, work_order_path)

def get_report(db: Session, inspection_id: str):
    return repository.get_report(db, inspection_id)