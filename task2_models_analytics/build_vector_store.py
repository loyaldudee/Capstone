"""
Step 2.2: Vector Store Indexing Script (Task 2 & 3)
---------------------------------------------------
Ingests all 1,800 incident descriptions from 'processed_data/claims_knowledge_base.csv',
generates dense vector embeddings, and stores them in a persistent ChromaDB index
located at 'vector_store/' with complete metadata for hybrid semantic retrieval.
"""

import os
import pandas as pd
import chromadb
from chromadb.config import Settings

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR = os.path.dirname(BASE_DIR)
PROCESSED_DATA_DIR = os.path.join(ROOT_DIR, "task1_data_preparation", "processed_data")
if not os.path.exists(PROCESSED_DATA_DIR):
    PROCESSED_DATA_DIR = os.path.join(BASE_DIR, "processed_data")
VECTOR_STORE_DIR = os.path.join(BASE_DIR, "vector_store")
COLLECTION_NAME = "claims_semantic_knowledge_base"


def build_vector_store():
    print("=" * 70)
    print(" STEP 2.2: BUILDING CHROMADB VECTOR STORE FOR CLAIMS RETRIEVAL")
    print("=" * 70)

    # 1. Load Claims Knowledge Base
    claims_path = os.path.join(PROCESSED_DATA_DIR, "claims_knowledge_base.csv")
    print(f"[1/4] Loading claims from {claims_path}...")
    df_claims = pd.read_csv(claims_path)
    total_claims = len(df_claims)
    print(f"      Total claims to index: {total_claims:,}")

    # 2. Initialize Persistent Chroma Client
    print(f"[2/4] Initializing persistent ChromaDB at '{VECTOR_STORE_DIR}'...")
    os.makedirs(VECTOR_STORE_DIR, exist_ok=True)
    client = chromadb.PersistentClient(path=VECTOR_STORE_DIR)

    # Delete existing collection if rebuilding
    existing_collections = [c.name for c in client.list_collections()]
    if COLLECTION_NAME in existing_collections:
        print(f"      Resetting existing collection '{COLLECTION_NAME}'...")
        client.delete_collection(COLLECTION_NAME)

    collection = client.create_collection(
        name=COLLECTION_NAME,
        metadata={"hnsw:space": "cosine"}  # Cosine similarity for semantic search
    )

    # 3. Prepare Documents and Metadatas
    print("[3/4] Preparing text narratives and metadata tags...")
    ids = []
    documents = []
    metadatas = []

    for _, row in df_claims.iterrows():
        cid = str(row["claim_id"])
        desc = str(row["incident_description"])

        meta = {
            "claim_id": cid,
            "customer_id": str(row["customer_id"]),
            "policy_type": str(row["policy_type"]),
            "incident_type": str(row["incident_type"]),
            "incident_severity": str(row["incident_severity"]),
            "claim_amount": float(row["claim_amount"]),
            "reporting_delay_days": int(row["reporting_delay_days"]),
            "police_report_filed": str(row["police_report_filed"]),
            "witness_present": str(row["witness_present"]),
            "prior_claims_count": int(row["prior_claims_count"]),
            "incident_date": str(row["incident_date"])
        }

        ids.append(cid)
        documents.append(desc)
        metadatas.append(meta)

    # 4. Batch Embed & Add to ChromaDB
    batch_size = 250
    print(f"[4/4] Generating vector embeddings in batches of {batch_size}...")
    for i in range(0, total_claims, batch_size):
        end_idx = min(i + batch_size, total_claims)
        collection.add(
            ids=ids[i:end_idx],
            documents=documents[i:end_idx],
            metadatas=metadatas[i:end_idx]
        )
        print(f"      Indexed claims {i+1} to {end_idx} of {total_claims}...")

    print(f"      Verification: Collection count in ChromaDB = {collection.count():,}")
    print("=" * 70)
    print(" CHROMADB VECTOR STORE BUILT AND PERSISTED SUCCESSFULLY!")
    print("=" * 70)


if __name__ == "__main__":
    build_vector_store()
