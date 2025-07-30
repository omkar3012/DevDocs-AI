"""
Kafka Producer for DevDocs AI
Handles sending events to Kafka topics for document processing
"""

import os
import json
from typing import Dict, Any
from kafka import KafkaProducer as KafkaProducerClient
from dotenv import load_dotenv
from datetime import datetime

load_dotenv()

class KafkaProducer:
    def __init__(self):
        self.bootstrap_servers = os.getenv("KAFKA_BOOTSTRAP_SERVERS", "localhost:9092")
        try:
            self.producer = KafkaProducerClient(
                bootstrap_servers=self.bootstrap_servers,
                value_serializer=lambda v: json.dumps(v).encode('utf-8'),
                key_serializer=lambda k: k.encode('utf-8') if k else None
            )
        except Exception as e:
            print(f"Warning: Could not connect to Kafka: {e}")
            self.producer = None

    def send_message(self, topic: str, message: Dict[str, Any], key: str = None):
        """Send a message to a Kafka topic"""
        if self.producer is None:
            print(f"Warning: Kafka producer not available, skipping message to {topic}")
            return False
        try:
            future = self.producer.send(topic, value=message, key=key)
            # Wait for the message to be sent
            record_metadata = future.get(timeout=10)
            print(f"Message sent to {topic} partition {record_metadata.partition} offset {record_metadata.offset}")
            return True
        except Exception as e:
            print(f"Error sending message to Kafka: {str(e)}")
            return False

    def send_document_upload_event(self, doc_id: str, storage_path: str, doc_type: str, user_id: str, filename: str):
        """Send document upload event to processing pipeline"""
        event = {
            "event_type": "document_upload",
            "doc_id": doc_id,
            "storage_path": storage_path,
            "doc_type": doc_type,
            "user_id": user_id,
            "filename": filename,
            "timestamp": str(datetime.utcnow())
        }
        return self.send_message("api-doc-upload", event, key=doc_id)

    def send_query_log_event(self, query: str, doc_id: str, user_id: str, response_time_ms: int):
        """Send query log event for analytics"""
        event = {
            "event_type": "query_log",
            "query": query,
            "doc_id": doc_id,
            "user_id": user_id,
            "response_time_ms": response_time_ms,
            "timestamp": str(datetime.utcnow())
        }
        return self.send_message("query-logs", event, key=user_id)

    def send_feedback_event(self, query: str, answer: str, was_helpful: bool, user_id: str, doc_id: str = None):
        """Send feedback event for analytics"""
        event = {
            "event_type": "feedback",
            "query": query,
            "answer": answer,
            "was_helpful": was_helpful,
            "user_id": user_id,
            "doc_id": doc_id,
            "timestamp": str(datetime.utcnow())
        }
        return self.send_message("feedback", event, key=user_id)

    def close(self):
        """Close the Kafka producer"""
        if self.producer:
            self.producer.close()

# Global producer instance
kafka_producer = KafkaProducer() 