"""
Agent state definition for LangGraph workflow

Defines all the fields that flow between agent nodes :-
- defect_input (from YOLO output and user)
- retrieved_chunks
- regulation_response
- parsed_regulations
- airworthiness_response
- parsed_airworthiness
- human_approved_airworthiness
- repair_response
- parsed_repair
- final_output
- error (if any node fails)

"""

from typing import TypedDict, Optional


class DefectInput(TypedDict):
    # Input from detection layer and user
    defect_type: str
    zone_id: str
    zone_label: str
    severity: str
    confidence: float
    description: Optional[str]
    inspection_type: Optional[str]


class AgentState(TypedDict):
    # Full state object passed between all agent nodes

    # Input (cannot be Optional)
    defect_input: DefectInput

    # Set by node_retrieve
    retrieved_chunks: Optional[list[dict]]
    chunks_text: Optional[str]

    # Set by node_match_regulations
    regulation_response: Optional[str]
    parsed_regulations: Optional[list[dict]]

    # Set by human approval checkpoint 1
    human_approved_airworthiness: Optional[bool]
    human_modified_status: Optional[str]

    # Set by node_assess_airworthiness
    airworthiness_response: Optional[str]
    parsed_airworthiness: Optional[dict]

    # Set by node_generate_repair_plan
    repair_response: Optional[str]
    parsed_repair: Optional[dict]

    # Set by node_compile_output
    final_output: Optional[dict]

    # Set if any step fails
    error: Optional[str]