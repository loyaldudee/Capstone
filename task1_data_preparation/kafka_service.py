"""
Kafka Service Manager & Producer Wrapper
-----------------------------------------
Manages connection to Apache Kafka broker on port 9092.
Publishes raw claim messages to topic 'raw-claims-ingest'.
Provides graceful fallback to in-memory queue if Kafka broker is unavailable.
"""

import os
import json
from datetime import datetime
from typing import Dict, Any, List

try:
    from kafka import KafkaProducer
    KAFKA_AVAILABLE = True
except ImportError:
    KAFKA_AVAILABLE = False


KAFKA_BOOTSTRAP_SERVERS = os.getenv("KAFKA_BOOTSTRAP_SERVERS", "localhost:9092")
TOPIC_RAW_CLAIMS = "raw-claims-ingest"

# In-Memory audit log buffer for UI stream monitoring
INGESTION_LOG_BUFFER: List[Dict[str, Any]] = []


def log_ingestion_event(stage: str, claim_id: str, message: str, status: str = "INFO"):
    """Appends an event log to the in-memory stream log buffer."""
    event = {
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "stage": stage,
        "claim_id": claim_id,
        "message": message,
        "status": status
    }
    INGESTION_LOG_BUFFER.append(event)
    # Keep buffer capped at 200 items
    if len(INGESTION_LOG_BUFFER) > 200:
        INGESTION_LOG_BUFFER.pop(0)


import socket

def is_kafka_broker_reachable(host: str = "localhost", port: int = 9092, timeout: float = 0.2) -> bool:
    """Fast non-blocking socket check to verify if Kafka broker on port 9092 is active."""
    try:
        host_name = host.split(":")[0]
        port_num = int(host.split(":")[1]) if ":" in host else port
        with socket.create_connection((host_name, port_num), timeout=timeout):
            return True
    except (socket.timeout, ConnectionRefusedError, OSError):
        return False


class KafkaProducerManager:
    _producer = None

    @classmethod
    def get_producer(cls):
        if not KAFKA_AVAILABLE:
            return None
            
        # Check socket connection to broker
        if not is_kafka_broker_reachable():
            cls._producer = None
            return None

        if cls._producer is None:
            try:
                cls._producer = KafkaProducer(
                    bootstrap_servers=KAFKA_BOOTSTRAP_SERVERS,
                    value_serializer=lambda v: json.dumps(v).encode("utf-8"),
                    request_timeout_ms=1000,
                    max_block_ms=1000
                )
                print(f"[Kafka Producer] Connected to Kafka broker at {KAFKA_BOOTSTRAP_SERVERS}")
            except Exception as e:
                print(f"[Kafka Producer Warning] Kafka connection failed: {e}")
                cls._producer = None
                
        return cls._producer


    @classmethod
    def publish_raw_claim(cls, raw_claim_dict: Dict[str, Any]) -> bool:
        """
        Publishes raw claim payload to Kafka topic 'raw-claims-ingest'.
        Returns True if published to Kafka, False if fallback mode was used.
        """
        cid = str(raw_claim_dict.get("claim_id", "RAW-CLAIM"))
        producer = cls.get_producer()

        if producer is not None:
            try:
                producer.send(TOPIC_RAW_CLAIMS, value=raw_claim_dict)
                producer.flush()
                log_ingestion_event(
                    stage="Kafka Producer",
                    claim_id=cid,
                    message=f"Event published to Kafka topic '{TOPIC_RAW_CLAIMS}' at {KAFKA_BOOTSTRAP_SERVERS}",
                    status="SUCCESS"
                )
                return True
            except Exception as e:
                print(f"[Kafka Publish Warning] Failed to publish message to Kafka: {e}")

        # Fallback log
        log_ingestion_event(
            stage="Ingestion Pipeline (Fallback)",
            claim_id=cid,
            message="Kafka broker offline/fallback. Passing payload directly to Sanitizer worker.",
            status="WARNING"
        )
        return False
