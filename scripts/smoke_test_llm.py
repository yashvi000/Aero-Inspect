"""
Test the full LLM pipeline:
retrieval → regulation matching → airworthiness → repair plan
"""

import sys
sys.path.append(".")

from src.backend.intelligence.llm.client import invoke
from src.backend.intelligence.llm.prompts import (
    format_regulation_prompt,
    format_airworthiness_prompt,
    format_repair_prompt,
)
from src.backend.intelligence.retrieval.search import search_chunks


def main():
    print("=== STEP 1: RETRIEVAL ===")
    results = search_chunks("crack", zone_id="zone_03")
    print(f"Retrieved {len(results)} chunks")

    chunks_text = ""
    for i, r in enumerate(results, 1):
        source = r["metadata"]["source"]
        doc_id = r["metadata"]["document_id"]
        chunk_preview = r["text"][:500]
        chunks_text += f"[Document {i} - {source} - {doc_id}]\n"
        chunks_text += chunk_preview
        chunks_text += "\n\n"

    print()
    print("=== STEP 2: REGULATION MATCHING ===")
    reg_prompt = format_regulation_prompt(
        defect_type="crack",
        zone_label="Left Forward Fuselage",
        severity="HIGH",
        description="25mm fatigue crack along rivet line near lap joint",
        retrieved_chunks=chunks_text,
    )
    print(f"Prompt length: {len(reg_prompt)}")
    reg_response = invoke(reg_prompt)
    print("LLM Response:")
    print(reg_response)

    print()
    print("=== STEP 3: AIRWORTHINESS ASSESSMENT ===")
    airworthy_prompt = format_airworthiness_prompt(
        defect_type="crack",
        zone_label="Left Forward Fuselage",
        severity="HIGH",
        matched_regulations=reg_response,
    )
    airworthy_response = invoke(airworthy_prompt)
    print("LLM Response:")
    print(airworthy_response)

    print()
    print("=== STEP 4: REPAIR PLAN ===")
    repair_prompt = format_repair_prompt(
        defect_type="crack",
        zone_label="Left Forward Fuselage",
        severity="HIGH",
        airworthiness_status="GROUND_AIRCRAFT",
        matched_regulations=reg_response,
        similar_cases="No similar cases available",
    )
    repair_response = invoke(repair_prompt)
    print("LLM Response:")
    print(repair_response)


if __name__ == "__main__":
    main()