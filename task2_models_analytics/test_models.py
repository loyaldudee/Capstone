"""
Standalone Model Testing & Benchmark Script (Task 2 & 4)
--------------------------------------------------------
Tests the trained models and ClaimsRiskEngine against:
1. The full held-out test split with Confusion Matrix and classification metrics.
2. Specific real-world insurance claim edge cases (Normal, Coverage Mismatch, Outlier, Delayed).
"""

import os
import json
import joblib
import pandas as pd
import numpy as np
from sklearn.metrics import classification_report, confusion_matrix, roc_auc_score
from task2_models_analytics.models.claims_risk_engine import ClaimsRiskEngine

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR = os.path.dirname(BASE_DIR)
PROCESSED_DATA_DIR = os.path.join(ROOT_DIR, "task1_data_preparation", "processed_data")
if not os.path.exists(PROCESSED_DATA_DIR):
    PROCESSED_DATA_DIR = os.path.join(BASE_DIR, "processed_data")
MODELS_DIR = os.path.join(BASE_DIR, "models")


def run_full_benchmark():
    print("=" * 75)
    print(" 1. FULL HELD-OUT TEST BENCHMARK EVALUATION")
    print("=" * 75)

    # Load data
    df_claims = pd.read_csv(os.path.join(PROCESSED_DATA_DIR, "claims_knowledge_base.csv"))
    df_gt = pd.read_csv(os.path.join(PROCESSED_DATA_DIR, "claims_ground_truth.csv"))
    df = pd.merge(df_claims, df_gt, on="claim_id")

    # Load inference engine
    engine = ClaimsRiskEngine.load(MODELS_DIR)

    # Evaluate all claims through the engine
    print(f"Evaluating {len(df):,} claims through ClaimsRiskEngine...")
    predictions = []
    probabilities = []
    risk_tiers = []

    for _, row in df.iterrows():
        claim_dict = row.to_dict()
        res = engine.evaluate_claim(claim_dict)
        predictions.append(1 if res["is_anomaly"] else 0)
        probabilities.append(res["composite_risk_score"])
        risk_tiers.append(res["risk_tier"])

    y_true = df["ground_truth_is_anomaly"].values
    y_pred = np.array(predictions)
    y_scores = np.array(probabilities)

    # Metrics
    cm = confusion_matrix(y_true, y_pred)
    tn, fp, fn, tp = cm.ravel()
    auc = roc_auc_score(y_true, y_scores)

    print("\nConfusion Matrix:")
    print(f"  [TN: {tn:4d}]  (Legitimate claims correctly approved)")
    print(f"  [FP: {fp:4d}]  (Legitimate claims flagged for review - False Positives)")
    print(f"  [FN: {fn:4d}]  (Anomalous claims missed - False Negatives)")
    print(f"  [TP: {tp:4d}]  (Anomalous claims correctly caught - True Positives)")

    print(f"\nOverall ROC-AUC Score: {auc:.4f}")
    print("\nClassification Report:")
    print(classification_report(y_true, y_pred, target_names=["Normal Claim", "High-Risk Anomaly"]))

    print("\nRisk Tier Distribution Across Dataset:")
    tier_counts = pd.Series(risk_tiers).value_counts()
    for tier, count in tier_counts.items():
        print(f"  • {tier:8s}: {count:5d} ({count/len(df):.1%})")


def run_scenario_edge_cases():
    print("\n" + "=" * 75)
    print(" 2. LIVE SCENARIO EDGE-CASE TESTING")
    print("=" * 75)

    engine = ClaimsRiskEngine.load(MODELS_DIR)

    scenarios = [
        {
            "title": "Scenario A: Standard Legitimate Fender Bender",
            "claim": {
                "claim_id": "SCEN-001",
                "policy_type": "Auto",
                "policy_count": 2,
                "policy_contribution_tier": 5,
                "purchasing_power_class": 6,
                "claim_amount": 2800.0,
                "incident_type": "Rear-End",
                "incident_severity": "Minor",
                "reporting_delay_days": 2,
                "police_report_filed": "Yes",
                "witness_present": "Yes",
                "prior_claims_count": 0
            }
        },
        {
            "title": "Scenario B: Coverage Mismatch (Claim on line with 0 active policies)",
            "claim": {
                "claim_id": "SCEN-002",
                "policy_type": "Boat_Marine",
                "policy_count": 0,  # Zero active policies!
                "policy_contribution_tier": 0,
                "purchasing_power_class": 4,
                "claim_amount": 14500.0,
                "incident_type": "Marina Collision",
                "incident_severity": "Moderate",
                "reporting_delay_days": 5,
                "police_report_filed": "Yes",
                "witness_present": "No",
                "prior_claims_count": 0
            }
        },
        {
            "title": "Scenario C: Exaggerated Claim Amount Outlier",
            "claim": {
                "claim_id": "SCEN-003",
                "policy_type": "Auto",
                "policy_count": 1,
                "policy_contribution_tier": 3,
                "purchasing_power_class": 3,
                "claim_amount": 78500.0,  # Extreme outlier!
                "incident_type": "Collision",
                "incident_severity": "Severe",
                "reporting_delay_days": 3,
                "police_report_filed": "Yes",
                "witness_present": "No",
                "prior_claims_count": 0
            }
        },
        {
            "title": "Scenario D: Suspicious 60-Day Reporting Delay without Police Report",
            "claim": {
                "claim_id": "SCEN-004",
                "policy_type": "Fire_Property",
                "policy_count": 1,
                "policy_contribution_tier": 4,
                "purchasing_power_class": 5,
                "claim_amount": 32000.0,
                "incident_type": "Electrical Fire",
                "incident_severity": "Severe",
                "reporting_delay_days": 62,  # Suspicious delay!
                "police_report_filed": "No",
                "witness_present": "No",
                "prior_claims_count": 1
            }
        }
    ]

    for item in scenarios:
        print(f"\n--- {item['title']} ---")
        res = engine.evaluate_claim(item["claim"])
        print(f"  • Composite Risk Score : {res['composite_risk_score']:.3f} (Tier: {res['risk_tier']})")
        print(f"  • Anomaly Detected     : {res['is_anomaly']}")
        print(f"  • SIU Handoff Required : {res['requires_investigation_handoff']}")
        print(f"  • Recommended Action   : {res['recommendation']}")
        print(f"  • Evidence Summary     : {res['evidence_summary']}")


if __name__ == "__main__":
    run_full_benchmark()
    run_scenario_edge_cases()
