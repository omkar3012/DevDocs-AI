"""
Redis Worker for DevDocs AI (Alternative to Kafka)
Listens to Redis messages and processes uploaded documents for chunking and embedding
"""

import os
import json
import tempfile
import redis
import time
from typing import List, Dict, Any
from dotenv import load_dotenv

from supabase_client import get_supabase_client
from utils.loaders import DocumentLoader
from utils.splitters import DocumentSplitter
from rag_service import RAGService

load_dotenv()

class RedisWorker:
    def __init__(self):
        self.supabase = get_supabase_client()
        self.rag_service = RAGService()
        self.loader = DocumentLoader()
        self.splitter = DocumentSplitter()
        
        # Initialize Redis connection
        redis_url = os.getenv("REDIS_URL", "redis://localhost:6379")
        self.redis_client = redis.from_url(redis_url, decode_responses=True)
        self.queue_name = "doc-processing-queue"

    def process_document(self, doc_id: str, storage_path: str, doc_type: str, user_id: str, filename: str):
        """Process a document: load, chunk, embed, and store"""
        try:
            print(f"🔄 Processing document: {filename} (ID: {doc_id})")
            
            # Download file from Supabase Storage
            file_content = self.supabase.storage.from_("api-docs").download(storage_path)
            
            # Save to temporary file
            with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(filename)[1]) as temp_file:
                temp_file.write(file_content)
                temp_file_path = temp_file.name
            
            try:
                # Load document based on type
                if doc_type == "openapi":
                    documents = self.loader.load_openapi(temp_file_path)
                elif doc_type == "pdf":
                    documents = self.loader.load_pdf(temp_file_path)
                elif doc_type == "markdown":
                    documents = self.loader.load_markdown(temp_file_path)
                else:
                    raise ValueError(f"Unsupported document type: {doc_type}")
                
                # Split documents into chunks
                chunks = self.splitter.split_documents(documents)
                
                # Create embeddings and store in database
                self.store_chunks_with_embeddings(chunks, doc_id)
                
                # Update document status to ready
                self.supabase.table("api_documents").update(
                    {"status": "ready"}
                ).eq("id", doc_id).execute()
                
                print(f"✅ Successfully processed {len(chunks)} chunks for document {doc_id}")
                
            finally:
                # Clean up temporary file
                os.unlink(temp_file_path)
                
        except Exception as e:
            print(f"❌ Error processing document {doc_id}: {str(e)}")
            # Update document status to failed
            self.supabase.table("api_documents").update(
                {"status": "failed", "error": str(e)}
            ).eq("id", doc_id).execute()

    def store_chunks_with_embeddings(self, chunks: List[Dict], doc_id: str):
        """Store chunks with their embeddings in the database"""
        for i, chunk in enumerate(chunks):
            try:
                # Get embedding for chunk text
                embedding = self.rag_service.get_embedding(chunk["text"])
                
                # Prepare chunk data
                chunk_data = {
                    "doc_id": doc_id,
                    "chunk_text": chunk["text"],
                    "metadata": chunk.get("metadata", {}),
                    "embedding": embedding,
                    "chunk_index": i
                }
                
                # Insert into database
                result = self.supabase.table("api_chunks").insert(chunk_data).execute()
                
                if not result.data:
                    print(f"⚠️  Failed to store chunk {i} for document {doc_id}")
                    
            except Exception as e:
                print(f"❌ Error storing chunk {i} for document {doc_id}: {str(e)}")

    def run(self):
        """Main worker loop"""
        print("🚀 Starting Redis Worker...")
        print(f"📡 Listening to queue: {self.queue_name}")
        
        try:
            while True:
                try:
                    # Block and wait for messages (5 second timeout)
                    result = self.redis_client.blpop(self.queue_name, timeout=5)
                    
                    if result is None:
                        # No message within timeout, continue
                        continue
                    
                    # Parse message
                    queue_name, message_data = result
                    message = json.loads(message_data)
                    
                    print(f"📨 Received message: {message}")
                    
                    # Extract message data
                    doc_id = message.get("doc_id")
                    storage_path = message.get("storage_path")
                    doc_type = message.get("doc_type")
                    user_id = message.get("user_id")
                    filename = message.get("filename")
                    
                    if not all([doc_id, storage_path, doc_type, user_id, filename]):
                        print(f"⚠️  Invalid message format: {message}")
                        continue
                    
                    # Process the document
                    self.process_document(doc_id, storage_path, doc_type, user_id, filename)
                    
                except json.JSONDecodeError as e:
                    print(f"❌ Error parsing message: {str(e)}")
                    continue
                except Exception as e:
                    print(f"❌ Error processing message: {str(e)}")
                    continue
                    
        except KeyboardInterrupt:
            print("🛑 Shutting down Redis Worker...")
        except Exception as e:
            print(f"❌ Fatal error in worker: {str(e)}")
        finally:
            self.redis_client.close()

if __name__ == "__main__":
    worker = RedisWorker()
    worker.run()