"""
Agent 2: Claims Risk Analysis Agent
-----------------------------------
Role: Analyzes claim characteristics, customer profile, and identifies risk indicators.
Tools: ClaimsRiskEngine (Supervised Risk Classifier) & Customer Dossier Lookup.
"""

import os
import sys
import pandas as pd
from datetime import datetime
from typing import Dict, Any

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

from task2_models_analytics.models.claims_risk_engine import ClaimsRiskEngine
from task3_multi_agent_system.state import ClaimsInvestigationState

models_path = os.path.join(ROOT_DIR, "task2_models_analytics", "models")
risk_engine = ClaimsRiskEngine.load(models_dir=models_path)

# Customer registry cache
CUSTOMERS_CSV = os.path.join(ROOT_DIR, "task1_data_preparation", "processed_data", "customers_clean.csv")
customers_cache = {}
if os.path.exists(CUSTOMERS_CSV):
    try:
        df_cust = pd.read_csv(CUSTOMERS_CSV)
        customers_cache = df_cust.set_index("customer_id").to_dict(orient="index")
    except Exception:
        pass


def claims_risk_analysis_agent_node(state: ClaimsInvestigationState) -> Dict[str, Any]:
    """LangGraph Node for the Claims Risk Analysis Agent."""
    claim_data = state.get("claim_data", {})
    customer_id = state.get("customer_id", "")
    policy_type = claim_data.get("policy_type", "Auto")
    policy_count = int(claim_data.get("policy_count", 0))

    # Fetch customer profile if not already present
    cust_profile = state.get("customer_profile") or customers_cache.get(customer_id, {})

    # Evaluate using the ML Risk Engine
    eval_result = risk_engine.evaluate_claim(claim_data)
    risk_prob = eval_result.get("risk_probability", 0.0)
    risk_tier = eval_result.get("risk_tier", "Low")

    # Policy Coverage Check
    if policy_count == 0:
        coverage_status = f"INVALID: No active policies on record for line '{policy_type}'"
    else:
        coverage_status = f"VALID: {policy_count} active policy/policies on record for '{policy_type}'"

    risk_analysis = {
        "supervised_risk_probability": risk_prob,
        "preliminary_risk_tier": risk_tier,
        "policy_coverage_status": coverage_status,
        "customer_subtype": cust_profile.get("customer_subtype_desc", "Standard"),
        "customer_main_type": cust_profile.get("customer_main_type_desc", "Standard"),
        "age_group": cust_profile.get("age_group_desc", "Unknown"),
        "purchasing_power_class": cust_profile.get("MKOOPKLA", claim_data.get("purchasing_power_class", 5)),
        "active_policies_total": cust_profile.get("total_policies_count", policy_count)
    }

    audit_entry = {
        "timestamp": datetime.now().isoformat(),
        "agent": "Claims Risk Analysis Agent",
        "action": "Policy & Risk Evaluation",
        "details": f"Evaluated coverage ({coverage_status}) and supervised risk score ({risk_prob:.1%})."
    }

    return {
        "customer_profile": cust_profile,
        "risk_analysis": risk_analysis,
        "policy_coverage_status": coverage_status,
        "audit_log": [audit_entry]
    }
