"""
Comprehensive Endpoint Verification Test for Aegis FastAPI Microservice
"""
import sys
import os

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

from fastapi.testclient import TestClient
from server import app

def run_api_tests():
    print("=" * 60)
    print("  AEGIS MICROSERVICE ENDPOINT VALIDATION SUITE")
    print("=" * 60)

    with TestClient(app) as client:
        # Test 1: Dashboard UI endpoint
        res = client.get("/")
        assert res.status_code == 200, f"Expected 200, got {res.status_code}"
        assert "Aegis" in res.text
        print("[PASS] GET / -> Successfully serves index.html")

        # Test 2: System Stats endpoint
        res = client.get("/api/stats")
        assert res.status_code == 200
        stats = res.json()
        assert stats["total_claims"] == 1800
        print(f"[PASS] GET /api/stats -> Total claims: {stats['total_claims']:,}, Pending: {stats['pending_review']:,}")

        # Test 3: Claims Explorer pagination and query
        res = client.get("/api/claims?page=1&limit=5&policy_type=Auto")
        assert res.status_code == 200
        claims_data = res.json()
        assert len(claims_data["claims"]) == 5
        sample_claim = claims_data["claims"][0]
        cid = sample_claim["claim_id"]
        print(f"[PASS] GET /api/claims -> Retrieved page 1 (5 items). Sample: {cid} ({sample_claim['policy_type']})")

        # Test 4: Claim Dossier with Customer Profiling
        res = client.get(f"/api/claims/{cid}")
        assert res.status_code == 200
        dossier = res.json()
        assert dossier["claim_id"] == cid
        assert "customer" in dossier and dossier["customer"]["customer_id"] == dossier["customer_id"]
        print(f"[PASS] GET /api/claims/{cid} -> Dossier loaded with Customer: {dossier['customer']['customer_subtype']}")

        # Test 5: Semantic Vector Search via ChromaDB
        res = client.post("/api/search/similar", json={
            "query_text": "Single vehicle collision on icy road during snowstorm",
            "top_k": 3
        })
        assert res.status_code == 200
        search_results = res.json()
        assert len(search_results) == 3
        top_match = search_results[0]
        print(f"[PASS] POST /api/search/similar -> Vector search matched: {top_match['claim_id']} ({top_match['similarity_score'] * 100:.1f}% similarity)")

        # Test 6: Human Reviewer Adjudication Gate
        res = client.post("/api/adjuster/decision", json={
            "claim_id": cid,
            "decision": "Approved",
            "notes": "Verified against vehicle telemetry and police incident report.",
            "adjuster_name": "Lead Forensic Adjuster"
        })
        assert res.status_code == 200
        decision_resp = res.json()
        assert decision_resp["success"] is True
        assert decision_resp["new_status"] == "Approved"
        print(f"[PASS] POST /api/adjuster/decision -> Decision 'Approved' successfully persisted for {cid}")

        # Verify status update in database
        res_check = client.get(f"/api/claims/{cid}")
        assert res_check.json()["claim_status"] == "Approved"
        print(f"[PASS] Claim status verification: {res_check.json()['claim_status']}")

        # Test 7: Evaluation Metrics Endpoint
        res = client.get("/api/evaluation/metrics")
        assert res.status_code == 200
        eval_metrics = res.json()
        auc = eval_metrics["criteria_2_risk_and_anomaly_detection"]["roc_auc_score"]
        hit1 = eval_metrics["criteria_1_similar_claim_retrieval"]["hit_rate_at_1"]
        print(f"[PASS] GET /api/evaluation/metrics -> ROC-AUC: {auc}, Hit@1: {hit1 * 100:.1f}%")

    print("\n" + "=" * 60)
    print("  ALL 7 FASTAPI MICROSERVICE ENDPOINTS VERIFIED & PASSING!")
    print("=" * 60)

if __name__ == "__main__":
    run_api_tests()
