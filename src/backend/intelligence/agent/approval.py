"""
Human-in-the-loop approval logic for agent workflow

Checkpoints:
1. After airworthiness assessment:
    Inspector reviews, and approves or override the status

2. After repair plan generation:
    Inspector reviews the complete output, approve or flags for modification

"""

from langgraph.types import interrupt

from src.shared.utils.logging import get_logger
from src.backend.core.settings import get_yaml_config
from src.backend.intelligence.agent.state import AgentState

logger = get_logger("agent")


def _get_airworthiness_statuses() -> str:
    config = get_yaml_config()
    return config["llm"]["valid_airworthiness_statuses"]


def checkpoint_airworthiness(state: AgentState) -> dict:
    """
    Checkpoint 1 : After airworthiness assessment

    The human can :
    - Approve the AI decision
    - Override with a different status
    """

    parsed_airworthiness = state.get("parsed_airworthiness", {})
    current_status = parsed_airworthiness.get("status", "GROUND_AIRCRAFT")

    logger.info(
        f"Checkpoint 1: Airworthiness review | "
        f"AI status : {current_status}"
    )

    # Paused and waiting for human input
    # Resumes after human approves (from API)
    human_input = interrupt({
        "checkpoint": "airworthiness_review",
        "message": "Please review the airworthiness assessment",
        "ai_status": current_status,
        "reasoning": parsed_airworthiness.get("reasoning", ""),
        "conditions": parsed_airworthiness.get("conditions", "none"),
        "regulation_reference": parsed_airworthiness.get("regulation_reference", "none"),
        "valid_statuses": list(_get_airworthiness_statuses()),
    })

    # Processing human response
    approved = human_input.get("approved", False)
    modified_status = human_input.get("modified_status")

    if approved:
        logger.info("Checkpoint 1: Inspector approved airworthiness")
        return {
            "human_approved_airworthiness": True,
            "human_modified_status": None,
        }

    if modified_status and modified_status in _get_airworthiness_statuses():
        logger.info(f"Checkpoint 1: Inspector modified status to {modified_status}")

        return {
            "human_approved_airworthiness": True,
            "human_modified_status": modified_status,
        }

    # Approved (default) if human response is invalid
    logger.warning("Checkpoint 1: Invalid human response | Defaulting to approved")

    return {
        "human_approved_airworthiness": True,
        "human_modified_status": None,
    }


def checkpoint_final_review(state: AgentState) -> dict:
    """
    Checkpoint 2 : After repair plan generation

    The human can :
    - Approve and trigger PDF generation
    - Flag for modification (workflow ends without PDF)
    """

    parsed_airworthiness = state.get("parsed_airworthiness", {})
    parsed_repair = state.get("parsed_repair", {})
    parsed_regulations = state.get("parsed_regulations", [])

    logger.info("Checkpoint 2: Final review before report generation")

    human_input = interrupt({
        "checkpoint": "final_review",
        "message": "Please review all the findings before generating reports",
        "airworthiness_status": parsed_airworthiness.get("status"),
        "airworthiness_reasoning": parsed_airworthiness.get("reasoning"),
        "regulations_count": len(parsed_regulations),
        "repair_steps_count": len(parsed_repair.get("repair_steps", [])),
        "ame_certification": parsed_repair.get("ame_certification"),
        "estimated_hours": parsed_repair.get("estimated_hours"),
    })

    approved = human_input.get("approved", False)

    if approved:
        logger.info("Checkpoint 2: Inspector approved final findings")
    else:
        logger.warning(
            "Checkpoint 2: Inspector did not approve | "
            "Reports will not be generated"
        )

    return {}