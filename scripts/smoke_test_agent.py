"""
Test full agent workflow with different defect scenarios.
Run: python scripts/smoke_test_agent.py
"""

import sys
sys.path.append(".")

from src.backend.intelligence.agent.workflow import (
    run_investigation,
    resume_after_airworthiness,
    resume_after_final_review,
)


def run_test(
    test_name: str,
    thread_id: str,
    defect_input: dict,
    approve_airworthiness: bool = True,
    override_status: str = None,
):
    """Run one full agent test case."""

    print()
    print("=" * 60)
    print(f"TEST: {test_name}")
    print("=" * 60)

    # Step 1
    print("\n--- Step 1: Investigation ---")
    state = run_investigation(
        defect_input=defect_input,
        thread_id=thread_id,
    )

    regs = state.get("parsed_regulations") or []
    airw = state.get("parsed_airworthiness") or {}
    print(f"Regulations: {len(regs)}")
    print(f"AI Airworthiness: {airw.get('status')}")
    print(f"AI Reasoning: {airw.get('reasoning', '')[:150]}")

    # Step 2
    print("\n--- Step 2: Airworthiness Approval ---")
    print(f"Approved: {approve_airworthiness} | Override: {override_status}")

    state = resume_after_airworthiness(
        thread_id=thread_id,
        approved=approve_airworthiness,
        modified_status=override_status,
    )

    repair = (state.get("parsed_repair") or {})
    print(f"Repair steps: {len(repair.get('repair_steps', []))}")
    print(f"Parts: {len(repair.get('parts_required', []))}")
    print(f"Tools: {len(repair.get('tools_required', []))}")
    print(f"AME cert: {repair.get('ame_certification')}")
    print(f"Hours: {repair.get('estimated_hours')}")

    # Step 3
    print("\n--- Step 3: Final Approval ---")
    state = resume_after_final_review(
        thread_id=thread_id,
        approved=True,
    )

    final = state.get("final_output") or {}
    print(f"\nFINAL RESULT:")
    print(f"  Defect: {final.get('defect_type')}")
    print(f"  Zone: {final.get('zone_label')}")
    print(f"  Severity: {final.get('severity')}")
    print(f"  Airworthiness: {final.get('airworthiness_status')}")
    print(f"  Override applied: {final.get('human_override_applied')}")
    print(f"  Regulations: {len(final.get('matched_regulations', []))}")
    print(f"  Repair steps: {len(final.get('repair_steps', []))}")
    print(f"  AME cert: {final.get('ame_certification')}")
    print(f"  Hours: {final.get('estimated_hours')}")
    print(f"  Error: {final.get('error')}")

    # Validation
    print(f"\n  VALIDATION:")
    errors = []

    if not final.get("airworthiness_status"):
        errors.append("Missing airworthiness_status")

    if final.get("airworthiness_status") not in [
        "AIRWORTHY", "AIRWORTHY_WITH_CONDITIONS", "GROUND_AIRCRAFT"
    ]:
        errors.append(f"Invalid status: {final.get('airworthiness_status')}")

    if not final.get("repair_steps"):
        errors.append("No repair steps generated")

    if not final.get("matched_regulations"):
        errors.append("No regulations found")

    if final.get("error"):
        errors.append(f"Error present: {final.get('error')}")

    if override_status and final.get("airworthiness_status") != override_status:
        errors.append(
            f"Override not applied: expected {override_status}, "
            f"got {final.get('airworthiness_status')}"
        )

    if errors:
        for e in errors:
            print(f"  ❌ {e}")
    else:
        print(f"  ✅ All validations passed")

    return final


def main():
    # ─── TEST 1: HIGH severity crack ────────────────
    run_test(
        test_name="HIGH severity crack - approve AI decision",
        thread_id="test-crack-high-001",
        defect_input={
            "defect_type": "crack",
            "zone_id": "zone_03",
            "zone_label": "Left Forward Fuselage",
            "severity": "HIGH",
            "confidence": 0.91,
            "description": "25mm fatigue crack along rivet line",
            "inspection_type": "DVI",
        },
        approve_airworthiness=True,
        override_status=None,
    )
    """
    # ─── TEST 2: MEDIUM severity corrosion ──────────
    run_test(
        test_name="MEDIUM severity corrosion - approve AI decision",
        thread_id="test-corrosion-med-001",
        defect_input={
            "defect_type": "corrosion",
            "zone_id": "zone_11",
            "zone_label": "Left Aft Fuselage",
            "severity": "MEDIUM",
            "confidence": 0.85,
            "description": "surface corrosion patch near lap joint, approximately 30mm diameter",
            "inspection_type": "DVI",
        },
        approve_airworthiness=True,
        override_status=None,
    )
    """
    # ─── TEST 3: LOW severity scratch ───────────────
    run_test(
        test_name="LOW severity scratch - approve AI decision",
        thread_id="test-scratch-low-001",
        defect_input={
            "defect_type": "scratch",
            "zone_id": "zone_04",
            "zone_label": "Right Forward Fuselage",
            "severity": "LOW",
            "confidence": 0.78,
            "description": "surface scratch from ground equipment contact",
            "inspection_type": "GVI",
        },
        approve_airworthiness=True,
        override_status=None,
    )
    """
    # ─── TEST 4: MEDIUM severity dent ───────────────
    run_test(
        test_name="MEDIUM severity dent - approve AI decision",
        thread_id="test-dent-med-001",
        defect_input={
            "defect_type": "dent",
            "zone_id": "zone_12",
            "zone_label": "Right Aft Fuselage",
            "severity": "MEDIUM",
            "confidence": 0.82,
            "description": "impact dent 50mm diameter depth approximately 3mm",
            "inspection_type": "DVI",
        },
        approve_airworthiness=True,
        override_status=None,
    )
    """
    # ─── TEST 5: MEDIUM severity paint damage ──────────
    run_test(
        test_name="MEDIUM severity paint damage - approve AI decision",
        thread_id="test-paint-medium-001",
        defect_input={
            "defect_type": "paint_damage",
            "zone_id": "zone_01",
            "zone_label": "Nose Section",
            "severity": "MEDIUM",
            "confidence": 0.73,
            "description": "paint chipping near antenna mount, bare metal exposed",
            "inspection_type": "GVI",
        },
        approve_airworthiness=True,
        override_status=None,
    )

    # ─── TEST 6: HIGH crack - inspector overrides ───
    run_test(
        test_name="HIGH severity crack - inspector overrides to AIRWORTHY_WITH_CONDITIONS",
        thread_id="test-crack-override-001",
        defect_input={
            "defect_type": "crack",
            "zone_id": "zone_03",
            "zone_label": "Left Forward Fuselage",
            "severity": "HIGH",
            "confidence": 0.91,
            "description": "25mm fatigue crack along rivet line",
            "inspection_type": "DVI",
        },
        approve_airworthiness=False,
        override_status="AIRWORTHY_WITH_CONDITIONS",
    )
    """
    # ─── TEST 7: MEDIUM corrosion - override to GROUND ──
    run_test(
        test_name="MEDIUM corrosion - inspector overrides to GROUND_AIRCRAFT",
        thread_id="test-corrosion-override-001",
        defect_input={
            "defect_type": "corrosion",
            "zone_id": "zone_11",
            "zone_label": "Left Aft Fuselage",
            "severity": "MEDIUM",
            "confidence": 0.85,
            "description": "extensive corrosion with pitting near aft pressure bulkhead",
            "inspection_type": "DVI",
        },
        approve_airworthiness=False,
        override_status="GROUND_AIRCRAFT",
    )

    # ─── TEST 8: LOW scratch - override to AIRWORTHY ──
    run_test(
        test_name="LOW scratch - inspector overrides to AIRWORTHY",
        thread_id="test-scratch-override-001",
        defect_input={
            "defect_type": "scratch",
            "zone_id": "zone_04",
            "zone_label": "Right Forward Fuselage",
            "severity": "LOW",
            "confidence": 0.78,
            "description": "minor cosmetic scratch from tool contact",
            "inspection_type": "GVI",
        },
        approve_airworthiness=False,
        override_status="AIRWORTHY",
    )
    """
    # ─── Summary ────────────────────────────────────
    print()
    print("=" * 60)
    print("ALL TESTS COMPLETE")
    print("=" * 60)


if __name__ == "__main__":
    main()