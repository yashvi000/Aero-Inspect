# Intelligence service entry point

from src.shared.utils.logging import get_logger
from src.backend.intelligence.agent.workflow import (
    run_investigation,
    resume_after_airworthiness,
    resume_after_final_review,
    get_current_state,
)
from src.backend.reports.service import generate_all_reports

logger = get_logger("service")


def start_investigation(defect_input: dict, thread_id: str) -> dict:
    # Starts a new investigation workflow
    # Runs till checkpoint 1 - airworthiness review
    
    logger.info(f"Starting Investigation | thread : {thread_id}")

    state = run_investigation(defect_input, thread_id)
    return _summarize_state(state, "checkpoint_airworthiness")


def resume_airworthiness(
    thread_id: str,
    approved: bool,
    modified_status: str = None,
) -> dict:
    # Resumes after airworthiness, runs till checkpoint 2 - repair review
    logger.info(f"Resuming after Airworthiness | thread : {thread_id}")

    state = resume_after_airworthiness(thread_id, approved, modified_status)
    return _summarize_state(state, "checkpoint_final_review")


def resume_final_review(
    thread_id: str,
    approved: bool,
) -> dict:
    # Resumes after repair, runs report generation
    logger.info(f"Resuming final review | thread : {thread_id}")

    state = resume_after_final_review(thread_id, approved)
    return _summarize_state(state, "complete")


def get_investigation_state(thread_id: str) -> dict:
    # Gets current state of an investigation
   
    state = get_current_state(thread_id)
    return _summarize_state(state, "unknown")


def generate_documents(
    thread_id: str,
    inspection_data: dict,
) -> dict:
    # Generates PDF reports after final approval
    # thread_id: Investigation thread ID

    logger.info(f"Generating reports | thread : {thread_id}")

    state = get_current_state(thread_id)
    final_output = state.get("final_output")

    if not final_output:
        logger.error(f"No final output for thread {thread_id}")
        return {
            "defect_report_path": None,
            "work_order_path": None,
            "error": "Investigation not complete",
        }

    paths = generate_all_reports(final_output, inspection_data)

    logger.info(
        f"Reports generated | "
        f"defect_report : {paths.get('defect_report_path')} | "
        f"work_order : {paths.get('work_order_path')}"
    )
    return paths


def _summarize_state(state: dict, paused_at: str) -> dict:
    # Extracts key fields from agent state for API response
    
    return {
        "paused_at": paused_at,
        "parsed_regulations": state.get("parsed_regulations"),
        "parsed_airworthiness": state.get("parsed_airworthiness"),
        "parsed_repair": state.get("parsed_repair"),
        "final_output": state.get("final_output"),
        "human_override_applied": state.get("human_modified_status") is not None,
        "error": state.get("error"),
    }