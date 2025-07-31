"""
Redis Producer for DevDocs AI
Sends document processing messages to Redis queue
"""

import os
import json
import redis
from typing import Dict, Any
from dotenv import load_dotenv

load_dotenv()

class RedisProducer:
    def __init__(self):
        redis_url = os.getenv("REDIS_URL", "redis://localhost:6379")
        self.redis_client = redis.from_url(redis_url, decode_responses=True)
        self.queue_name = "doc-processing-queue"

    def send_message(self, queue_name: str, message: Dict[str, Any]):
        """Send a message to Redis queue"""
        try:
            message_json = json.dumps(message)
            self.redis_client.rpush(queue_name, message_json)
            print(f"📤 Sent message to {queue_name}: {message}")
        except Exception as e:
            print(f"❌ Failed to send message to Redis: {str(e)}")
            raise

    def send_document_processing_message(self, doc_id: str, storage_path: str, doc_type: str, user_id: str, filename: str):
        """Send document processing message"""
        message = {
            "doc_id": doc_id,
            "storage_path": storage_path,
            "doc_type": doc_type,
            "user_id": user_id,
            "filename": filename
        }
        self.send_message(self.queue_name, message)

    def close(self):
        """Close Redis connection"""
        self.redis_client.close()