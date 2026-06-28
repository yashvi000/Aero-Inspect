from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional
from src.backend.db.session import get_db
from src.backend.inspections import service
from src.shared.utils.paths import REPORTS_DIR

router = APIRouter(prefix="/inspections", tags=["Inspections"])

class CreateInspectionRequest(BaseModel):
    aircraft_type: str
    notes: Optional[str] = None

class ApproveRequest(BaseModel):
    approved_by: str

# 1. Create inspection
@router.post("")
def create_inspection(request: CreateInspectionRequest, db: Session = Depends(get_db)):
    inspection = service.create_inspection(db, request.aircraft_type, request.notes)
    return {
        "inspection_id": inspection.id,
        "status": inspection.status,
        "created_at": inspection.created_at
    }

# 2. Upload image
@router.post("/{inspection_id}/upload")
def upload_image(inspection_id: str, file: UploadFile = File(...), db: Session = Depends(get_db)):
    inspection = service.get_inspection(db, inspection_id)
    if not inspection:
        raise HTTPException(status_code=404, detail="Inspection not found")
    file_path = service.save_image(inspection_id, file)
    service.update_status(db, inspection_id, "DETECTING")
    return {
        "status": "DETECTING",
        "image_path": file_path,
        "message": "Image uploaded, detection in progress"
    }

# 3. Get detection result
@router.get("/{inspection_id}/detection")
def get_detection(inspection_id: str, db: Session = Depends(get_db)):
    inspection = service.get_inspection(db, inspection_id)
    if not inspection:
        raise HTTPException(status_code=404, detail="Inspection not found")
    existing = service.get_detection(db, inspection_id)
    if existing:
        return {
            "status": "DETECTION_COMPLETE",
            "defect_type": existing.defect_type,
            "confidence": existing.confidence,
            "severity": existing.severity,
            "bounding_box": {
                "x": existing.bbox_x,
                "y": existing.bbox_y,
                "width": existing.bbox_w,
                "height": existing.bbox_h
            },
            "zone": existing.zone
        }
    mock = service.get_mock_detection()
    service.save_detection(db, inspection_id, mock)
    service.update_status(db, inspection_id, "DETECTION_COMPLETE")
    return {"status": "DETECTION_COMPLETE", **mock}

# 4. Approve detection
@router.post("/{inspection_id}/approve-detection")
def approve_detection(inspection_id: str, request: ApproveRequest, db: Session = Depends(get_db)):
    inspection = service.get_inspection(db, inspection_id)
    if not inspection:
        raise HTTPException(status_code=404, detail="Inspection not found")
    service.update_status(db, inspection_id, "INVESTIGATING")
    return {
        "status": "INVESTIGATING",
        "approved_by": request.approved_by,
        "message": "Detection approved, agent investigating"
    }

# 5. Get agent result
@router.get("/{inspection_id}/agent-result")
def get_agent_result(inspection_id: str, db: Session = Depends(get_db)):
    inspection = service.get_inspection(db, inspection_id)
    if not inspection:
        raise HTTPException(status_code=404, detail="Inspection not found")
    existing = service.get_agent_finding(db, inspection_id)
    if existing:
        return {
            "status": "AGENT_COMPLETE",
            "probable_causes": existing.probable_causes,
            "regulation_refs": existing.regulation_refs,
            "airworthiness_status": existing.airworthiness_status,
            "recommended_action": existing.recommended_action,
            "repair_steps": existing.repair_steps
        }
    mock = service.get_mock_agent_result()
    service.save_agent_finding(db, inspection_id, mock)
    service.update_status(db, inspection_id, "AGENT_COMPLETE")
    return {"status": "AGENT_COMPLETE", **mock}

# 6. Approve findings
@router.post("/{inspection_id}/approve-findings")
def approve_findings(inspection_id: str, request: ApproveRequest, db: Session = Depends(get_db)):
    inspection = service.get_inspection(db, inspection_id)
    if not inspection:
        raise HTTPException(status_code=404, detail="Inspection not found")
    service.update_status(db, inspection_id, "FINDINGS_APPROVED")
    return {
        "status": "FINDINGS_APPROVED",
        "approved_by": request.approved_by,
        "message": "Ready to generate reports"
    }

# 7. Generate reports
@router.post("/{inspection_id}/generate-reports")
def generate_reports(inspection_id: str, db: Session = Depends(get_db)):
    inspection = service.get_inspection(db, inspection_id)
    if not inspection:
        raise HTTPException(status_code=404, detail="Inspection not found")
    defect_path = str(REPORTS_DIR / f"defect_report_{inspection_id}.pdf")
    work_order_path = str(REPORTS_DIR / f"work_order_{inspection_id}.pdf")
    service.save_report(db, inspection_id, defect_path, work_order_path)
    service.update_status(db, inspection_id, "COMPLETE")
    return {
        "status": "COMPLETE",
        "message": "Reports generated successfully"
    }

# 8. Download defect report
@router.get("/{inspection_id}/reports/defect")
def download_defect_report(inspection_id: str, db: Session = Depends(get_db)):
    report = service.get_report(db, inspection_id)
    if not report or not report.defect_report_path:
        raise HTTPException(status_code=404, detail="Report not found")
    return FileResponse(
        report.defect_report_path,
        media_type="application/pdf",
        filename=f"defect_report_{inspection_id}.pdf"
    )

# 9. Download work order
@router.get("/{inspection_id}/reports/work-order")
def download_work_order(inspection_id: str, db: Session = Depends(get_db)):
    report = service.get_report(db, inspection_id)
    if not report or not report.work_order_path:
        raise HTTPException(status_code=404, detail="Report not found")
    return FileResponse(
        report.work_order_path,
        media_type="application/pdf",
        filename=f"work_order_{inspection_id}.pdf"
    )

# 10. Get all inspections
@router.get("")
def get_all_inspections(page: int = 1, per_page: int = 20, db: Session = Depends(get_db)):
    total, inspections = service.get_all_inspections(db, page, per_page)
    return {
        "total": total,
        "page": page,
        "per_page": per_page,
        "inspections": [
            {
                "inspection_id": i.id,
                "aircraft_type": i.aircraft_type,
                "status": i.status,
                "created_at": i.created_at
            } for i in inspections
        ]
    }