from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from src.backend.db.session import get_db
from src.backend.inspections import repository
from src.shared.utils.logging import get_logger

logger = get_logger("reports")
router = APIRouter(prefix="/api/reports", tags=["Reports"])

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