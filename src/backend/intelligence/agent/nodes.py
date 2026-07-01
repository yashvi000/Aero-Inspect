"""
Agent node functions for LangGraph workflow

1. node_retrieve : searches relevant documents
2. node_match_regulations : identifies applicable regulations
3. node_assess_airworthiness : determines fly/ground status
4. node_generate_repair_plan : creates maintenance action plan
5. node_compile_output : structures final result

"""

from src.shared.utils.logging import get_logger
from src.backend.core.settings import get_yaml_config

from src.backend.intelligence.retrieval.search import search_chunks
from src.backend.intelligence.llm.client import invoke
from src.backend.intelligence.agent.state import AgentState

from src.backend.intelligence.llm.prompts import (
    format_regulation_prompt,
    format_airworthiness_prompt,
    format_repair_prompt,
)

from src.backend.intelligence.llm.parsers import (
    parse_regulations,
    parse_airworthiness,
    parse_repair_plan,
)

logger = get_logger("agent")


def _get_chunk_preview_length() -> int:
    config = get_yaml_config()
    return config["retrieval"].get("chunk_preview_length", 500)


def _format_chunks_text(chunks: list[dict]) -> str:
    
    # Formatting retrieved chunks into a single string for prompt
    
    preview_length = _get_chunk_preview_length()
    chunks_text = ""

    for i, chunk in enumerate(chunks, 1):
        source = chunk["metadata"].get("source", "unknown")
        doc_id = chunk["metadata"].get("document_id", "unknown")
        preview = chunk["text"][:preview_length]

        chunks_text += f"[Document {i} - {source} - {doc_id}]\n"
        chunks_text += preview
        chunks_text += "\n\n"

    return chunks_text


def _format_regulations_text(regulations: list[dict]) -> str:
    # Formats parsed regulations into readable string for next prompt
    
    if not regulations:
        return "No applicable regulations found in available documents."

    lines = []
    for reg in regulations:
        lines.append(f"Regulation ID : {reg.get('id', 'unknown')}")
        lines.append(f"Source : {reg.get('source', 'unknown')}")
        lines.append(f"Requirement : {reg.get('requirement', 'see document')}")
        lines.append(f"Compliance Timeline : {reg.get('compliance_timeline', 'not specified')}")
        lines.append("")

    return "\n".join(lines)


# Node 1: Retrieve 
def node_retrieve(state: AgentState) -> dict:
    # Searches the vector store for relevant regulatory chunks

    defect_input = state["defect_input"]

    logger.info(
        f"Node Retrieve | "
        f"defect : {defect_input['defect_type']} | "
        f"zone : {defect_input['zone_id']}"
    )

    try:
        chunks = search_chunks(
            defect_type=defect_input["defect_type"],
            zone_id=defect_input.get("zone_id"),
            zone_label=defect_input.get("zone_label"),
            description=defect_input.get("description"),
        )

        chunks_text = _format_chunks_text(chunks)
        logger.info(f"Node Retrieve completed | chunks : {len(chunks)}")

        return {
            "retrieved_chunks": chunks,
            "chunks_text": chunks_text,
        }

    except Exception as e:
        logger.error(f"Node Retrieve failed: {e}")
        return {
            "retrieved_chunks": [],
            "chunks_text": "",
            "error": f"Retrieval failed: {str(e)}",
        }


# Node 2: Match Regulations 
def node_match_regulations(state: AgentState) -> dict:
    # Sends retrieved chunks to LLM to identify applicable regulations

    defect_input = state["defect_input"]
    chunks_text = state.get("chunks_text", "")

    logger.info("Node Match Regulations : Sending to LLM")

    if not chunks_text:
        logger.warning("No chunks text available for regulation matching")
        return {
            "regulation_response": "",
            "parsed_regulations": [],
        }

    try:
        prompt = format_regulation_prompt(
            defect_type=defect_input["defect_type"],
            zone_label=defect_input.get("zone_label", "unknown"),
            severity=defect_input["severity"],
            description=defect_input.get("description", ""),
            retrieved_chunks=chunks_text,
        )

        response = invoke(prompt)
        regulations = parse_regulations(response)

        logger.info(
            f"Node Match Regulations complete | "
            f"regulations_found : {len(regulations)}"
        )

        return {
            "regulation_response": response,
            "parsed_regulations": regulations,
        }

    except Exception as e:
        logger.error(f"Node Match Regulations failed: {e}")
        return {
            "regulation_response": "",
            "parsed_regulations": [],
            "error": f"Regulation matching failed: {str(e)}",
        }


# Node 3: Assess Airworthiness
def node_assess_airworthiness(state: AgentState) -> dict:
    # Determines airworthiness status based on defect and regulations

    defect_input = state["defect_input"]
    parsed_regulations = state.get("parsed_regulations", [])

    logger.info("Node Assess Airworthiness : sending to LLM")
    regulations_text = _format_regulations_text(parsed_regulations)

    try:
        prompt = format_airworthiness_prompt(
            defect_type=defect_input["defect_type"],
            zone_label=defect_input.get("zone_label", "unknown"),
            severity=defect_input["severity"],
            matched_regulations=regulations_text,
        )

        response = invoke(prompt)
        airworthiness = parse_airworthiness(response)

        # Human modified status at checkpoint overrides
        if state.get("human_modified_status"):
            logger.info(
                f"Human overrode Airworthiness Status | "
                f"{airworthiness['status']} changed to "
                f"{state['human_modified_status']}"
            )
            airworthiness["status"] = state["human_modified_status"]
            airworthiness["reasoning"] += " [Status modified by inspector]"

        logger.info(
            f"Node Assess Airworthiness complete | "
            f"status : {airworthiness['status']}"
        )

        return {
            "airworthiness_response": response,
            "parsed_airworthiness": airworthiness,
        }

    except Exception as e:
        logger.error(f"Node Assess Airworthiness failed: {e}")
        return {
            "airworthiness_response": "",
            "parsed_airworthiness": {
                "status": "GROUND_AIRCRAFT",
                "reasoning": f"Assessment failed - Defaulting to ground: {str(e)}",
                "conditions": "none",
                "regulation_reference": "none",
            },
            "error": f"Airworthiness assessment failed: {str(e)}",
        }


# Node 4: Generate Repair Plan
def node_generate_repair_plan(state: AgentState) -> dict:
    # Generates complete maintenance action plan

    defect_input = state["defect_input"]
    parsed_regulations = state.get("parsed_regulations", [])
    parsed_airworthiness = state.get("parsed_airworthiness", {})

    logger.info("Node Generate Repair Plan : sending to LLM")

    regulations_text = _format_regulations_text(parsed_regulations)
    airworthiness_status = parsed_airworthiness.get("status", "GROUND_AIRCRAFT")

    try:
        prompt = format_repair_prompt(
            defect_type=defect_input["defect_type"],
            zone_label=defect_input.get("zone_label", "unknown"),
            severity=defect_input["severity"],
            airworthiness_status=airworthiness_status,
            matched_regulations=regulations_text,
            similar_cases="",
        )

        response = invoke(prompt)
        repair = parse_repair_plan(response)

        logger.info(
            f"Node Generate Repair Plan complete | "
            f"steps : {len(repair.get('repair_steps', []))}"
        )

        return {
            "repair_response": response,
            "parsed_repair": repair,
        }

    except Exception as e:
        logger.error(f"Node Generate Repair Plan failed: {e}")
        return {
            "repair_response": "",
            "parsed_repair": {
                "repair_steps": ["Contact manufacturer for repair guidance"],
                "parts_required": ["To be determined"],
                "tools_required": ["Standard toolkit"],
                "ame_certification": "B1.1 - Aeroplane Turbine",
                "estimated_hours": 0,
                "compliance_deadline": "not specified",
            },
            "error": f"Repair plan generation failed: {str(e)}",
        }


# Node 5: Compile Output 
def node_compile_output(state: AgentState) -> dict:
    # Compiles all node outputs into final structured result

    logger.info("Node Compile Output | Structuring final result")

    defect_input = state["defect_input"]
    parsed_regulations = state.get("parsed_regulations", [])
    parsed_airworthiness = state.get("parsed_airworthiness", {})
    parsed_repair = state.get("parsed_repair", {})

    human_override = state.get("human_modified_status")
    ai_status = parsed_airworthiness.get("status", "GROUND_AIRCRAFT")
    ai_reasoning = parsed_airworthiness.get("reasoning", "")
    ai_conditions = parsed_airworthiness.get("conditions", "none")

    if human_override:
        final_status = human_override
        final_reasoning = (
            f"AI recommended: {ai_status} | "
            f"Inspector overrode to: {human_override} | "
            f"Original AI reasoning: {ai_reasoning}"
        )
        final_conditions = "none" if human_override == "AIRWORTHY" else ai_conditions
    else:
        final_status = ai_status
        final_reasoning = ai_reasoning
        final_conditions = ai_conditions

    final_output = {
        "defect_type": defect_input["defect_type"],
        "zone_id": defect_input.get("zone_id"),
        "zone_label": defect_input.get("zone_label"),
        "severity": defect_input["severity"],
        "confidence": defect_input.get("confidence"),
        
        "matched_regulations": parsed_regulations,
        "airworthiness_status": final_status,
        "airworthiness_reasoning": final_reasoning,
        "airworthiness_conditions": final_conditions,
        "regulation_reference": parsed_airworthiness.get("regulation_reference", "none"),
        
        "repair_steps": parsed_repair.get("repair_steps", []),
        "parts_required": parsed_repair.get("parts_required", []),
        "tools_required": parsed_repair.get("tools_required", []),
        "ame_certification": parsed_repair.get("ame_certification", "B1.1 - Aeroplane Turbine"),
        "estimated_hours": parsed_repair.get("estimated_hours", 0),
        "compliance_deadline": parsed_repair.get("compliance_deadline", "not specified"),
        
        "human_override_applied": human_override is not None,
        "error": state.get("error"),
    }

    logger.info(
        f"Node Compile Output completed | "
        f"airworthiness : {final_output['airworthiness_status']} | "
        f"regulations : {len(final_output['matched_regulations'])} | "
        f"steps : {len(final_output['repair_steps'])}"
    )
    return {"final_output": final_output}