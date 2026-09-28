"""
Streaming Consumer & Ingestion Worker Service
----------------------------------------------
Background worker that processes incoming raw claim messages (from Kafka or direct REST intake),
executes DataSanitizer cleaning, persists sanitized records to SQLAlchemy RDBMS (`insurance.db`),
and indexes dense embeddings in ChromaDB Vector Store.
"""

import os
import sys
import time
from typing import Dict, Any, List

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

from database import SessionLocal
from models import Claim, Customer
from task1_data_preparation.data_sanitizer import DataSanitizer
from task1_data_preparation.kafka_service import log_ingestion_event
import chromadb

VECTOR_STORE_DIR = os.path.join(ROOT_DIR, "task2_models_analytics", "vector_store")
COLLECTION_NAME = "claims_semantic_knowledge_base"


class IngestionWorker:
    @staticmethod
    def process_and_persist_claim(raw_payload: Dict[str, Any]) -> Dict[str, Any]:
        """
        Processes a raw claim payload through sanitation, saves to RDBMS,
        and indexes narrative in ChromaDB.
        """
        db = SessionLocal()
        try:
            # 1. Sanitize payload
            existing_count = db.query(Claim).count()
            cleaned = DataSanitizer.clean_claim_payload(raw_payload, next_claim_num=existing_count + 1)
            cid = cleaned["claim_id"]

            log_ingestion_event(
                stage="DataSanitizer",
                claim_id=cid,
                message=f"Sanitized payload: Policy '{cleaned['policy_type']}', Amount €{cleaned['claim_amount']:,.2f}, Delay {cleaned['reporting_delay_days']} days.",
                status="SUCCESS"
            )

            # 2. Persist or update in RDBMS
            existing_claim = db.query(Claim).filter(Claim.claim_id == cid).first()
            if not existing_claim:
                # Ensure customer exists or create default customer profile
                cust_id = cleaned["customer_id"]
                existing_cust = db.query(Customer).filter(Customer.customer_id == cust_id).first()
                if not existing_cust:
                    new_cust = Customer(
                        customer_id=cust_id,
                        customer_subtype="Ingested Policyholder",
                        customer_main_type="Standard Client",
                        age_group="30-45 years",
                        purchasing_power_class=cleaned["purchasing_power_class"],
                        total_policies_count=cleaned["policy_count"],
                        active_product_lines_count=1,
                        has_car_policy=True if cleaned["policy_type"] == "Auto" else False,
                        has_fire_policy=True if cleaned["policy_type"] == "Fire_Property" else False,
                        has_boat_policy=True if cleaned["policy_type"] == "Boat_Marine" else False,
                        has_life_policy=True if cleaned["policy_type"] == "Life_Health" else False,
                        has_accident_policy=True if cleaned["policy_type"] == "Accident_Liability" else False
                    )
                    db.add(new_cust)

                new_claim = Claim(
                    claim_id=cleaned["claim_id"],
                    customer_id=cleaned["customer_id"],
                    policy_type=cleaned["policy_type"],
                    policy_count=cleaned["policy_count"],
                    policy_contribution_tier=cleaned["policy_contribution_tier"],
                    purchasing_power_class=cleaned["purchasing_power_class"],
                    claim_amount=cleaned["claim_amount"],
                    incident_type=cleaned["incident_type"],
                    incident_severity=cleaned["incident_severity"],
                    incident_date=cleaned["incident_date"],
                    claim_date=cleaned["claim_date"],
                    reporting_delay_days=cleaned["reporting_delay_days"],
                    police_report_filed=cleaned["police_report_filed"],
                    witness_present=cleaned["witness_present"],
                    prior_claims_count=cleaned["prior_claims_count"],
                    incident_description=cleaned["incident_description"],
                    claim_status="Pending Review"
                )
                db.add(new_claim)
                db.commit()

                log_ingestion_event(
                    stage="SQLAlchemy RDBMS",
                    claim_id=cid,
                    message=f"Persisted new record to database table 'claims' (Total records: {db.query(Claim).count():,}).",
                    status="SUCCESS"
                )

            # 3. Index into ChromaDB Vector Store
            try:
                os.makedirs(VECTOR_STORE_DIR, exist_ok=True)
                client = chromadb.PersistentClient(path=VECTOR_STORE_DIR)
                collection = client.get_or_create_collection(
                    name=COLLECTION_NAME,
                    metadata={"hnsw:space": "cosine"}
                )

                meta = {
                    "claim_id": cleaned["claim_id"],
                    "customer_id": cleaned["customer_id"],
                    "policy_type": cleaned["policy_type"],
                    "incident_type": cleaned["incident_type"],
                    "incident_severity": cleaned["incident_severity"],
                    "claim_amount": cleaned["claim_amount"],
                    "reporting_delay_days": cleaned["reporting_delay_days"],
                    "police_report_filed": cleaned["police_report_filed"],
                    "witness_present": cleaned["witness_present"],
                    "prior_claims_count": cleaned["prior_claims_count"],
                    "incident_date": cleaned["incident_date"]
                }

                collection.upsert(
                    ids=[cleaned["claim_id"]],
                    documents=[cleaned["incident_description"]],
                    metadatas=[meta]
                )

                log_ingestion_event(
                    stage="ChromaDB Vector Store",
                    claim_id=cid,
                    message=f"Upserted narrative embedding to collection '{COLLECTION_NAME}' (Total vectors: {collection.count():,}).",
                    status="SUCCESS"
                )
            except Exception as ve:
                print(f"[Vector Ingest Warning] Failed to index to ChromaDB: {ve}")
                log_ingestion_event(
                    stage="ChromaDB Vector Store",
                    claim_id=cid,
                    message=f"Vector indexing warning: {ve}",
                    status="WARNING"
                )

            return cleaned

        except Exception as e:
            db.rollback()
            log_ingestion_event(
                stage="Ingestion Worker Error",
                claim_id=raw_payload.get("claim_id", "UNKNOWN"),
                message=f"Failed to process claim: {e}",
                status="ERROR"
            )
            raise e
        finally:
            db.close()
