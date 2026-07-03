from src.shared.utils.logging import get_logger
from src.backend.reports.defect_report import generate_defect_report
from src.backend.reports.work_order import generate_work_order

logger = get_logger("reports")


def generate_all_reports(
    final_output: dict,
    inspection_data: dict,
) -> dict:
    """
    Generates both PDF reports

    Args:
        final_output: Compiled output from agent workflow
        inspection_data: Dict containing:
            - inspection_id: str
            - inspection_type: str (GVI/DVI/SDI)
            - ame_name: str
            - ame_licence: str
            - ame_employee_id: str
            - organization: str (optional)

    Returns:
        Dict with:
            defect_report_path: str or None
            work_order_path: str or None
            error: str or None
    """

    result = {
        "defect_report_path": None,
        "work_order_path": None,
        "error": None,
    }

    try:
        result["defect_report_path"] = generate_defect_report(
            final_output, inspection_data
        )
    except Exception as e:
        logger.error(f"Failed to generate defect report: {e}")
        result["error"] = f"Defect report failed: {str(e)}"

    try:
        result["work_order_path"] = generate_work_order(
            final_output, inspection_data
        )
    except Exception as e:
        logger.error(f"Failed to generate work order: {e}")
        
        if result["error"]:
            result["error"] += f" | Work order failed: {str(e)}"
        else:
            result["error"] = f"Work order failed: {str(e)}"

    if result["defect_report_path"] and result["work_order_path"]:
        logger.info("Both reports generated successfully")
    else:
        logger.warning("One or both reports failed to generate")
    return result