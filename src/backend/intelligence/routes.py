from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional
from src.backend.db.session import get_db
from src.backend.intelligence.service import (
    start_investigation,
    resume_airworthiness,
    resume_final_review,
    get_investigation_state,
    generate_documents,
)
from src.shared.utils.logging import get_logger

logger = get_logger("intelligence")
router = APIRouter(prefix="/api/investigations", tags=["Investigations"])

class StartInvestigationRequest(BaseModel):
    inspection_id: str
    defect_type: str
    zone_id: str
    zone_label: str
    severity: str
    confidence: float
    description: Optional[str] = None
    inspection_type: str

class ApproveAirworthinessRequest(BaseModel):
    approved: bool
    modified_status: Optional[str] = None

class ApproveFinalRequest(BaseModel):
    approved: bool

class GenerateDocumentsRequest(BaseModel):
    inspection_id: str
    inspection_type: str
    ame_name: str
    ame_licence: str
    ame_employee_id: str
    organization: Optional[str] = None

@router.post("/start")
def start(request: StartInvestigationRequest):
    try:
        defect_input = {
            "defect_type": request.defect_type,
            "zone_id": request.zone_id,
            "zone_label": request.zone_label,
            "severity": request.severity,
            "confidence": request.confidence,
            "description": request.description,
            "inspection_type": request.inspection_type,
        }
        result = start_investigation(defect_input, thread_id=request.inspection_id)
        logger.info(f"Investigation started for inspection {request.inspection_id}")
        return result
    except Exception as e:
        logger.error(f"Error starting investigation: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/{thread_id}/approve-airworthiness")
def approve_airworthiness(thread_id: str, request: ApproveAirworthinessRequest):
    try:
        result = resume_airworthiness(
            thread_id=thread_id,
            approved=request.approved,
            modified_status=request.modified_status
        )
        logger.info(f"Airworthiness approved for thread {thread_id}")
        return result
    except Exception as e:
        logger.error(f"Error approving airworthiness: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/{thread_id}/approve-final")
def approve_final(thread_id: str, request: ApproveFinalRequest):
    try:
        result = resume_final_review(
            thread_id=thread_id,
            approved=request.approved
        )
        logger.info(f"Final review approved for thread {thread_id}")
        return result
    except Exception as e:
        logger.error(f"Error approving final review: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{thread_id}/state")
def get_state(thread_id: str):
    try:
        result = get_investigation_state(thread_id=thread_id)
        return result
    except Exception as e:
        logger.error(f"Error getting investigation state: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/generate-documents")
def generate_docs(request: GenerateDocumentsRequest):
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
            thread_id=request.inspection_id,
            inspection_data=inspection_data
        )
        logger.info(f"Documents generated for inspection {request.inspection_id}")
        return result
    except Exception as e:
        logger.error(f"Error generating documents: {e}")
        raise HTTPException(status_code=500, detail=str(e))