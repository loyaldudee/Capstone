"""
Data Ingestion API Router (APIRouter)
--------------------------------------
Provides RESTful endpoints for manual single-claim ingestion, bulk CSV streaming upload,
and live Kafka event audit logs for the Ingestion Portal UI.

Architecture: All ingestion flows exclusively through Kafka.
  1. UI/API -> POST /api/ingest/claim -> Kafka Producer -> Topic 'raw-claims-ingest'
  2. Background KafkaConsumerWorker polls the topic and persists to DB + ChromaDB.
"""

import io
import csv
import json
import threading
from typing import Dict, Any, List, Optional
from fastapi import APIRouter, UploadFile, File, HTTPException, Body, status

from task1_data_preparation.kafka_service import KafkaProducerManager, INGESTION_LOG_BUFFER, log_ingestion_event
from task1_data_preparation.streaming_worker import IngestionWorker

ingest_router = APIRouter(prefix="/api/ingest", tags=["Data Ingestion & Kafka Pipeline"])


# ---------------------------------------------------------------------------
# Background Kafka Consumer Thread
# ---------------------------------------------------------------------------
_consumer_thread: Optional[threading.Thread] = None
_consumer_running = False


def start_kafka_consumer():
    """Starts the background Kafka consumer thread if not already running."""
    global _consumer_thread, _consumer_running
    if _consumer_running:
        return

    try:
        from kafka import KafkaConsumer
    except ImportError:
        print("[Kafka Consumer] kafka-python not installed. Consumer disabled.")
        return

    from task1_data_preparation.kafka_service import is_kafka_broker_reachable, KAFKA_BOOTSTRAP_SERVERS, TOPIC_RAW_CLAIMS

    if not is_kafka_broker_reachable():
        print("[Kafka Consumer] Broker not reachable. Consumer not started.")
        return

    def _consume_loop():
        global _consumer_running
        _consumer_running = True
        print(f"[Kafka Consumer] Starting consumer on topic '{TOPIC_RAW_CLAIMS}'...")
        try:
            consumer = KafkaConsumer(
                TOPIC_RAW_CLAIMS,
                bootstrap_servers=KAFKA_BOOTSTRAP_SERVERS,
                value_deserializer=lambda m: json.loads(m.decode("utf-8")),
                auto_offset_reset="latest",
                enable_auto_commit=True,
                group_id="aegis-ingestion-worker",
                consumer_timeout_ms=5000,
                session_timeout_ms=10000,
                request_timeout_ms=15000,
            )
            print(f"[Kafka Consumer] Connected and listening on '{TOPIC_RAW_CLAIMS}'.")
            log_ingestion_event(
                stage="Kafka Consumer",
                claim_id="SYSTEM",
                message=f"Consumer connected to topic '{TOPIC_RAW_CLAIMS}'. Awaiting messages...",
                status="SUCCESS"
            )

            while _consumer_running:
                # Poll with timeout so the thread can be stopped
                msg_pack = consumer.poll(timeout_ms=2000)
                for tp, messages in msg_pack.items():
                    for message in messages:
                        payload = message.value
                        try:
                            log_ingestion_event(
                                stage="Kafka Consumer",
                                claim_id=str(payload.get("claim_id", "RAW")),
                                message=f"Consumed message from partition {message.partition}, offset {message.offset}. Processing...",
                                status="INFO"
                            )
                            cleaned = IngestionWorker.process_and_persist_claim(payload)
                            log_ingestion_event(
                                stage="Kafka Consumer",
                                claim_id=cleaned.get("claim_id", "UNKNOWN"),
                                message=f"Successfully persisted claim '{cleaned['claim_id']}' to DB & Vector Store via Kafka pipeline.",
                                status="SUCCESS"
                            )
                        except Exception as e:
                            log_ingestion_event(
                                stage="Kafka Consumer Error",
                                claim_id=str(payload.get("claim_id", "UNKNOWN")),
                                message=f"Consumer processing failed: {e}",
                                status="ERROR"
                            )

        except Exception as e:
            print(f"[Kafka Consumer] Consumer loop error: {e}")
            log_ingestion_event(
                stage="Kafka Consumer",
                claim_id="SYSTEM",
                message=f"Consumer error: {e}",
                status="ERROR"
            )
        finally:
            _consumer_running = False
            print("[Kafka Consumer] Consumer thread stopped.")

    _consumer_thread = threading.Thread(target=_consume_loop, daemon=True, name="kafka-consumer-worker")
    _consumer_thread.start()


# ---------------------------------------------------------------------------
# API Endpoints
# ---------------------------------------------------------------------------

@ingest_router.post("/claim", summary="Submit Single Claim Payload (Kafka Streaming)")
def submit_single_claim(payload: Dict[str, Any] = Body(...)):
    """
    Submits a single raw claim payload (manual form intake).
    Publishes event to Kafka topic 'raw-claims-ingest'.
    The background Kafka consumer will pick it up, sanitize, and persist.
    If Kafka is unavailable, falls back to direct processing.
    """
    try:
        # Attempt to publish to Kafka
        published_to_kafka = KafkaProducerManager.publish_raw_claim(payload)

        if published_to_kafka:
            # Start consumer if not already running
            start_kafka_consumer()

            log_ingestion_event(
                stage="API Gateway",
                claim_id=str(payload.get("claim_id", "NEW")),
                message=f"Claim payload published to Kafka. Consumer will process and persist.",
                status="SUCCESS"
            )

            return {
                "success": True,
                "message": "Claim published to Kafka topic 'raw-claims-ingest'. Processing via streaming pipeline.",
                "published_to_kafka": True,
                "cleaned_data": {
                    "claim_id": f"CLM-INGEST-QUEUED",
                    "policy_type": payload.get("policy_type", "Unknown"),
                    "claim_amount": payload.get("claim_amount", 0),
                    "incident_type": payload.get("incident_type", "Unknown"),
                    "incident_severity": payload.get("incident_severity", "Unknown"),
                    "incident_description": payload.get("incident_description", ""),
                    "status": "Queued via Kafka — consumer will persist shortly."
                }
            }
        else:
            # Kafka unavailable — fallback to direct processing
            cleaned_record = IngestionWorker.process_and_persist_claim(payload)

            log_ingestion_event(
                stage="API Gateway (Fallback)",
                claim_id=cleaned_record.get("claim_id", "UNKNOWN"),
                message=f"Kafka offline. Claim processed directly via fallback pipeline.",
                status="WARNING"
            )

            return {
                "success": True,
                "message": "Kafka offline. Claim processed directly via fallback pipeline.",
                "published_to_kafka": False,
                "cleaned_data": cleaned_record
            }
    except Exception as e:
        log_ingestion_event(
            stage="API Gateway Error",
            claim_id=str(payload.get("claim_id", "UNKNOWN")),
            message=f"Ingestion failed: {str(e)}",
            status="ERROR"
        )
        raise HTTPException(status_code=400, detail=f"Ingestion failed: {str(e)}")


@ingest_router.post("/csv", summary="Upload & Stream Batch Claims CSV")
async def upload_batch_csv(file: UploadFile = File(...)):
    """
    Uploads a CSV file of claims, reads records, publishes each row to Kafka stream.
    The background consumer handles persistence.
    """
    if not file.filename.endswith(".csv"):
        raise HTTPException(status_code=400, detail="Only .csv files are supported.")

    try:
        content = await file.read()
        text_stream = io.StringIO(content.decode("utf-8-sig"))
        reader = csv.DictReader(text_stream)

        rows = list(reader)
        if not rows:
            raise HTTPException(status_code=400, detail="CSV file is empty.")

        log_ingestion_event(
            stage="CSV Batch Upload",
            claim_id="BATCH",
            message=f"Received CSV file '{file.filename}' with {len(rows):,} records. Enqueuing for streaming ingestion...",
            status="INFO"
        )

        published_kafka_count = 0
        direct_processed_count = 0

        for row in rows:
            if KafkaProducerManager.publish_raw_claim(row):
                published_kafka_count += 1
            else:
                # Fallback: process directly if Kafka is down
                IngestionWorker.process_and_persist_claim(row)
                direct_processed_count += 1

        # Start consumer to process the Kafka messages
        if published_kafka_count > 0:
            start_kafka_consumer()

        return {
            "success": True,
            "filename": file.filename,
            "total_records_ingested": published_kafka_count + direct_processed_count,
            "kafka_messages_published": published_kafka_count,
            "direct_fallback_count": direct_processed_count,
            "mode": "Kafka Streaming" if published_kafka_count > 0 else "Direct Fallback"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"CSV Batch Ingestion error: {str(e)}")


@ingest_router.get("/logs", summary="Get Live Streaming Ingestion Audit Logs")
def get_ingestion_logs(limit: int = 50):
    """Returns recent live event logs from the streaming ingestion audit buffer."""
    return {"logs": INGESTION_LOG_BUFFER[-limit:]}


@ingest_router.get("/status", summary="Get Kafka & Ingestion Pipeline Health")
def get_pipeline_status():
    """Returns Kafka broker connectivity and streaming pipeline operational status."""
    producer = KafkaProducerManager.get_producer()
    return {
        "kafka_connected": producer is not None,
        "bootstrap_servers": "localhost:9092",
        "topic": "raw-claims-ingest",
        "mode": "Kafka Streaming (Live)" if producer is not None else "Direct Pipeline (Fallback)",
        "consumer_active": _consumer_running,
        "total_events_logged": len(INGESTION_LOG_BUFFER)
    }
