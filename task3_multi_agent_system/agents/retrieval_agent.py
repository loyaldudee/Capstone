"""
Agent 1: Claims Retrieval Agent
-------------------------------
Role: Retrieves similar historical claims and relevant information from the ChromaDB vector store.
Tool: ClaimsVectorEngine
"""

import os
import sys
from datetime import datetime
from typing import Dict, Any

# Ensure parent path resolution
ROOT_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

from task2_models_analytics.models.claims_vector_engine import ClaimsVectorEngine
from task3_multi_agent_system.state import ClaimsInvestigationState

# Initialize tool
vector_store_path = os.path.join(ROOT_DIR, "task2_models_analytics", "vector_store")
vector_engine = ClaimsVectorEngine.load(vector_store_dir=vector_store_path)


def claims_retrieval_agent_node(state: ClaimsInvestigationState) -> Dict[str, Any]:
    """LangGraph Node for the Claims Retrieval Agent."""
    claim_data = state.get("claim_data", {})
    claim_id = state.get("claim_id", "")
    description = claim_data.get("incident_description", "")
    policy_type = claim_data.get("policy_type", None)

    # 1. Retrieve similar historical claims
    if claim_id and claim_id.startswith("CLM-"):
        similar = vector_engine.find_similar_by_claim_id(claim_id=claim_id, top_k=3)
    else:
        similar = vector_engine.search_similar_claims(query_text=description, policy_type=policy_type, top_k=3)

    # 2. Extract synthesis insights
    insights = []
    if similar:
        avg_amt = sum(s.get("claim_amount", 0) for s in similar) / len(similar)
        top_sim = similar[0].get("similarity_score", 0)
        top_id = similar[0].get("claim_id", "N/A")
        insights.append(f"Retrieved {len(similar)} similar historical claims (Average historical payout: €{avg_amt:,.2f}).")
        insights.append(f"Closest match: {top_id} (Cosine Similarity: {top_sim:.1%}).")
    else:
        insights.append("No prior claims matched above similarity threshold.")

    audit_entry = {
        "timestamp": datetime.now().isoformat(),
        "agent": "Claims Retrieval Agent",
        "action": "Semantic Vector Search",
        "details": f"Retrieved {len(similar)} similar incidents from ChromaDB."
    }

    return {
        "similar_claims": similar,
        "retrieval_insights": " ".join(insights),
        "audit_log": [audit_entry]
    }
