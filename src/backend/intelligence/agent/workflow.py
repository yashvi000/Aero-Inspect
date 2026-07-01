"""
LangGraph agent workflow for aerospace defect investigation.

Workflow sequence:
    1. retrieve -> 2. match_regulations -> 3. assess_airworthiness -> 4. [CHECKPOINT 1 : human reviews airworthiness] 
    -> 5. generate_repair_plan -> 6. [CHECKPOINT 2 : human reviews all findings] -> 7. compile_output
"""

from langgraph.graph import StateGraph, END
from langgraph.checkpoint.memory import MemorySaver
from langgraph.types import Command

from src.shared.utils.logging import get_logger
from src.backend.intelligence.agent.state import AgentState, DefectInput
from src.backend.intelligence.agent.approval import checkpoint_airworthiness, checkpoint_final_review

from src.backend.intelligence.agent.nodes import (
    node_retrieve,
    node_match_regulations,
    node_assess_airworthiness,
    node_generate_repair_plan,
    node_compile_output
)


logger = get_logger("agent")


def _build_graph() -> StateGraph:
    # Building and compiling LangGraph state machine.
    
    graph = StateGraph(AgentState)

    # Adding all nodes
    graph.add_node("retrieve", node_retrieve)
    graph.add_node("match_regulations", node_match_regulations)
    graph.add_node("assess_airworthiness", node_assess_airworthiness)
    graph.add_node("checkpoint_airworthiness", checkpoint_airworthiness)
    graph.add_node("generate_repair_plan", node_generate_repair_plan)
    graph.add_node("checkpoint_final_review", checkpoint_final_review)
    graph.add_node("compile_output", node_compile_output)

    # Defining edges (execution order)
    graph.set_entry_point("retrieve")
    graph.add_edge("retrieve", "match_regulations")
    graph.add_edge("match_regulations", "assess_airworthiness")
    graph.add_edge("assess_airworthiness", "checkpoint_airworthiness")
    graph.add_edge("checkpoint_airworthiness", "generate_repair_plan")
    graph.add_edge("generate_repair_plan", "checkpoint_final_review")
    graph.add_edge("checkpoint_final_review", "compile_output")
    graph.add_edge("compile_output", END)

    # in-memory checkpointer between interrupts
    checkpointer = MemorySaver()
    compiled = graph.compile(
        checkpointer=checkpointer,
        interrupt_before=[
            "checkpoint_airworthiness",
            "checkpoint_final_review",
        ]
    )
    return compiled


# Building graph once at module load
_graph = _build_graph()


def run_investigation(
    defect_input: DefectInput,
    thread_id: str,
) -> dict:
    """
    Starts a new investigation workflow and runs till first human checkpoint
    
    Returns current state for frontend display
    """

    logger.info(f"Starting investigation ...")
    logger.info(
        f"defect : {defect_input['defect_type']} | "
        f"zone : {defect_input.get('zone_id')} | "
        f"thread : {thread_id}"
    )

    config = {"configurable": {"thread_id": thread_id}}

    initial_state: AgentState = {
        "defect_input": defect_input,
        "retrieved_chunks": None,
        "chunks_text": None,
        "regulation_response": None,
        "parsed_regulations": None,
        "human_approved_airworthiness": None,
        "human_modified_status": None,
        "airworthiness_response": None,
        "parsed_airworthiness": None,
        "repair_response": None,
        "parsed_repair": None,
        "final_output": None,
        "error": None,
    }

    # Runs until first checkpoint
    state = _graph.invoke(initial_state, config=config)

    logger.info(
        f"Investigation paused at checkpoint | thread : {thread_id}"
    )
    return state


def resume_after_airworthiness(
    thread_id: str,
    approved: bool,
    modified_status: str = None,
) -> dict:
    """
    Resumes workflow after inspector reviews airworthiness

    Args:
        thread_id: Same thread ID used in run_investigation
        approved: True if inspector approves AI decision
        modified_status: Optional override status from inspector

    Returns:
        Updated agent state after running to next checkpoint
    """

    logger.info(f"Resuming after airworthiness ... ")
    logger.info(
        f"thread : {thread_id} | "
        f"approved : {approved} | "
        f"modified_status : {modified_status}"
    )

    config = {"configurable": {"thread_id": thread_id}}

    human_response = {
        "approved": approved,
        "modified_status": modified_status,
    }

    state = _graph.invoke(
        Command(resume= human_response),
        config=config,
    )
    return state


def resume_after_final_review(
    thread_id: str,
    approved: bool,
) -> dict:
    """
    Resumes workflow after inspector reviews all findings

    Args:
        thread_id: Same thread ID used in run_investigation
        approved: True if inspector approves and wants reports

    Returns:
        Final compiled agent state with full output
    """

    logger.info(f"Resuming after final review ... ")
    logger.info(
        f"thread : {thread_id} | "
        f"approved : {approved}"
    )

    config = {"configurable": {"thread_id": thread_id}}
    human_response = {"approved": approved}

    state = _graph.invoke(
        Command(resume= human_response),
        config=config,
    )

    final_output = state.get("final_output", {})

    logger.info(f"Investigation complete")
    logger.info(
        f"thread : {thread_id} | "
        f"airworthiness : {final_output.get('airworthiness_status')}"
    )
    return state


def get_current_state(thread_id: str) -> dict:
    # Gets current state of investigation thread (for polling or reconnecting)

    config = {"configurable": {"thread_id": thread_id}}

    try:
        state = _graph.get_state(config)
        return state.values if state else {}
    
    except Exception as e:
        logger.error(f"Failed to get state for thread {thread_id}: {e}")
        return {}