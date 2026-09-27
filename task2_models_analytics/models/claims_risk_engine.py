"""
Claims Risk & Anomaly Inference Engine (Agent Tool)
---------------------------------------------------
Provides a unified interface for Multi-Agent workflows and FastAPI endpoints:
- Evaluates observable claim features.
- Computes Isolation Forest anomaly scores.
- Computes Supervised Risk probabilities and risk tiers.
- Formulates quantified, explainable risk drivers and evidence briefs (PRD Task 2).
"""

import os
import json
import joblib
import numpy as np
import pandas as pd
from typing import Dict, Any, List

MODELS_DIR = os.path.dirname(os.path.abspath(__file__))


class ClaimsRiskEngine:
    def __init__(self, models_dir: str = MODELS_DIR):
        self.models_dir = models_dir
        self.preprocessor = None
        self.iso_forest = None
        self.risk_classifier = None
        self.baseline_stats = {}
        self._load_artifacts()

    def _load_artifacts(self):
        prep_path = os.path.join(self.models_dir, "preprocessor.joblib")
        iso_path = os.path.join(self.models_dir, "isolation_forest.joblib")
        rf_path = os.path.join(self.models_dir, "risk_classifier.joblib")
        stats_path = os.path.join(self.models_dir, "policy_baseline_stats.json")

        if os.path.exists(prep_path):
            self.preprocessor = joblib.load(prep_path)
        if os.path.exists(iso_path):
            self.iso_forest = joblib.load(iso_path)
        if os.path.exists(rf_path):
            self.risk_classifier = joblib.load(rf_path)
        if os.path.exists(stats_path):
            with open(stats_path, "r", encoding="utf-8") as f:
                self.baseline_stats = json.load(f)

    @classmethod
    def load(cls, models_dir: str = MODELS_DIR):
        return cls(models_dir=models_dir)

    def evaluate_claim(self, claim: Dict[str, Any]) -> Dict[str, Any]:
        """
        Evaluates a single claim dictionary with observable features and returns
        comprehensive risk, anomaly, and explainability metrics.
        """
        required_cols = [
            "claim_amount", "reporting_delay_days", "policy_count",
            "policy_contribution_tier", "purchasing_power_class", "prior_claims_count",
            "policy_type", "incident_type", "incident_severity",
            "police_report_filed", "witness_present"
        ]

        # Extract features into DataFrame
        input_data = {col: [claim.get(col, 0)] for col in required_cols}
        df_input = pd.DataFrame(input_data)

        # 1. Transform features
        X_proc = self.preprocessor.transform(df_input)

        # 2. Isolation Forest Anomaly Scoring
        iso_pred_raw = self.iso_forest.predict(X_proc)[0]  # -1 = anomaly, 1 = normal
        is_iso_anomaly = bool(iso_pred_raw == -1)
        raw_score = -self.iso_forest.score_samples(X_proc)[0]
        # Calibrated normalized anomaly score (0.0 to 1.0)
        anomaly_score = round(float(np.clip(raw_score * 1.8 - 0.2, 0.05, 0.98)), 3)

        # 3. Supervised Risk Classification
        risk_prob = round(float(self.risk_classifier.predict_proba(X_proc)[0, 1]), 3)

        # 4. Composite Risk Score (Weighted blend of ML probability and Anomaly Score)
        composite_score = round(float(0.65 * risk_prob + 0.35 * anomaly_score), 3)

        # Assign Risk Tier
        if composite_score >= 0.75:
            risk_tier = "Critical"
        elif composite_score >= 0.50:
            risk_tier = "High"
        elif composite_score >= 0.25:
            risk_tier = "Medium"
        else:
            risk_tier = "Low"

        # 5. Explainable Risk Factors (Evidence Extraction)
        risk_drivers = []
        evidence_points = []

        claim_amount = float(claim.get("claim_amount", 0))
        policy_type = claim.get("policy_type", "Auto")
        reporting_delay = int(claim.get("reporting_delay_days", 0))
        policy_count = int(claim.get("policy_count", 1))
        purchasing_power = int(claim.get("purchasing_power_class", 5))
        prior_claims = int(claim.get("prior_claims_count", 0))
        police_report = claim.get("police_report_filed", "Yes")
        severity = claim.get("incident_severity", "Moderate")

        # Baseline comparison
        baseline = self.baseline_stats.get(policy_type, {"median": 4500, "std": 3000})
        median_amt = baseline.get("median", 4500)
        std_amt = baseline.get("std", 3000)

        # Check A: Policy Coverage Mismatch
        if policy_count == 0:
            risk_drivers.append({
                "factor": "Policy Coverage Mismatch",
                "severity": "Critical",
                "details": f"Policyholder holds zero active policies on record for line: {policy_type}"
            })
            evidence_points.append(f"Coverage Mismatch: Claim filed under '{policy_type}' but policy count is 0.")

        # Check B: Amount Discrepancy
        if claim_amount > (median_amt + 2.5 * std_amt):
            ratio = round(claim_amount / max(median_amt, 1), 1)
            risk_drivers.append({
                "factor": "Unusual Claim Amount",
                "severity": "High",
                "details": f"Claim amount €{claim_amount:,.2f} is {ratio}x higher than line median (€{median_amt:,.2f})"
            })
            evidence_points.append(f"Amount Outlier: €{claim_amount:,.2f} exceeds line median by {ratio}x.")

        # Check C: Reporting Delay
        if reporting_delay > 30:
            risk_drivers.append({
                "factor": "Prolonged Reporting Delay",
                "severity": "High",
                "details": f"Claim was reported {reporting_delay} days post-incident without expedited notification"
            })
            evidence_points.append(f"Reporting Delay: Notification lagged {reporting_delay} days.")

        # Check D: Major Incident Documentation
        if severity in ["Severe", "Catastrophic"] and police_report == "No":
            risk_drivers.append({
                "factor": "Lack of Official Documentation",
                "severity": "Medium",
                "details": f"{severity} severity incident reported without an official police investigation report"
            })
            evidence_points.append(f"Documentation Gap: {severity} incident without police report.")

        # Check E: Repeated Velocity
        if prior_claims >= 2:
            risk_drivers.append({
                "factor": "Elevated Claim Velocity",
                "severity": "Medium",
                "details": f"Insured has {prior_claims} prior historical claims on record"
            })
            evidence_points.append(f"History Indicator: Policyholder has {prior_claims} prior claims.")

        if not evidence_points:
            evidence_points.append("Standard claim profile; valid policy coverage; loss amount within expected actuarial bounds.")

        # Recommended Action for Reviewer / Multi-Agent Handoff
        if composite_score >= 0.70 or policy_count == 0:
            recommendation = "Escalate to Special Investigation Unit (SIU) for In-Depth Manual Review"
            requires_investigation_handoff = True
        elif composite_score >= 0.40:
            recommendation = "Request Additional Supporting Receipts & Witness Statements"
            requires_investigation_handoff = False
        else:
            recommendation = "Fast-Track Cleared for Standard Settlement"
            requires_investigation_handoff = False

        return {
            "claim_id": claim.get("claim_id", "UNKNOWN"),
            "composite_risk_score": composite_score,
            "risk_probability": risk_prob,
            "anomaly_score": anomaly_score,
            "is_anomaly": is_iso_anomaly or (composite_score >= 0.65),
            "risk_tier": risk_tier,
            "recommendation": recommendation,
            "requires_investigation_handoff": requires_investigation_handoff,
            "risk_drivers": risk_drivers,
            "evidence_summary": " | ".join(evidence_points)
        }


# Quick test when executed standalone
if __name__ == "__main__":
    engine = ClaimsRiskEngine.load()
    test_claim = {
        "claim_id": "TEST-001",
        "policy_type": "Auto",
        "policy_count": 0,  # Coverage mismatch
        "policy_contribution_tier": 4,
        "purchasing_power_class": 5,
        "claim_amount": 34500.0,  # Outlier
        "incident_type": "Collision",
        "incident_severity": "Severe",
        "reporting_delay_days": 45,  # Delay
        "police_report_filed": "No",
        "witness_present": "No",
        "prior_claims_count": 1
    }
    result = engine.evaluate_claim(test_claim)
    print("Test Evaluation Result:")
    print(json.dumps(result, indent=2))
