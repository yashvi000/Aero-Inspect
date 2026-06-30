# Parses raw LLM text responses into structured Python dicts

import re
from src.shared.utils.logging import get_logger
from src.backend.core.settings import get_yaml_config

logger = get_logger("llm")

def _get_airworthiness_statuses() -> str:
    config = get_yaml_config()
    return config["llm"]["valid_airworthiness_statuses"]


def parse_regulations(raw_response: str) -> list[dict]:
    """
    Parsing regulation matching LLM response into list of regulation dicts

    Returns:
        [id, source, requirement, compliance_timeline]

    Expected LLM output format:
    - Regulation ID: AD 2015-21-06
    - Source: FAA_AD
    - Requirement: Inspect lap joints for cracking
    - Compliance Timeline: Within 500 flight cycles

    """

    if not raw_response or not raw_response.strip():
        logger.warning("Empty response for regulation parsing")
        return []

    regulations = []
    current_reg = {}

    for line in raw_response.split("\n"):
        line = line.strip()

        if not line:
            if current_reg and current_reg.get("id"):
                regulations.append(current_reg)
                current_reg = {}
            continue

        lower_line = line.lower()

        if "regulation id:" in lower_line or "- regulation id:" in lower_line:
            if current_reg and current_reg.get("id"):
                regulations.append(current_reg)
            current_reg = {}
            current_reg["id"] = _extract_value(line)

        elif "source:" in lower_line:
            current_reg["source"] = _extract_value(line)

        elif "requirement:" in lower_line:
            current_reg["requirement"] = _extract_value(line)

        elif "compliance timeline:" in lower_line or "compliance:" in lower_line:
            current_reg["compliance_timeline"] = _extract_value(line)

    if current_reg and current_reg.get("id"):
        regulations.append(current_reg)

    # Filling missing fields with defaults
    for reg in regulations:
        reg.setdefault("id", "unknown")
        reg.setdefault("source", "unknown")
        reg.setdefault("requirement", "see full document")
        reg.setdefault("compliance_timeline", "not specified")

    logger.info(f"Parsed {len(regulations)} regulations from LLM response")
    return regulations


def parse_airworthiness(raw_response: str) -> dict:
    """
    Parsing airworthiness assessment LLM response

    Returns:
        [status, reasoning, conditions, regulation_reference]
    
    Expected LLM output format:
    - Status: AIRWORTHY_WITH_CONDITIONS
    - Reasoning: The crack is below critical threshold...
    - Conditions: Reinspect within 200 flight cycles
    - Regulation Reference: AD 2015-21-06

    """
    if not raw_response or not raw_response.strip():
        logger.warning("Empty response for airworthiness parsing")
        return {
            "status": "GROUND_AIRCRAFT",
            "reasoning": "Unable to determine airworthiness - defaulting to ground",
            "conditions": "none",
            "regulation_reference": "none"
        }

    result = {
        "status": "GROUND_AIRCRAFT",
        "reasoning": "",
        "conditions": "none",
        "regulation_reference": "none"
    }

    for line in raw_response.split("\n"):
        line = line.strip()
        lower_line = line.lower()

        if lower_line.startswith("status:"):
            status_text = _extract_value(line).upper().replace(" ", "_")
            if status_text in _get_airworthiness_statuses():
                result["status"] = status_text
            
            else:
                for valid_status in _get_airworthiness_statuses():
                    if valid_status.lower().replace("_", " ") in lower_line:
                        result["status"] = valid_status
                        break

        elif lower_line.startswith("reasoning:"):
            result["reasoning"] = _extract_value(line)

        elif lower_line.startswith("conditions:") or lower_line.startswith("condition:"):
            result["conditions"] = _extract_value(line)

        elif lower_line.startswith("regulation reference:") or lower_line.startswith("regulation:"):
            result["regulation_reference"] = _extract_value(line)

    # Full response if reasoning is empty 
    if not result["reasoning"]:
        result["reasoning"] = raw_response.strip()[:500]

    logger.info(f"Parsed airworthiness - status : {result['status']}")
    return result


def parse_repair_plan(raw_response: str) -> dict:
    """
    Parsing repair plan LLM response

    Returns:
        [repair_steps, parts_required, tools_required, ame_certification, 
        estimated_hours, compliance_deadline]

    Expected LLM output format:
    Repair Steps:
    1. Clean affected area
    2. Remove corrosion
    ...
    Parts Required:
    - Doubler plate | P/N: 737-51-442 | Qty: 1
    ...
    Tools Required:
    - Orbital sander
    ...
    AME Certification: Category B1.1
    Estimated Time: 4 hours
    Compliance Deadline: Within 500 flight cycles

    """
    if not raw_response or not raw_response.strip():
        logger.warning("Empty response for repair plan parsing")
        return _empty_repair_plan()

    result = {
        "repair_steps": [],
        "parts_required": [],
        "tools_required": [],
        "ame_certification": "Category B1 - Airframe",
        "estimated_hours": 0,
        "compliance_deadline": "not specified"
    }

    current_section = None

    for line in raw_response.split("\n"):
        line = line.strip()

        if not line:
            continue

        lower_line = line.lower()

        if "repair steps:" in lower_line or "repair procedure:" in lower_line:
            current_section = "steps"
            continue
        elif "parts required:" in lower_line or "parts:" in lower_line:
            current_section = "parts"
            continue
        elif "tools required:" in lower_line or "tools:" in lower_line:
            current_section = "tools"
            continue
        elif "ame certification:" in lower_line or "ame licence:" in lower_line:
            result["ame_certification"] = _extract_value(line)
            current_section = None
            continue
        elif "estimated time:" in lower_line:
            result["estimated_hours"] = _extract_hours(line)
            current_section = None
            continue
        elif "compliance deadline:" in lower_line:
            result["compliance_deadline"] = _extract_value(line)
            current_section = None
            continue

        if current_section == "steps":
            step = _clean_list_item(line)
            if step:
                result["repair_steps"].append(step)

        elif current_section == "parts":
            part = _clean_list_item(line)
            if part:
                result["parts_required"].append(part)

        elif current_section == "tools":
            tool = _clean_list_item(line)
            if tool:
                result["tools_required"].append(tool)

    # Defaults
    if not result["repair_steps"]:
        result["repair_steps"] = ["Refer applicable SRM for repair procedure"]

    if not result["parts_required"]:
        result["parts_required"] = ["To be determined based on damage assessment"]

    if not result["tools_required"]:
        result["tools_required"] = ["Standard aircraft maintenance toolkit"]

    logger.info(
        f"Parsed repair plan : "
        f"{len(result['repair_steps'])} steps | "
        f"{len(result['parts_required'])} parts | "
        f"{len(result['tools_required'])} tools"
    )
    return result



def _extract_value(line: str) -> str:
    # Extracting value after first colon in a line
    if ":" in line:
        return line.split(":", 1)[1].strip()
    return line.strip()


def _clean_list_item(line: str) -> str:
    # Removing bullets, numbers, dashes from list item
    cleaned = re.sub(r'^[\d]+[.)]\s*', '', line)
    cleaned = re.sub(r'^[-•*]\s*', '', cleaned)
    return cleaned.strip()


def _extract_hours(line: str) -> float:
    # Extracting hours from lines like 'Estimated Time: 4 hours'
    numbers = re.findall(r'[\d.]+', line)
    if numbers:
        try:
            return float(numbers[0])
        except ValueError:
            return 0
    return 0


def _empty_repair_plan() -> dict:
    # Empty repair plan with safe defaults
    return {
        "repair_steps": ["Unable to generate repair plan"],
        "parts_required": ["To be determined"],
        "tools_required": ["Standard toolkit"],
        "ame_certification": "Category B1 - Airframe",
        "estimated_hours": 0,
        "compliance_deadline": "not specified"
    }