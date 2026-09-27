"""
Claims Vector Retrieval Engine (Agent Tool)
-------------------------------------------
Provides semantic vector similarity search over the claims knowledge base:
- Natural-language semantic querying (e.g. 'car skidded on black ice').
- Claim-to-claim similarity search by claim_id (Task 2 & 3).
- Hybrid metadata filtering (by policy_type, amount ranges).
- Tool interface for the Claims Retrieval Agent.
"""

import os
from typing import List, Dict, Any, Optional
import chromadb

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
VECTOR_STORE_DIR = os.path.join(BASE_DIR, "vector_store")
COLLECTION_NAME = "claims_semantic_knowledge_base"


class ClaimsVectorEngine:
    def __init__(self, vector_store_dir: str = VECTOR_STORE_DIR):
        self.vector_store_dir = vector_store_dir
        self.client = chromadb.PersistentClient(path=self.vector_store_dir)
        self.collection = self.client.get_collection(name=COLLECTION_NAME)

    @classmethod
    def load(cls, vector_store_dir: str = VECTOR_STORE_DIR):
        return cls(vector_store_dir=vector_store_dir)

    def search_similar_claims(
        self,
        query_text: str,
        policy_type: Optional[str] = None,
        top_k: int = 5
    ) -> List[Dict[str, Any]]:
        """
        Searches the knowledge base for claims matching a natural-language description.
        Optionally filters by policy_type (e.g., 'Auto', 'Fire_Property').
        """
        where_filter = None
        if policy_type:
            where_filter = {"policy_type": policy_type}

        results = self.collection.query(
            query_texts=[query_text],
            n_results=top_k,
            where=where_filter,
            include=["documents", "metadatas", "distances"]
        )

        formatted_results = []
        if results and results["ids"] and results["ids"][0]:
            ids = results["ids"][0]
            docs = results["documents"][0]
            metas = results["metadatas"][0]
            dists = results["distances"][0]

            for i in range(len(ids)):
                # Convert cosine distance to cosine similarity: sim = 1 - dist
                sim_score = round(float(1.0 - dists[i]), 4)
                meta = metas[i]

                formatted_results.append({
                    "claim_id": ids[i],
                    "similarity_score": sim_score,
                    "policy_type": meta.get("policy_type"),
                    "incident_type": meta.get("incident_type"),
                    "incident_severity": meta.get("incident_severity"),
                    "claim_amount": meta.get("claim_amount"),
                    "police_report_filed": meta.get("police_report_filed"),
                    "reporting_delay_days": meta.get("reporting_delay_days"),
                    "incident_description": docs[i]
                })

        return formatted_results

    def find_similar_by_claim_id(
        self,
        claim_id: str,
        top_k: int = 5
    ) -> List[Dict[str, Any]]:
        """
        Retrieves historical claims similar to a specific existing claim ID.
        Excludes the target claim itself from the returned results.
        """
        # Fetch the document of the target claim
        target = self.collection.get(ids=[claim_id], include=["documents", "metadatas"])
        if not target or not target["documents"]:
            return []

        target_text = target["documents"][0]
        # Query top_k + 1 to account for the target claim itself being returned
        results = self.collection.query(
            query_texts=[target_text],
            n_results=top_k + 1,
            include=["documents", "metadatas", "distances"]
        )

        similar_claims = []
        if results and results["ids"] and results["ids"][0]:
            ids = results["ids"][0]
            docs = results["documents"][0]
            metas = results["metadatas"][0]
            dists = results["distances"][0]

            for i in range(len(ids)):
                if ids[i] == claim_id:
                    continue  # Skip self
                sim_score = round(float(1.0 - dists[i]), 4)
                meta = metas[i]
                similar_claims.append({
                    "claim_id": ids[i],
                    "similarity_score": sim_score,
                    "policy_type": meta.get("policy_type"),
                    "incident_type": meta.get("incident_type"),
                    "incident_severity": meta.get("incident_severity"),
                    "claim_amount": meta.get("claim_amount"),
                    "incident_description": docs[i]
                })
                if len(similar_claims) >= top_k:
                    break

        return similar_claims


# Quick verification when executed directly
if __name__ == "__main__":
    import json
    engine = ClaimsVectorEngine.load()
    query = "car collided into utility pole on icy snowy road"
    print(f"Query: '{query}'")
    matches = engine.search_similar_claims(query, top_k=2)
    print("Top 2 Matches:")
    print(json.dumps(matches, indent=2))
