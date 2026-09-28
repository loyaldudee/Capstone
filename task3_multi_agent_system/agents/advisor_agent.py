"""
Agent 6: Senior Claims Adjudication Advisor Agent (Adjuster Copilot)
-------------------------------------------------------------------
Role: Analyzes synthesized findings across all agents, provides strategic
decision recommendations, and generates rigorous claimant inquiry questions.
"""

import os
import sys
import json
import re
from datetime import datetime
from typing import Dict, Any, List

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

from task3_multi_agent_system.llm_client import generate_llm_response
from task3_multi_agent_system.state import ClaimsInvestigationState


def claims_advisor_agent_node(state: ClaimsInvestigationState) -> Dict[str, Any]:
    """LangGraph Node for the Senior Claims Adjudication Advisor Agent."""
    claim_id = state.get("claim_id", "UNKNOWN")
    claim_data = state.get("claim_data", {})
    customer_id = state.get("customer_id", "UNKNOWN")
    risk_info = state.get("risk_analysis", {})
    anomaly_info = state.get("anomaly_findings", {})
    outliers = state.get("statistical_outliers", [])
    checklist = state.get("siu_evidence_checklist", [])
    coverage_status = state.get("policy_coverage_status", "")
    
    claim_amount = float(claim_data.get("claim_amount", 0.0))
    policy_type = claim_data.get("policy_type", "Auto")
    incident_type = claim_data.get("incident_type", "Incident")
    severity = claim_data.get("incident_severity", "Moderate")
    incident_desc = str(claim_data.get("incident_description", "")).strip()
    delay = int(claim_data.get("reporting_delay_days", 0))
    police_report = claim_data.get("police_report_filed", "No")
    witness = claim_data.get("witness_present", "No")
    risk_prob = risk_info.get("supervised_risk_probability", 0.0)
    risk_tier = risk_info.get("preliminary_risk_tier", "Medium")

    words = incident_desc.split()
    is_vague_narrative = len(words) <= 3 or (len(words) < 7 and severity in ["Severe", "Catastrophic"])
    is_high_risk = risk_tier in ["High", "Critical"] or risk_prob > 0.6 or any("CRITICAL" in c for c in checklist)

    # Build prompt for LLM
    prompt = f"""You are the Senior Claims Adjudication Advisor Agent (Copilot for Senior Insurance Adjusters).
Analyze this claim file and provide structured strategic guidance for the human reviewer:

[CLAIM PROFILE]
- Claim ID: {claim_id} | Customer ID: {customer_id}
- Policy Line: {policy_type} | Incident Type: {incident_type} ({severity} Severity)
- Claimed Amount: €{claim_amount:,.2f}
- Incident Description: "{incident_desc}" (Word count: {len(words)})
- Policy Coverage Status: {coverage_status}
- Reporting Delay: {delay} days | Police Report: {police_report} | Witnesses: {witness}
- Risk Tier: {risk_tier} (Risk Probability: {risk_prob:.1%})
- Outliers Detected: {len(outliers)} ({[o.get('type') for o in outliers]})
- Evidence Flags: {checklist}

Respond in strictly valid JSON format with these exact keys:
{{
  "recommended_decision": "Documentation Review" | "SIU Escalation" | "Approved",
  "decision_rationale": "Clear 2-sentence rationale for the adjuster explaining why this decision is recommended.",
  "key_risk_drivers": ["bullet 1", "bullet 2", "bullet 3"],
  "claimant_inquiry_questions": [
    "Specific professional question 1 to ask the policyholder",
    "Specific professional question 2 to ask the policyholder",
    "Specific professional question 3 to ask the policyholder"
  ],
  "mandatory_documents": [
    "Mandatory document 1 required before disbursement",
    "Mandatory document 2 required before disbursement"
  ],
  "prefilled_adjuster_notes": "Formal adjuster sign-off rationale text ready to be recorded in audit ledger."
}}
"""

    guidance = None
    raw_llm = generate_llm_response(prompt, system_prompt="You are an expert Senior Insurance Adjuster Advisor. Output ONLY valid JSON.")
    if raw_llm:
        try:
            # Extract JSON block if surrounded by markdown code fences
            cleaned = re.sub(r"^```json\s*", "", raw_llm.strip())
            cleaned = re.sub(r"\s*```$", "", cleaned)
            guidance = json.loads(cleaned)
        except Exception:
            pass

    # High-Fidelity Deterministic Fallback if LLM unavailable or invalid JSON
    if not guidance or not isinstance(guidance, dict):
        if is_high_risk or any("CRITICAL" in c for c in checklist):
            rec = "SIU Escalation"
            rationale = (
                f"Elevated fraud or coverage risk detected ({risk_tier} tier, {risk_prob:.1%} probability). "
                f"Significant anomalies require formal special investigation prior to any financial authorization."
            )
        elif is_vague_narrative or "SUSPENDED" in coverage_status or len(checklist) > 0:
            rec = "Documentation Review"
            rationale = (
                f"Narrative detail is grossly insufficient ({len(words)} words: '{incident_desc}') to substantiate "
                f"a €{claim_amount:,.2f} {severity} loss. Claim must be suspended pending comprehensive factual verification."
            )
        else:
            rec = "Approved"
            rationale = (
                f"Claim satisfies standard actuarial underwriting parameters with consistent policy coverage "
                f"and acceptable latency ({delay} days)."
            )

        # Questions tailored to the policy type & loss
        questions = []
        if is_vague_narrative:
            questions.append(
                f"Please provide an exhaustive, chronological account of the incident on {claim_data.get('incident_date', 'the date of loss')}, including exact origin, cause, and timeline."
            )
        if policy_type in ["Fire", "Fire_Property", "Property"]:
            questions.append("Was the property occupied at the time of fire ignition, and were any emergency services or municipal fire brigades dispatched?")
            questions.append("Please identify the specific room or equipment where the fire initiated and state any heating or electrical installations nearby.")
            questions.append(f"Can you provide itemized repair and replacement invoices supporting the claimed amount of €{claim_amount:,.2f}?")
        elif policy_type in ["Auto", "Third Party"]:
            questions.append("Where did the collision occur, and what were the weather, road, and visibility conditions at the exact time of impact?")
            questions.append("Were there any third-party vehicles, passengers, or pedestrians involved, and were insurance details exchanged at the scene?")
        else:
            questions.append(f"Please describe the sequence of events and furnish proof of ownership for all items claimed under €{claim_amount:,.2f}.")

        if delay > 7:
            questions.append(f"What caused the {delay}-day delay between the incident date and filing this formal notification?")

        # Mandatory Documents
        docs = []
        if policy_type in ["Fire", "Fire_Property", "Property"]:
            docs.append("Official Municipal Fire Department Incident & Origin Report")
            docs.append("Certified General Contractor Itemized Scope of Damage Estimate")
            docs.append("Photographic and video documentation of structural & contents damage")
        elif policy_type in ["Auto", "Third Party"]:
            docs.append("Official Police Accident Investigation Report")
            docs.append("Authorized Body Shop Repair Estimate & Diagnostic Scan")
        else:
            docs.append("Independent Loss Assessor Detailed Inspection Dossier")
            docs.append("Proof of purchase receipts or valuation appraisal certificates")

        # Risk drivers
        drivers = []
        if is_vague_narrative:
            drivers.append(f"Narrative Insufficiency: Description '{incident_desc}' contains only {len(words)} word(s)")
        if claim_amount > 20000:
            drivers.append(f"High Monetary Exposure: Claimed €{claim_amount:,.2f} exceeds line thresholds")
        if delay > 7:
            drivers.append(f"Reporting Lag: {delay} days exceeds benchmark (0-7 days)")
        if "SUSPENDED" in coverage_status or "INVALID" in coverage_status:
            drivers.append(f"Coverage Alert: {coverage_status}")

        notes = (
            f"Advising {rec}. Loss narrative ('{incident_desc}') lacks substantiation for €{claim_amount:,.2f} {severity} loss. "
            f"Disbursement placed on hold pending receipt of certified third-party documentation and claimant clarification."
        )

        guidance = {
            "recommended_decision": rec,
            "decision_rationale": rationale,
            "key_risk_drivers": drivers or ["Standard review protocol indicated."],
            "claimant_inquiry_questions": questions[:4],
            "mandatory_documents": docs,
            "prefilled_adjuster_notes": notes
        }

    audit_entry = {
        "timestamp": datetime.now().isoformat(),
        "agent": "Adjudication Advisor Agent",
        "action": "Strategic Decision Formulation",
        "details": f"Formulated recommendation '{guidance.get('recommended_decision')}' with {len(guidance.get('claimant_inquiry_questions', []))} claimant inquiry prompts."
    }

    return {
        "advisor_guidance": guidance,
        "final_recommended_action": f"ADVISOR: {guidance.get('recommended_decision')} - {guidance.get('decision_rationale', '')[:80]}...",
        "audit_log": [audit_entry]
    }
