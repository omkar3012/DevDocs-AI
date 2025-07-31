"""
Embedding Worker for DevDocs AI
Listens to Kafka events and processes uploaded documents for chunking and embedding
"""

import os
import json
import tempfile
from typing import List, Dict, Any
from kafka import KafkaConsumer
from dotenv import load_dotenv

from supabase_client import get_supabase_client
from utils.loaders import DocumentLoader
from utils.splitters import DocumentSplitter
from rag_service import RAGService

load_dotenv()

class EmbeddingWorker:
    def __init__(self):
        self.supabase = get_supabase_client()
        self.rag_service = RAGService()
        self.loader = DocumentLoader()
        self.splitter = DocumentSplitter()
        
        # Initialize Kafka consumer
        self.consumer = KafkaConsumer(
            'api-doc-upload',
            bootstrap_servers=os.getenv("KAFKA_BOOTSTRAP_SERVERS", "localhost:9092"),
            auto_offset_reset='earliest',
            enable_auto_commit=True,
            group_id='embedding-worker-group',
            value_deserializer=lambda x: json.loads(x.decode('utf-8'))
        )

    def process_document(self, doc_id: str, storage_path: str, doc_type: str, user_id: str, filename: str):
        """Process a document: load, chunk, embed, and store"""
        try:
            print(f"Processing document: {filename} (ID: {doc_id})")
            
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
                
                print(f"Successfully processed {len(chunks)} chunks for document {doc_id}")
                
            finally:
                # Clean up temporary file
                os.unlink(temp_file_path)
                
        except Exception as e:
            print(f"Error processing document {doc_id}: {str(e)}")
            # Update document status to failed
            self.supabase.table("api_documents").update(
                {"status": "failed", "error": str(e)}
            ).eq("id", doc_id).execute()

    def store_chunks_with_embeddings(self, chunks: List[Dict], doc_id: str):
        """Store chunks with their embeddings in the database"""
        try:
            for i, chunk in enumerate(chunks):
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
                    print(f"Failed to store chunk {i} for document {doc_id}")
            
            # Update document chunk count (status already updated to 'ready')
            self.supabase.table("api_documents").update(
                {"chunk_count": len(chunks)}
            ).eq("id", doc_id).execute()
            
        except Exception as e:
            print(f"Error storing chunks for document {doc_id}: {str(e)}")
            raise

    def run(self):
        """Main worker loop"""
        print("Starting Embedding Worker...")
        print(f"Listening to Kafka topic: api-doc-upload")
        print(f"Bootstrap servers: {os.getenv('KAFKA_BOOTSTRAP_SERVERS', 'localhost:9092')}")
        
        try:
            for message in self.consumer:
                try:
                    event = message.value
                    print(f"Received event: {event}")
                    
                    # Extract event data
                    doc_id = event.get("doc_id")
                    storage_path = event.get("storage_path")
                    doc_type = event.get("doc_type")
                    user_id = event.get("user_id")
                    filename = event.get("filename")
                    
                    if not all([doc_id, storage_path, doc_type, user_id, filename]):
                        print(f"Invalid event data: {event}")
                        continue
                    
                    # Process the document
                    self.process_document(doc_id, storage_path, doc_type, user_id, filename)
                    
                except Exception as e:
                    print(f"Error processing message: {str(e)}")
                    continue
                    
        except KeyboardInterrupt:
            print("Shutting down Embedding Worker...")
        finally:
            self.consumer.close()

if __name__ == "__main__":
    worker = EmbeddingWorker()
    worker.run() 