"""
Agent 3: Anomaly Detection Agent
--------------------------------
Role: Investigates unusual claim patterns, amount outliers, and statistical discrepancies.
Tools: ClaimsRiskEngine (Isolation Forest) & Policy Baseline Comparator.
"""

import os
import sys
import json
from datetime import datetime
from typing import Dict, Any

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

from task2_models_analytics.models.claims_risk_engine import ClaimsRiskEngine
from task3_multi_agent_system.state import ClaimsInvestigationState

models_path = os.path.join(ROOT_DIR, "task2_models_analytics", "models")
risk_engine = ClaimsRiskEngine.load(models_dir=models_path)


def anomaly_detection_agent_node(state: ClaimsInvestigationState) -> Dict[str, Any]:
    """LangGraph Node for the Anomaly Detection Agent."""
    claim_data = state.get("claim_data", {})
    eval_result = risk_engine.evaluate_claim(claim_data)

    anomaly_score = eval_result.get("anomaly_score", 0.0)
    is_anomaly = eval_result.get("is_anomaly", False)
    risk_drivers = eval_result.get("risk_drivers", [])

    # Compile structured statistical outlier report
    outliers = []
    claim_amount = float(claim_data.get("claim_amount", 0.0))
    policy_type = claim_data.get("policy_type", "Auto")
    delay = int(claim_data.get("reporting_delay_days", 0))
    severity = claim_data.get("incident_severity", "Moderate")
    police_report = claim_data.get("police_report_filed", "Yes")

    baseline = risk_engine.baseline_stats.get(policy_type, {"median": 4500, "std": 3000})
    median_amt = baseline.get("median", 4500)
    std_amt = baseline.get("std", 3000)

    # 1. Amount Check
    if claim_amount > (median_amt + 2.0 * std_amt):
        ratio = round(claim_amount / max(median_amt, 1), 1)
        outliers.append({
            "type": "Amount Outlier",
            "metric": f"€{claim_amount:,.2f}",
            "baseline": f"Median €{median_amt:,.2f} (std: €{std_amt:,.2f})",
            "significance": f"{ratio}x above expected line median"
        })

    # 2. Delay Check
    if delay > 30:
        outliers.append({
            "type": "Reporting Lag Outlier",
            "metric": f"{delay} days",
            "baseline": "0 - 7 days standard",
            "significance": "Unusually prolonged notification latency"
        })

    # 3. Documentation Check
    if severity in ["Severe", "Catastrophic"] and police_report == "No":
        outliers.append({
            "type": "Documentation Void",
            "metric": f"{severity} severity loss",
            "baseline": "Police Investigation Report Required",
            "significance": "High-value catastrophic damage lacking independent verification"
        })

    # 4. Narrative Substance & Vagueness Void Check
    desc = str(claim_data.get("incident_description", "")).strip()
    words = desc.split()
    if (len(words) <= 3 and claim_amount > 5000) or (len(words) < 6 and severity in ["Severe", "Catastrophic"]):
        outliers.append({
            "type": "Narrative Insufficiency Void",
            "metric": f"'{desc}' ({len(words)} word{'s' if len(words) != 1 else ''})",
            "baseline": "Forensic narrative detail (origin, context, damage scope)",
            "significance": f"Critical lack of incident circumstances for a €{claim_amount:,.2f} {severity} loss"
        })

    anomaly_findings = {
        "isolation_forest_anomaly_score": anomaly_score,
        "is_statistical_outlier": is_anomaly or len(outliers) > 0,
        "outlier_count": len(outliers),
        "primary_risk_drivers": risk_drivers,
        "composite_risk_score": eval_result.get("composite_risk_score", 0.0)
    }

    audit_entry = {
        "timestamp": datetime.now().isoformat(),
        "agent": "Anomaly Detection Agent",
        "action": "Multivariate Outlier Inspection",
        "details": f"Flagged {len(outliers)} statistical outliers (Anomaly score: {anomaly_score:.3f})."
    }

    return {
        "anomaly_findings": anomaly_findings,
        "statistical_outliers": outliers,
        "requires_investigation_handoff": eval_result.get("requires_investigation_handoff", False) or len(outliers) > 0,
        "audit_log": [audit_entry]
    }
