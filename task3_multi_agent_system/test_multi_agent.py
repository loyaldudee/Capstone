"""
Task 3 End-to-End Multi-Agent Verification Script
-------------------------------------------------
Tests the LangGraph multi-agent workflow on:
1. A Routine Claim (should complete without handoff)
2. A Complex Anomaly Claim (should trigger dynamic A2A Handoff to Investigation Support Agent)
3. Displays the full audit log tracing A2A communication.
"""

import os
import sys
import json

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

from task3_multi_agent_system.graph import run_claims_investigation, claims_agent_app


def test_routine_claim_flow():
    print("=" * 75)
    print(" TEST 1: ROUTINE CLAIM (AUTO-CLEAR WORKFLOW)")
    print("=" * 75)

    routine_claim = {
        "claim_id": "CLM-ROUTINE-001",
        "customer_id": "CUST_00401",
        "policy_type": "Auto",
        "policy_count": 2,
        "policy_contribution_tier": 5,
        "purchasing_power_class": 6,
        "claim_amount": 2950.0,
        "incident_type": "Collision",
        "incident_severity": "Moderate",
        "incident_date": "2024-05-12",
        "reporting_delay_days": 2,
        "police_report_filed": "Yes",
        "witness_present": "Yes",
        "prior_claims_count": 0,
        "incident_description": "Front-end collision at intersection during light rain; bumper damage. Other driver present. Insured (40-50 years, Career and childcare)."
    }

    result = run_claims_investigation(routine_claim)

    print("\n[WORKFLOW EXECUTION SUMMARY]")
    print(f"• Claim ID:                  {result['claim_id']}")
    print(f"• Stage Reached:             {result.get('current_stage')}")
    print(f"• Investigation Handoff:     {result.get('requires_investigation_handoff')}")
    print(f"• Coverage Status:           {result.get('policy_coverage_status')}")
    print(f"• Similar Claims Retrieved:  {len(result.get('similar_claims', []))}")
    print(f"\n[EXECUTIVE SUMMARY]:\n{result.get('executive_summary')}")

    print("\n[A2A AUDIT LOG TRACE]:")
    for log in result.get("audit_log", []):
        print(f"  [{log['timestamp'][:19]}] {log['agent']:28s} -> {log['action']}: {log['details']}")


def test_complex_anomaly_claim_flow():
    print("\n" + "=" * 75)
    print(" TEST 2: COMPLEX CLAIM (DYNAMIC A2A HANDOFF TO INVESTIGATION AGENT)")
    print("=" * 75)

    complex_claim = {
        "claim_id": "CLM-ANOMALY-002",
        "customer_id": "CUST_08817",
        "policy_type": "Boat_Marine",
        "policy_count": 0,  # Coverage Mismatch!
        "policy_contribution_tier": 0,
        "purchasing_power_class": 4,
        "claim_amount": 68500.0,  # Extreme Outlier!
        "incident_type": "Marina Collision",
        "incident_severity": "Catastrophic",
        "incident_date": "2024-02-14",
        "reporting_delay_days": 55,  # 55-day delay!
        "police_report_filed": "No",  # Catastrophic with no police report!
        "witness_present": "No",
        "prior_claims_count": 2,
        "incident_description": "Pleasure craft collided with harbor pilings during gale-force wind; total hull rupture. Insured reported severe flooding."
    }

    result = run_claims_investigation(complex_claim)

    print("\n[WORKFLOW EXECUTION SUMMARY]")
    print(f"• Claim ID:                  {result['claim_id']}")
    print(f"• Final Stage Reached:       {result.get('current_stage')}")
    print(f"• Investigation Handoff:     {result.get('requires_investigation_handoff')} (DYNAMIC HANDOFF TRIGGERED)")
    print(f"• Final Recommended Action:  {result.get('final_recommended_action')}")
    
    dossier = result.get("investigation_dossier", {})
    print(f"• Recommendation Tier:       {dossier.get('recommendation_tier')}")
    print(f"• Total Evidence Flags:      {dossier.get('total_flags_count')}")

    print("\n[SIU EVIDENCE CHECKLIST]:")
    for item in result.get("siu_evidence_checklist", []):
        print(f"  [!] {item}")

    print("\n[HUMAN-IN-THE-LOOP DECISION GATE]:")
    print(f"  Options Available to Adjuster: {dossier.get('human_decision_gate', {}).get('options')}")
    print(f"  Status: Pending Human Reviewer Confirmation")

    print("\n[A2A AUDIT LOG TRACE]:")
    for log in result.get("audit_log", []):
        print(f"  [{log['timestamp'][:19]}] {log['agent']:28s} -> {log['action']}: {log['details']}")


if __name__ == "__main__":
    test_routine_claim_flow()
    test_complex_anomaly_claim_flow()
