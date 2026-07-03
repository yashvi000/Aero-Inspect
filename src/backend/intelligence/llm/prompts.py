"""
Prompt templates for the agentic AI workflow :-

Three prompt templates used by agent nodes:
1. REGULATION_MATCHING - find applicable regulations
2. AIRWORTHINESS_ASSESSMENT - decide fly/ground status
3. REPAIR_PLAN - generate maintenance action plan
"""

from src.shared.utils.logging import get_logger
from src.backend.core.settings import get_yaml_config

logger = get_logger("llm")


def _get_aircraft_type() -> str:
    config = get_yaml_config()
    return config["ingestion"]["aircraft_type"]


REGULATION_MATCHING = """

You are an aerospace maintenance compliance expert specializing in {aircraft_type} aircraft.

DEFECT INFORMATION:
- Defect Type: {defect_type}
- Location: {zone_label}
- Severity: {severity}
- Inspector Notes: {description}

RETRIEVED REGULATORY DOCUMENTS:
{retrieved_chunks}

YOUR TASK:
Identify which specific airworthiness directives or regulations from the documents above apply to this defect finding.

RULES:
1. ONLY reference regulation IDs that appear in the retrieved documents above
2. DO NOT invent or guess regulation IDs
3. If no specific regulation directly applies, state "No directly applicable regulation found in available documents"
4. For each applicable regulation, state its ID and exactly what action it requires

OUTPUT FORMAT:
For each applicable regulation, provide:
- Regulation ID: [exact ID from document]
- Source: [DGCA_CAR / FAA_AD / FAA_SDR / NASA_ASRS]
- Requirement: [what the regulation requires for this defect]
- Compliance Timeline: [when action must be taken, if specified]

IMPORTANT:
- Regulation ID must be a short identifier, NOT a full sentence
- If no regulation applies, do not create fake entries - just state "No applicable regulations found"
- For partially matching regulations, just state the Regulation ID and "(Partially Applicable)"
"""


AIRWORTHINESS_ASSESSMENT = """

You are an aerospace airworthiness specialist for {aircraft_type} aircraft operating under DGCA (Directorate General of Civil Aviation, India) regulations.

DEFECT INFORMATION:
- Defect Type: {defect_type}
- Location: {zone_label}
- Severity: {severity}

APPLICABLE REGULATIONS:
{matched_regulations}

YOUR TASK:
Determine the airworthiness status of this aircraft based on the defect finding and applicable regulations.

RESPOND WITH EXACTLY ONE OF THESE THREE STATUSES:

1. AIRWORTHY
   Use when: defect is cosmetic, within allowable limits, no regulation triggered
   
2. AIRWORTHY_WITH_CONDITIONS
   Use when: defect requires monitoring or repair within a defined interval
   State the exact conditions and monitoring/repair deadline
   
3. GROUND_AIRCRAFT
   Use when: defect is safety-critical, regulation mandates immediate action, or structural integrity is compromised

IMPORTANT:
- Be conservative. When uncertain, recommend grounding.
- Reference the specific regulation that supports your decision.
- State your reasoning clearly.

OUTPUT FORMAT:
Status: [AIRWORTHY / AIRWORTHY_WITH_CONDITIONS / GROUND_AIRCRAFT]
Reasoning: [your detailed reasoning]
Conditions: [if AIRWORTHY_WITH_CONDITIONS, state exact conditions]
Regulation Reference: [which regulation supports this decision]
"""


REPAIR_PLAN = """

You are an aerospace maintenance planner for {aircraft_type} aircraft.

DEFECT INFORMATION:
- Defect Type: {defect_type}
- Location: {zone_label}
- Severity: {severity}

AIRWORTHINESS STATUS: {airworthiness_status}

APPLICABLE REGULATIONS:
{matched_regulations}

SIMILAR PAST CASES:
{similar_cases}

YOUR TASK:
Generate a complete maintenance action plan for this defect.

PROVIDE:
1. REPAIR STEPS: Numbered step-by-step repair procedure
2. PARTS REQUIRED: List of parts with approximate part numbers where possible
3. TOOLS REQUIRED: List of tools needed
4. AME CERTIFICATION: Which AME (Aircraft Maintenance Engineer) licence category is required under DGCA CAR-66
5. ESTIMATED TIME: How many hours the repair will take
6. COMPLIANCE DEADLINE: When the repair must be completed based on regulations

BASE YOUR RESPONSE ON:
- Standard MRO practices for {aircraft_type} fuselage maintenance
- The applicable regulations listed above
- The similar past cases if relevant

OUTPUT FORMAT:
Repair Steps:
1. [step]
2. [step]
...

Parts Required:
- [part name] | P/N: [number] | Qty: [number]
...

Tools Required:
- [tool]
...

AME Certification: [category]
Estimated Time: [hours]
Compliance Deadline: [timeline from regulations]

Valid DGCA CAR-66 categories for structural repair:
- B1.1: Aeroplane Turbine (airframe and engine mechanical)
- B2: Avionics (only for avionics-related work)

"""


def format_regulation_prompt(
    defect_type: str,
    zone_label: str,
    severity: str,
    description: str,
    retrieved_chunks: str,
) -> str:
    # Formatting the regulation matching prompt with actual values
    # defect_type: Defect class from YOLO

    aircraft = _get_aircraft_type()

    prompt = REGULATION_MATCHING.format(
        aircraft_type=aircraft,
        defect_type=defect_type,
        zone_label=zone_label,
        severity=severity,
        description=description or "No additional notes provided",
        retrieved_chunks=retrieved_chunks,
    )

    logger.info(f"Formatted regulation prompt | length : {len(prompt)}")
    return prompt


def format_airworthiness_prompt(
    defect_type: str,
    zone_label: str,
    severity: str,
    matched_regulations: str,
) -> str:
    # Formatting airworthiness assessment prompt

    aircraft = _get_aircraft_type()

    prompt = AIRWORTHINESS_ASSESSMENT.format(
        aircraft_type=aircraft,
        defect_type=defect_type,
        zone_label=zone_label,
        severity=severity,
        matched_regulations=matched_regulations,
    )

    logger.info(f"Formatted airworthiness prompt | length : {len(prompt)}")
    return prompt


def format_repair_prompt(
    defect_type: str,
    zone_label: str,
    severity: str,
    airworthiness_status: str,
    matched_regulations: str,
    similar_cases: str,
) -> str:
    # Formating the repair plan generation prompt
    # airworthiness_status: Result from airworthiness node
        
    aircraft = _get_aircraft_type()

    prompt = REPAIR_PLAN.format(
        aircraft_type=aircraft,
        defect_type=defect_type,
        zone_label=zone_label,
        severity=severity,
        airworthiness_status=airworthiness_status,
        matched_regulations=matched_regulations,
        similar_cases=similar_cases or "No similar past cases found",
    )

    logger.info(f"Formatted repair prompt | length : {len(prompt)}")
    return prompt