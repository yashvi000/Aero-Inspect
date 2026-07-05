from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional
from src.backend.db.session import get_db
from src.backend.inspections import repository
from src.shared.utils.logging import get_logger
from src.backend.intelligence.service import generate_documents

logger = get_logger("reports")
router = APIRouter(prefix="/api/reports", tags=["Reports"])

class GenerateReportsRequest(BaseModel):
    thread_id: str
    inspection_id: str
    inspection_type: str
    ame_name: str
    ame_licence: str
    ame_employee_id: str
    organization: Optional[str] = None

@router.post("/generate")
def generate_reports(request: GenerateReportsRequest, db: Session = Depends(get_db)):
    try:
        inspection_data = {
            "inspection_id": request.inspection_id,
            "inspection_type": request.inspection_type,
            "ame_name": request.ame_name,
            "ame_licence": request.ame_licence,
            "ame_employee_id": request.ame_employee_id,
            "organization": request.organization,
        }
        result = generate_documents(
            thread_id=request.thread_id,
            inspection_data=inspection_data
        )
        if result.get("error"):
            raise HTTPException(status_code=500, detail=result["error"])
        # Save paths to DB
        if result.get("defect_report_path") and result.get("work_order_path"):
            repository.save_report(
                db, request.inspection_id,
                result["defect_report_path"],
                result["work_order_path"]
            )
        logger.info(f"Reports generated for inspection {request.inspection_id}")
        return {
            "defect_report_path": result.get("defect_report_path"),
            "work_order_path": result.get("work_order_path")
        }
    except Exception as e:
        logger.error(f"Report generation error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{inspection_id}/defect-report")
def download_defect_report(inspection_id: str, db: Session = Depends(get_db)):
    report = repository.get_report(db, inspection_id)
    if not report or not report.defect_report_path:
        raise HTTPException(status_code=404, detail="Defect report not found")
    logger.info(f"Serving defect report for inspection {inspection_id}")
    return FileResponse(
        report.defect_report_path,
        media_type="application/pdf",
        filename=f"defect_report_{inspection_id}.pdf"
    )

@router.get("/{inspection_id}/work-order")
def download_work_order(inspection_id: str, db: Session = Depends(get_db)):
    report = repository.get_report(db, inspection_id)
    if not report or not report.work_order_path:
        raise HTTPException(status_code=404, detail="Work order not found")
    logger.info(f"Serving work order for inspection {inspection_id}")
    return FileResponse(
        report.work_order_path,
        media_type="application/pdf",
        filename=f"work_order_{inspection_id}.pdf"
    )