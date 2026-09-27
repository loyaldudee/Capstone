"""
Step 2.1: Model Training & Explainability Engine (PRD Task 2)
------------------------------------------------------------
Trains:
1. Unsupervised Anomaly Detection Model (Isolation Forest) on observable claim features.
2. Supervised Risk Prioritization Model (Random Forest Classifier) on a 80/20 train/test split.
3. Feature Attribution & Explainability Layer that produces evidence-backed risk indicators.

Exports to 'models/':
- preprocessor.joblib
- isolation_forest.joblib
- risk_classifier.joblib
- claims_risk_engine.py (Reusable inference class & agent tool)
- model_metrics.json (Comprehensive evaluation report on held-out test split)
"""

import os
import json
import joblib
import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import IsolationForest, RandomForestClassifier
from sklearn.metrics import (
    roc_auc_score,
    precision_score,
    recall_score,
    f1_score,
    accuracy_score,
    classification_report
)

# Paths
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR = os.path.dirname(BASE_DIR)
PROCESSED_DATA_DIR = os.path.join(ROOT_DIR, "task1_data_preparation", "processed_data")
if not os.path.exists(PROCESSED_DATA_DIR):
    PROCESSED_DATA_DIR = os.path.join(BASE_DIR, "processed_data")
MODELS_DIR = os.path.join(BASE_DIR, "models")
os.makedirs(MODELS_DIR, exist_ok=True)

# Feature definitions (Pure observable features - ZERO leakage)
NUMERICAL_FEATURES = [
    "claim_amount",
    "reporting_delay_days",
    "policy_count",
    "policy_contribution_tier",
    "purchasing_power_class",
    "prior_claims_count"
]

CATEGORICAL_FEATURES = [
    "policy_type",
    "incident_type",
    "incident_severity",
    "police_report_filed",
    "witness_present"
]

ALL_MODEL_FEATURES = NUMERICAL_FEATURES + CATEGORICAL_FEATURES


def train_and_export_models():
    print("=" * 70)
    print(" STEP 2.1: CLAIMS ANOMALY & RISK DETECTION MODEL TRAINING")
    print("=" * 70)

    # 1. Load Datasets
    print("[1/5] Loading clean observable claims and ground truth...")
    claims_path = os.path.join(PROCESSED_DATA_DIR, "claims_knowledge_base.csv")
    gt_path = os.path.join(PROCESSED_DATA_DIR, "claims_ground_truth.csv")

    df_claims = pd.read_csv(claims_path)
    df_gt = pd.read_csv(gt_path)

    # Merge on claim_id strictly for training/evaluation
    df = pd.merge(df_claims, df_gt[["claim_id", "ground_truth_is_anomaly", "ground_truth_anomaly_type"]], on="claim_id")
    print(f"      Loaded {len(df):,} claims. Anomaly rate: {df['ground_truth_is_anomaly'].mean():.2%}")

    # 2. Build Preprocessor Pipeline
    print("[2/5] Building feature preprocessor pipeline...")
    preprocessor = ColumnTransformer(
        transformers=[
            ("num", StandardScaler(), NUMERICAL_FEATURES),
            ("cat", OneHotEncoder(handle_unknown="ignore", sparse_output=False), CATEGORICAL_FEATURES)
        ]
    )

    X = df[ALL_MODEL_FEATURES]
    y = df["ground_truth_is_anomaly"].values

    # Train / Test Split (80% train, 20% test stratified)
    X_train_df, X_test_df, y_train, y_test = train_test_split(
        X, y, test_size=0.20, random_state=42, stratify=y
    )

    preprocessor.fit(X_train_df)
    X_train_proc = preprocessor.transform(X_train_df)
    X_test_proc = preprocessor.transform(X_test_df)
    print(f"      Training set: {len(X_train_df):,} | Test set: {len(X_test_df):,} | Processed features: {X_train_proc.shape[1]}")

    # 3. Train Model 1: Unsupervised Isolation Forest (Anomaly Detection)
    print("[3/5] Training Unsupervised Isolation Forest (Anomaly Detection)...")
    iso_forest = IsolationForest(
        n_estimators=150,
        contamination=0.13,  # Calibrated to expected insurance anomaly frequency
        random_state=42,
        n_jobs=-1
    )
    iso_forest.fit(X_train_proc)

    # Evaluate Isolation Forest on test set
    # IsolationForest returns -1 for outlier, 1 for inlier
    iso_preds_raw = iso_forest.predict(X_test_proc)
    iso_preds_binary = np.where(iso_preds_raw == -1, 1, 0)
    iso_scores = -iso_forest.score_samples(X_test_proc)  # Higher = more anomalous

    # Normalize anomaly score to [0, 1]
    iso_score_min = iso_scores.min()
    iso_score_max = iso_scores.max()
    iso_scores_norm = (iso_scores - iso_score_min) / (iso_score_max - iso_score_min + 1e-8)

    iso_roc = roc_auc_score(y_test, iso_scores_norm)
    iso_prec = precision_score(y_test, iso_preds_binary, zero_division=0)
    iso_rec = recall_score(y_test, iso_preds_binary, zero_division=0)
    iso_f1 = f1_score(y_test, iso_preds_binary, zero_division=0)

    print(f"      Isolation Forest Test Metrics: ROC-AUC={iso_roc:.4f}, Precision={iso_prec:.4f}, Recall={iso_rec:.4f}, F1={iso_f1:.4f}")

    # 4. Train Model 2: Supervised Risk Prioritization Model (Random Forest Classifier)
    print("[4/5] Training Supervised Risk Classifier (Random Forest)...")
    risk_classifier = RandomForestClassifier(
        n_estimators=200,
        max_depth=8,
        min_samples_leaf=4,
        class_weight="balanced",
        random_state=42,
        n_jobs=-1
    )
    risk_classifier.fit(X_train_proc, y_train)

    rf_probs = risk_classifier.predict_proba(X_test_proc)[:, 1]
    rf_preds = risk_classifier.predict(X_test_proc)

    rf_roc = roc_auc_score(y_test, rf_probs)
    rf_prec = precision_score(y_test, rf_preds, zero_division=0)
    rf_rec = recall_score(y_test, rf_preds, zero_division=0)
    rf_f1 = f1_score(y_test, rf_preds, zero_division=0)
    rf_acc = accuracy_score(y_test, rf_preds)

    print(f"      Risk Classifier Test Metrics:  ROC-AUC={rf_roc:.4f}, Precision={rf_prec:.4f}, Recall={rf_rec:.4f}, F1={rf_f1:.4f}, Accuracy={rf_acc:.4f}")

    # Extract Feature Importances
    cat_feature_names = preprocessor.named_transformers_["cat"].get_feature_names_out(CATEGORICAL_FEATURES)
    feature_names = list(NUMERICAL_FEATURES) + list(cat_feature_names)
    importances = risk_classifier.feature_importances_
    sorted_idx = np.argsort(importances)[::-1]
    top_features = [{"feature": feature_names[i], "importance": round(float(importances[i]), 4)} for i in sorted_idx[:10]]

    # 5. Export Models and Metrics
    print("[5/5] Exporting models and evaluation metrics to 'models/'...")
    joblib.dump(preprocessor, os.path.join(MODELS_DIR, "preprocessor.joblib"))
    joblib.dump(iso_forest, os.path.join(MODELS_DIR, "isolation_forest.joblib"))
    joblib.dump(risk_classifier, os.path.join(MODELS_DIR, "risk_classifier.joblib"))

    # Save benchmark metrics report
    metrics_report = {
        "evaluation_timestamp": pd.Timestamp.now().isoformat(),
        "test_records_count": len(y_test),
        "test_anomalies_count": int(y_test.sum()),
        "models": {
            "isolation_forest_unsupervised": {
                "roc_auc": round(float(iso_roc), 4),
                "precision": round(float(iso_prec), 4),
                "recall": round(float(iso_rec), 4),
                "f1_score": round(float(iso_f1), 4),
                "role": "Anomaly Detection Agent Tool"
            },
            "random_forest_supervised": {
                "roc_auc": round(float(rf_roc), 4),
                "precision": round(float(rf_prec), 4),
                "recall": round(float(rf_rec), 4),
                "f1_score": round(float(rf_f1), 4),
                "accuracy": round(float(rf_acc), 4),
                "role": "Risk Analysis Agent & Prioritization Tool"
            }
        },
        "top_predictive_features": top_features,
        "input_features": {
            "numerical": NUMERICAL_FEATURES,
            "categorical": CATEGORICAL_FEATURES
        }
    }

    metrics_path = os.path.join(MODELS_DIR, "model_metrics.json")
    with open(metrics_path, "w", encoding="utf-8") as f:
        json.dump(metrics_report, f, indent=2)

    # Compute baseline reference statistics by policy_type for explainability
    policy_stats = df.groupby("policy_type")["claim_amount"].agg(["median", "std", "mean"]).to_dict(orient="index")
    stats_path = os.path.join(MODELS_DIR, "policy_baseline_stats.json")
    with open(stats_path, "w", encoding="utf-8") as f:
        json.dump(policy_stats, f, indent=2)

    print(f"      Saved: {os.path.join(MODELS_DIR, 'preprocessor.joblib')}")
    print(f"      Saved: {os.path.join(MODELS_DIR, 'isolation_forest.joblib')}")
    print(f"      Saved: {os.path.join(MODELS_DIR, 'risk_classifier.joblib')}")
    print(f"      Saved: {metrics_path}")
    print(f"      Saved: {stats_path}")
    print("=" * 70)
    print(" MODEL TRAINING COMPLETED SUCCESSFULLY!")
    print("=" * 70)


if __name__ == "__main__":
    train_and_export_models()
