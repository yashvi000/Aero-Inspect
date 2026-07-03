from sqlalchemy.orm import Session
from src.backend.db.models.inspection import Inspection
from src.backend.db.models.detection import DetectionFinding
from src.backend.db.models.investigation import AgentFinding
from src.backend.db.models.report import Report
import uuid

def create_inspection(db: Session, aircraft_type: str, notes: str = None, zone_id: str = None, inspection_type: str = None):
    inspection = Inspection(
        id=str(uuid.uuid4()),
        aircraft_type=aircraft_type,
        notes=notes,
        zone_id=zone_id,
        inspection_type=inspection_type,
        status="CREATED"
    )
    db.add(inspection)
    db.commit()
    db.refresh(inspection)
    return inspection

def get_inspection(db: Session, inspection_id: str):
    return db.query(Inspection).filter(Inspection.id == inspection_id).first()

def get_all_inspections(db: Session, page: int = 1, per_page: int = 20):
    offset = (page - 1) * per_page
    total = db.query(Inspection).count()
    inspections = db.query(Inspection).order_by(Inspection.created_at.desc()).offset(offset).limit(per_page).all()
    return total, inspections

def update_inspection_status(db: Session, inspection_id: str, status: str):
    inspection = get_inspection(db, inspection_id)
    if inspection:
        inspection.status = status
        db.commit()
        db.refresh(inspection)
    return inspection

def save_detection(db: Session, inspection_id: str, defect_type: str, confidence: float, severity: str, bbox: dict, zone: str):
    finding = DetectionFinding(
        id=str(uuid.uuid4()),
        inspection_id=inspection_id,
        defect_type=defect_type,
        confidence=confidence,
        severity=severity,
        bbox_x=bbox.get("x"),
        bbox_y=bbox.get("y"),
        bbox_w=bbox.get("width"),
        bbox_h=bbox.get("height"),
        zone=zone
    )
    db.add(finding)
    db.commit()
    db.refresh(finding)
    return finding

def get_detection(db: Session, inspection_id: str):
    return db.query(DetectionFinding).filter(DetectionFinding.inspection_id == inspection_id).first()

def save_agent_finding(db: Session, inspection_id: str, data: dict):
    finding = AgentFinding(
        id=str(uuid.uuid4()),
        inspection_id=inspection_id,
        probable_causes=data.get("probable_causes"),
        regulation_refs=data.get("regulation_refs"),
        airworthiness_status=data.get("airworthiness_status"),
        recommended_action=data.get("recommended_action"),
        repair_steps=data.get("repair_steps")
    )
    db.add(finding)
    db.commit()
    db.refresh(finding)
    return finding

def get_agent_finding(db: Session, inspection_id: str):
    return db.query(AgentFinding).filter(AgentFinding.inspection_id == inspection_id).first()

def save_report(db: Session, inspection_id: str, defect_path: str, work_order_path: str):
    report = Report(
        id=str(uuid.uuid4()),
        inspection_id=inspection_id,
        defect_report_path=defect_path,
        work_order_path=work_order_path
    )
    db.add(report)
    db.commit()
    db.refresh(report)
    return report

def get_report(db: Session, inspection_id: str):
    return db.query(Report).filter(Report.inspection_id == inspection_id).first()