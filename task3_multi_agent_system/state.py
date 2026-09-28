"""
Claims Investigation State Definition for LangGraph Workflow
------------------------------------------------------------
Defines the shared typed state dictionary passed between all 5 agents.
"""

import operator
from typing import TypedDict, List, Dict, Any, Optional, Annotated
from datetime import datetime


class ClaimsInvestigationState(TypedDict, total=False):
    # Initial Inputs
    claim_id: str
    claim_data: Dict[str, Any]
    customer_id: str
    customer_profile: Dict[str, Any]

    # Agent 1: Claims Retrieval Agent Outputs
    similar_claims: List[Dict[str, Any]]
    retrieval_insights: str

    # Agent 2: Claims Risk Analysis Agent Outputs
    risk_analysis: Dict[str, Any]
    policy_coverage_status: str

    # Agent 3: Anomaly Detection Agent Outputs
    anomaly_findings: Dict[str, Any]
    statistical_outliers: List[Dict[str, Any]]

    # Agent 4: Claims Summarization Agent Outputs
    executive_summary: str

    # Agent 5: Investigation Support Agent Outputs (Handoff)
    investigation_dossier: Dict[str, Any]
    siu_evidence_checklist: List[str]
    final_recommended_action: str

    # Agent 6: Senior Claims Adjudication Advisor Agent
    advisor_guidance: Dict[str, Any]

    # Flow Control & Handoff Flags
    requires_investigation_handoff: bool
    current_stage: str
    audit_log: Annotated[List[Dict[str, Any]], operator.add]


def create_initial_state(claim_data: Dict[str, Any], customer_profile: Optional[Dict[str, Any]] = None) -> ClaimsInvestigationState:
    """Helper to initialize a clean state for the LangGraph workflow."""
    cid = claim_data.get("claim_id", "UNKNOWN")
    cust_id = claim_data.get("customer_id", "UNKNOWN")
    return {
        "claim_id": cid,
        "claim_data": claim_data,
        "customer_id": cust_id,
        "customer_profile": customer_profile or {},
        "similar_claims": [],
        "retrieval_insights": "",
        "risk_analysis": {},
        "policy_coverage_status": "Pending Verification",
        "anomaly_findings": {},
        "statistical_outliers": [],
        "executive_summary": "",
        "investigation_dossier": {},
        "siu_evidence_checklist": [],
        "advisor_guidance": {},
        "final_recommended_action": "Pending Review",
        "requires_investigation_handoff": False,
        "current_stage": "INITIALIZED",
        "audit_log": [
            {
                "timestamp": datetime.now().isoformat(),
                "agent": "System Orchestrator",
                "action": "Workflow Initialized",
                "details": f"Investigation started for Claim {cid} (Customer {cust_id})"
            }
        ]
    }
