# Generate Defect Analysis Report as PDF
import uuid
from datetime import datetime

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import mm
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle
)

from src.shared.utils.logging import get_logger
from src.shared.utils.paths import REPORTS_DIR
from src.backend.core.settings import get_yaml_config

logger = get_logger("reports")


def _get_organization() -> str:
    config = get_yaml_config()
    return config.get("reports", {}).get(
        "organization", "MRO Organization"
    )


def _get_aircraft_type() -> str:
    config = get_yaml_config()
    return config["ingestion"]["aircraft_type"]


def generate_defect_report(
    final_output: dict,
    inspection_data: dict,
) -> str:
    """
    Generates Defect Analysis Report PDF
    
    Args:
        final_output: Compiled output from agent workflow
        inspection_data: Additional inspection metadata

    Returns:
        Absolute path to generated PDF file

    """

    REPORTS_DIR.mkdir(parents=True, exist_ok=True)

    report_id = f"DAR-{uuid.uuid4().hex[:8].upper()}"
    timestamp = datetime.now().strftime("%d-%m-%Y %H:%M:%S")
    filename = f"defect_report_{report_id}.pdf"
    filepath = REPORTS_DIR / filename

    organization = inspection_data.get("organization") or _get_organization()
    aircraft_type = _get_aircraft_type()

    doc = SimpleDocTemplate(
        str(filepath),
        pagesize=A4,
        topMargin=20 * mm,
        bottomMargin=20 * mm,
        leftMargin=15 * mm,
        rightMargin=15 * mm,
    )

    styles = getSampleStyleSheet()

    title_style = ParagraphStyle(
        "ReportTitle",
        parent=styles["Heading1"],
        fontSize=16,
        alignment=1,
        spaceAfter=10,
    )

    heading_style = ParagraphStyle(
        "SectionHeading",
        parent=styles["Heading2"],
        fontSize=12,
        spaceBefore=15,
        spaceAfter=5,
        textColor=colors.HexColor("#1a3c5e"),
    )

    body_style = styles["Normal"]
    body_style.fontSize = 10
    body_style.leading = 14

    elements = []

    # Title
    elements.append(Paragraph("DEFECT ANALYSIS REPORT", title_style))
    elements.append(Paragraph(organization, ParagraphStyle(
        "Org", parent=styles["Normal"], alignment=1, fontSize=10,
    )))
    elements.append(Spacer(1, 10 * mm))

    # Header table
    header_data = [
        ["Report ID", report_id],
        ["Date", timestamp],
        ["Inspection ID", inspection_data.get("inspection_id", "N/A")],
        ["Aircraft Type", aircraft_type],
        ["Inspection Type", inspection_data.get("inspection_type", "N/A")],
        ["Zone", f"{final_output.get('zone_label', 'N/A')} ({final_output.get('zone_id', '')})"],
    ]

    header_table = Table(header_data, colWidths=[50 * mm, 120 * mm])
    header_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (0, -1), colors.HexColor("#e8edf2")),
        ("FONTNAME", (0, 0), (0, -1), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, -1), 10),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("LEFTPADDING", (0, 0), (-1, -1), 8),
        ("TOPPADDING", (0, 0), (-1, -1), 5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
    ]))
    elements.append(header_table)
    elements.append(Spacer(1, 8 * mm))

    # Detection results
    elements.append(Paragraph("DEFECT DETECTION RESULTS", heading_style))

    detection_data = [
        ["Defect Type", (final_output.get("defect_type") or "N/A").upper()],
        ["Confidence", f"{(final_output.get('confidence') or 0) * 100:.1f}%"],
        ["Severity", final_output.get("severity", "N/A")],
        ["Detection Method", "YOLOv11n Visual Inspection"],
    ]

    detection_table = Table(detection_data, colWidths=[50 * mm, 120 * mm])
    detection_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (0, -1), colors.HexColor("#e8edf2")),
        ("FONTNAME", (0, 0), (0, -1), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, -1), 10),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
        ("LEFTPADDING", (0, 0), (-1, -1), 8),
        ("TOPPADDING", (0, 0), (-1, -1), 5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
    ]))
    elements.append(detection_table)
    elements.append(Spacer(1, 5 * mm))

    # Regulations
    elements.append(Paragraph("APPLICABLE REGULATIONS", heading_style))

    regulations = final_output.get("matched_regulations", [])
    if regulations:
        reg_header = [[
            Paragraph("<b>Regulation ID</b>", body_style),
            Paragraph("<b>Source</b>", body_style),
            Paragraph("<b>Requirement</b>", body_style),
        ]]
        
        reg_rows = []
        for reg in regulations:
            reg_rows.append([
                Paragraph(reg.get("id", "N/A"), body_style),
                Paragraph(reg.get("source", "N/A"), body_style),
                Paragraph(reg.get("requirement", "N/A"), body_style),
            ])

        reg_table = Table(
            reg_header + reg_rows,
            colWidths=[40 * mm, 25 * mm, 105 * mm],
        )
        reg_table.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1a3c5e")),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ("FONTSIZE", (0, 0), (-1, -1), 9),
            ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
            ("VALIGN", (0, 0), (-1, -1), "TOP"),
            ("LEFTPADDING", (0, 0), (-1, -1), 5),
            ("TOPPADDING", (0, 0), (-1, -1), 4),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
        ]))
        elements.append(reg_table)
    else:
        elements.append(Paragraph(
            "No directly applicable regulations found", body_style,
        ))

    elements.append(Spacer(1, 5 * mm))

    # Airworthiness
    elements.append(Paragraph("AIRWORTHINESS DETERMINATION", heading_style))

    status = final_output.get("airworthiness_status", "GROUND_AIRCRAFT")
    status_color = {
        "AIRWORTHY": "#27ae60",
        "AIRWORTHY_WITH_CONDITIONS": "#f39c12",
        "GROUND_AIRCRAFT": "#cf311f",
    }.get(status, "#cf311f")

    elements.append(Paragraph(
        f"<b>Status : <font color='{status_color}'>{status}</font></b>",
        body_style,
    ))
    elements.append(Spacer(1, 2 * mm))
    elements.append(Paragraph(
        f"<b>Reasoning :</b> {final_output.get('airworthiness_reasoning', 'N/A')}",
        body_style,
    ))

    if final_output.get("airworthiness_conditions", "none") != "none":
        elements.append(Paragraph(
            f"<b>Conditions :</b> {final_output.get('airworthiness_conditions')}",
            body_style,
        ))

    if final_output.get("human_override_applied"):
        elements.append(Spacer(1, 2 * mm))
        elements.append(Paragraph(
            "<i>Note : Airworthiness status was modified by the inspector</i>",
            body_style,
        ))

    elements.append(Spacer(1, 5 * mm))

    # Recommended action
    elements.append(Paragraph("RECOMMENDED ACTION", heading_style))
    elements.append(Paragraph(
        f"Compliance Deadline: {final_output.get('compliance_deadline', 'Not specified')}",
        body_style,
    ))
    elements.append(Spacer(1, 8 * mm))

    # Sign-off
    elements.append(Paragraph("INSPECTOR SIGN-OFF", heading_style))

    signoff_data = [
        ["Inspector Name", inspection_data.get("ame_name", "")],
        ["Employee ID", inspection_data.get("ame_employee_id", "")],
        ["AME Licence", inspection_data.get("ame_licence", "")],
        ["Date", timestamp],
        ["Signature", ""],
    ]

    signoff_table = Table(signoff_data, colWidths=[50 * mm, 120 * mm])
    signoff_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (0, -1), colors.HexColor("#e8edf2")),
        ("FONTNAME", (0, 0), (0, -1), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, -1), 10),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
        ("LEFTPADDING", (0, 0), (-1, -1), 8),
        ("TOPPADDING", (0, 0), (-1, -1), 5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
    ]))
    elements.append(signoff_table)

    doc.build(elements)

    logger.info(f"Defect Report generated: {filepath}")
    return str(filepath)