# Generates Maintenance Work Order as PDF

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
    TableStyle,
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


def generate_work_order(
    final_output: dict,
    inspection_data: dict,
) -> str:
    """
    Generates a Maintenance Work Order PDF

    Args:
        final_output: Compiled output from agent workflow
        inspection_data: Additional inspection metadata

    Returns:
        Absolute path to generated PDF file
    
    """
    
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)

    wo_id = f"WO-{uuid.uuid4().hex[:8].upper()}"
    timestamp = datetime.now().strftime("%d-%m-%Y %H:%M:%S")
    filename = f"work_order_{wo_id}.pdf"
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
        "WOTitle",
        parent=styles["Heading1"],
        fontSize=16,
        alignment=1,
        spaceAfter=10,
    )

    heading_style = ParagraphStyle(
        "WOHeading",
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
    elements.append(Paragraph("MAINTENANCE WORK ORDER", title_style))
    elements.append(Paragraph(organization, ParagraphStyle(
        "Org", parent=styles["Normal"], alignment=1, fontSize=10,
    )))
    elements.append(Spacer(1, 10 * mm))

    # Header table
    header_data = [
        ["Work Order ID", wo_id],
        ["Date Issued", timestamp],
        ["Aircraft Type", aircraft_type],
        ["Inspection ID", inspection_data.get("inspection_id", "N/A")],
        ["Zone", f"{final_output.get('zone_label', 'N/A')} ({final_output.get('zone_id', '')})"],
        ["Defect Type", (final_output.get("defect_type") or "N/A").upper()],
        ["Severity", final_output.get("severity", "N/A")],
        ["Airworthiness Status", final_output.get("airworthiness_status", "N/A")],
    ]

    header_table = Table(header_data, colWidths=[50 * mm, 120 * mm])
    header_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (0, -1), colors.HexColor("#e8edf2")),
        ("FONTNAME", (0, 0), (0, -1), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, -1), 10),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
        ("LEFTPADDING", (0, 0), (-1, -1), 8),
        ("TOPPADDING", (0, 0), (-1, -1), 5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
    ]))
    elements.append(header_table)
    elements.append(Spacer(1, 8 * mm))

    # Regulation references
    elements.append(Paragraph("REGULATION REFERENCES", heading_style))

    regulations = final_output.get("matched_regulations", [])
    if regulations:
        for reg in regulations:
            elements.append(Paragraph(
                f"<b>{reg.get('id', 'N/A')}</b> ({reg.get('source', '')}) - "
                f"{reg.get('requirement', 'see full document')}",
                body_style,
            ))
            elements.append(Spacer(1, 1 * mm))
    else:
        elements.append(Paragraph("No regulations referenced", body_style))

    elements.append(Spacer(1, 5 * mm))

    # Repair procedure
    elements.append(Paragraph("REPAIR PROCEDURE", heading_style))

    steps = final_output.get("repair_steps", [])
    if steps:
        for i, step in enumerate(steps, 1):
            elements.append(Paragraph(f"<b>{i}.</b> {step}", body_style))
            elements.append(Spacer(1, 1 * mm))
    else:
        elements.append(Paragraph(
            "Refer to applicable SRM for repair procedure", body_style,
        ))

    elements.append(Spacer(1, 5 * mm))

    # Parts required
    elements.append(Paragraph("REQUIRED PARTS", heading_style))

    parts = final_output.get("parts_required", [])
    if parts:
        for part in parts:
            elements.append(Paragraph(f"- {part}", body_style))
    else:
        elements.append(Paragraph("To be determined", body_style))

    elements.append(Spacer(1, 5 * mm))

    # Tools required
    elements.append(Paragraph("REQUIRED TOOLS", heading_style))

    tools = final_output.get("tools_required", [])
    if tools:
        for tool in tools:
            elements.append(Paragraph(f"- {tool}", body_style))
    else:
        elements.append(Paragraph("Standard aircraft maintenance toolkit", body_style))

    elements.append(Spacer(1, 5 * mm))

    # Certification and compliance
    elements.append(Paragraph("CERTIFICATION AND COMPLIANCE", heading_style))

    cert_data = [[
            "AME Certification Required",
            Paragraph(
                final_output.get("ame_certification", "B1.1"),
                body_style,
            ),
        ],[
            "Estimated Time",
            f"{final_output.get('estimated_hours', 'N/A')} hours",
        ],[
            "Compliance Deadline",
            Paragraph(
                final_output.get("compliance_deadline", "Not specified"),
                body_style,
            ),
        ],[
            "DGCA Authorization",
            "Work authorized under DGCA CAR-145",
        ]
    ]

    cert_table = Table(cert_data, colWidths=[55 * mm, 115 * mm])
    cert_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (0, -1), colors.HexColor("#e8edf2")),
        ("FONTNAME", (0, 0), (0, -1), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, -1), 10),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
        ("LEFTPADDING", (0, 0), (-1, -1), 8),
        ("TOPPADDING", (0, 0), (-1, -1), 5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
    ]))
    elements.append(cert_table)
    elements.append(Spacer(1, 8 * mm))

    # Sign-off
    elements.append(Paragraph("SIGN-OFF", heading_style))

    signoff_data = [
        ["Performed by (AME)", inspection_data.get("ame_name", "")],
        ["Licence No", inspection_data.get("ame_licence", "")],
        ["Employee ID", inspection_data.get("ame_employee_id", "")],
        ["Date Completed", ""],
        ["Supervisor", ""],
        ["Supervisor Signature", ""],
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

    logger.info(f"Work Order Report generated: {filepath}")
    return str(filepath)