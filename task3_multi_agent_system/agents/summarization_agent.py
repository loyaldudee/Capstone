"""
Agent 4: Claims Summarization Agent
-----------------------------------
Role: Synthesizes findings from Retrieval, Risk Analysis, and Anomaly Detection agents
into a structured, concise case brief for insurance reviewers.
Uses: LLM Client (gpt-4o-mini) with deterministic structured fallback.
"""

import os
import sys
from datetime import datetime
from typing import Dict, Any

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

from task3_multi_agent_system.llm_client import generate_llm_response, check_llm_status
from task3_multi_agent_system.state import ClaimsInvestigationState


def claims_summarization_agent_node(state: ClaimsInvestigationState) -> Dict[str, Any]:
    """LangGraph Node for the Claims Summarization Agent."""
    claim_id = state.get("claim_id", "UNKNOWN")
    claim_data = state.get("claim_data", {})
    risk_info = state.get("risk_analysis", {})
    anomaly_info = state.get("anomaly_findings", {})
    similar_claims = state.get("similar_claims", [])
    coverage_status = state.get("policy_coverage_status", "")

    # Build prompt for LLM
    prompt = f"""
Analyze the following insurance claim investigation file and provide a structured case summary for a Senior Claims Reviewer:

[CLAIM OVERVIEW]
Claim ID: {claim_id}
Customer ID: {state.get('customer_id')}
Policy Line: {claim_data.get('policy_type')} (Active policies on record: {claim_data.get('policy_count')})
Claim Amount: €{float(claim_data.get('claim_amount', 0)):,.2f}
Incident Type: {claim_data.get('incident_type')} ({claim_data.get('incident_severity')} severity)
Incident Date: {claim_data.get('incident_date')} | Reporting Delay: {claim_data.get('reporting_delay_days')} days
Police Report: {claim_data.get('police_report_filed')} | Witnesses: {claim_data.get('witness_present')}
Incident Narrative: {claim_data.get('incident_description')}

[RISK & ANOMALY FINDINGS]
Coverage Status: {coverage_status}
Supervised Risk Probability: {risk_info.get('supervised_risk_probability', 0):.1%}
Isolation Forest Anomaly Score: {anomaly_info.get('isolation_forest_anomaly_score', 0):.3f}
Preliminary Risk Tier: {risk_info.get('preliminary_risk_tier')}
Statistical Outliers Detected: {anomaly_info.get('outlier_count', 0)}

[SIMILAR HISTORICAL CLAIMS]
{similar_claims[:2]}

Please provide:
1. Executive Incident Synopsis
2. Policyholder Coverage & Demographic Assessment
3. Identified Discrepancies & Anomaly Indicators
4. Preliminary Recommendation for Human Adjuster
"""

    llm_available, llm_reason = check_llm_status()

    llm_summary = generate_llm_response(prompt)

    # Fallback structured brief if LLM response not returned
    if not llm_summary:
        # Determine conclusive recommendation from other agents' findings
        risk_prob = risk_info.get('supervised_risk_probability', 0)
        risk_tier = risk_info.get('preliminary_risk_tier', 'Low')
        is_anomaly = anomaly_info.get('is_anomaly', False)
        checklist = state.get('siu_evidence_checklist', [])

        if 'INVALID' in coverage_status or 'SUSPENDED' in coverage_status:
            conclusion = 'Documentation Review — coverage status requires verification before any disbursement.'
        elif risk_tier in ['High', 'Critical'] or risk_prob > 0.6 or any('CRITICAL' in c for c in checklist):
            conclusion = 'SIU Escalation — elevated risk indicators and anomaly flags warrant formal investigation.'
        elif is_anomaly or len(checklist) > 0:
            conclusion = 'Documentation Review — anomalous patterns detected; additional documentation required.'
        else:
            conclusion = 'Approved — claim parameters fall within standard actuarial thresholds across all agents.'

        outliers_str = ", ".join([o.get("type", "") for o in state.get("statistical_outliers", [])]) or "None"

        # Build the notification banner (only shown when LLM is unreachable)
        llm_notice = ""
        if not llm_available:
            llm_notice = (
                f"⚠️ **LLM Service Notice**: The AI language model is not reachable right now"
                f" ({llm_reason}). This summary is generated using deterministic rule-based"
                f" synthesis from verified agent findings.\n\n"
            )

        llm_summary = (
            f"{llm_notice}"
            f"### Executive Claim Brief: {claim_id}\n\n"
            f"**1. Incident Synopsis**: Insured filed claim for a {claim_data.get('incident_severity', '').lower()} "
            f"{claim_data.get('incident_type', '')} on {claim_data.get('incident_date', '')} totaling "
            f"€{float(claim_data.get('claim_amount', 0)):,.2f}.\n\n"
            f"**2. Policy Coverage Assessment**: {coverage_status}. Policyholder belongs to demographic class "
            f"'{risk_info.get('customer_subtype')}' with purchasing power tier {risk_info.get('purchasing_power_class')}/8.\n\n"
            f"**3. Risk & Anomaly Indicators**: Supervised Risk Probability is {risk_info.get('supervised_risk_probability', 0):.1%} "
            f"(Tier: {risk_info.get('preliminary_risk_tier')}). Detected statistical outliers: {outliers_str}. "
            f"Reporting delay: {claim_data.get('reporting_delay_days')} days.\n\n"
            f"**4. Historical Similarity**: Matched {len(similar_claims)} historical incidents in ChromaDB. "
            f"Overall pattern consistency: {state.get('retrieval_insights', 'Verified')}.\n\n"
            f"**5. Conclusive Recommendation**: {conclusion}"
        )

    llm_mode = "LLM-Powered" if (llm_available and llm_summary and not llm_summary.startswith("⚠️")) else f"Deterministic Fallback ({llm_reason})"
    audit_entry = {
        "timestamp": datetime.now().isoformat(),
        "agent": "Claims Summarization Agent",
        "action": "Case Synthesis",
        "details": f"Generated comprehensive executive claim brief for Reviewer. [Mode: {llm_mode}]"
    }

    return {
        "executive_summary": llm_summary,
        "audit_log": [audit_entry],
        "current_stage": "SUMMARIZATION_COMPLETE"
    }
