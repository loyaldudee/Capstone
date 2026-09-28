"""
Agent 5: Investigation Support Agent
------------------------------------
Role: Consolidates findings, manages dynamic A2A handoffs for complex/suspicious claims,
constructs evidentiary audit trails, and formats human-in-the-loop review checklists.
"""

import os
import sys
from datetime import datetime
from typing import Dict, Any, List

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

from task3_multi_agent_system.state import ClaimsInvestigationState


def investigation_support_agent_node(state: ClaimsInvestigationState) -> Dict[str, Any]:
    """LangGraph Node for the Investigation Support Agent (Handoff Target)."""
    claim_id = state.get("claim_id", "UNKNOWN")
    claim_data = state.get("claim_data", {})
    risk_info = state.get("risk_analysis", {})
    anomaly_info = state.get("anomaly_findings", {})
    outliers = state.get("statistical_outliers", [])
    coverage_status = state.get("policy_coverage_status", "")

    # Compile Evidence Checklist
    checklist: List[str] = []

    # 1. Coverage & Narrative Check
    if "INVALID" in coverage_status:
        checklist.append("[CRITICAL] Policy Coverage Failure: Verify active policy registry before any disbursement.")
    elif "SUSPENDED" in coverage_status:
        checklist.append("[CRITICAL] Narrative Insufficiency: Loss description lacks essential details to substantiate claim. Disbursement suspended.")

    # 2. Amount Outliers
    for out in outliers:
        checklist.append(f"[HIGH RISK] {out.get('type')}: {out.get('metric')} ({out.get('significance')}).")

    # 3. Documentation
    if claim_data.get("police_report_filed") == "No" and claim_data.get("incident_severity") in ["Severe", "Catastrophic"]:
        checklist.append("[DOCUMENTATION] Official police/emergency incident report is absent for major loss.")

    # 4. Latency
    if int(claim_data.get("reporting_delay_days", 0)) > 30:
        checklist.append(f"[NOTIFICATION] Delayed notice ({claim_data.get('reporting_delay_days')} days). Issue claimant explanation questionnaire.")

    # Formulate Final Action
    if not checklist:
        action = "CLEAR FOR APPROVAL: Standard settlement pathway approved by multi-agent review."
        recommendation_tier = "Routine Settlement"
    elif any("CRITICAL" in c for c in checklist) or len(checklist) >= 2:
        action = "ESCALATE TO SPECIAL INVESTIGATION UNIT (SIU): Forensic fraud/coverage review required."
        recommendation_tier = "SIU Escalation"
    else:
        action = "REQUEST DOCUMENTATION: Suspend claim pending receipt of verified repair invoices and witness statements."
        recommendation_tier = "Documentation Review"

    dossier = {
        "claim_id": claim_id,
        "investigation_status": "FLAGGED_FOR_HUMAN_REVIEW",
        "recommendation_tier": recommendation_tier,
        "final_action": action,
        "total_flags_count": len(checklist),
        "evidence_checklist": checklist,
        "human_decision_gate": {
            "options": ["Approve Claim", "Request Additional Invoices", "Refer to SIU Special Investigation"],
            "pending_user_decision": True
        }
    }

    audit_entry = {
        "timestamp": datetime.now().isoformat(),
        "agent": "Investigation Support Agent",
        "action": "A2A Handoff Received & Dossier Compiled",
        "details": f"Constructed SIU evidence checklist with {len(checklist)} investigative items. Action: {action}"
    }

    return {
        "investigation_dossier": dossier,
        "siu_evidence_checklist": checklist,
        "final_recommended_action": action,
        "audit_log": [audit_entry],
        "current_stage": "INVESTIGATION_SUPPORT_COMPLETE"
    }
