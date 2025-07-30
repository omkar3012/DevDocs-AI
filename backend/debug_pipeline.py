#!/usr/bin/env python3
"""
Debug script for document processing pipeline
Checks the entire flow from upload to chunk storage
"""

import os
import sys
import json
from dotenv import load_dotenv

# Add the current directory to the path so we can import our modules
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from supabase_client import get_supabase_client
from kafka_producer import KafkaProducer
from embedding_worker import EmbeddingWorker
from utils.loaders import DocumentLoader
from utils.splitters import DocumentSplitter
from rag_service import RAGService

def debug_document_pipeline():
    """Debug the entire document processing pipeline"""
    print("🔍 Debugging Document Processing Pipeline...")
    
    # Load environment variables
    load_dotenv()
    
    # Check environment variables
    print("\n📋 Environment Check:")
    huggingface_token = os.getenv("HUGGINGFACEHUB_API_TOKEN")
    supabase_url = os.getenv("SUPABASE_URL")
    supabase_key = os.getenv("SUPABASE_SERVICE_ROLE_KEY")
    kafka_servers = os.getenv("KAFKA_BOOTSTRAP_SERVERS", "localhost:9092")
    
    print(f"   Hugging Face Token: {'✅ Set' if huggingface_token and huggingface_token != 'your_huggingface_token_here' else '❌ Not set'}")
    print(f"   Supabase URL: {'✅ Set' if supabase_url else '❌ Not set'}")
    print(f"   Supabase Key: {'✅ Set' if supabase_key else '❌ Not set'}")
    print(f"   Kafka Servers: {kafka_servers}")
    
    # Check database connection and tables
    print("\n🗄️ Database Check:")
    try:
        supabase = get_supabase_client()
        
        # Check documents table
        result = supabase.table("api_documents").select("count", count="exact").execute()
        doc_count = result.count if result.count is not None else 0
        print(f"   Documents in database: {doc_count}")
        
        # Check chunks table
        result = supabase.table("api_chunks").select("count", count="exact").execute()
        chunk_count = result.count if result.count is not None else 0
        print(f"   Chunks in database: {chunk_count}")
        
        # Get sample documents with status
        if doc_count > 0:
            docs = supabase.table("api_documents").select("*").limit(5).execute()
            print(f"   Sample documents:")
            for doc in docs.data:
                status = doc.get('status', 'unknown')
                chunk_count = doc.get('chunk_count', 0)
                print(f"     - {doc['name']} (ID: {doc['id']})")
                print(f"       Status: {status}, Chunks: {chunk_count}")
                print(f"       Type: {doc['type']}, Path: {doc['storage_path']}")
        
    except Exception as e:
        print(f"❌ Database connection failed: {str(e)}")
        return
    
    # Check Kafka connection
    print("\n📡 Kafka Check:")
    try:
        kafka_producer = KafkaProducer()
        if kafka_producer.producer:
            print("   ✅ Kafka producer connected")
            
            # Test message sending
            test_event = {
                "event_type": "test",
                "message": "test message",
                "timestamp": "2024-01-01T00:00:00Z"
            }
            success = kafka_producer.send_message("test-topic", test_event)
            print(f"   Test message sent: {'✅ Success' if success else '❌ Failed'}")
        else:
            print("   ❌ Kafka producer not connected")
    except Exception as e:
        print(f"   ❌ Kafka connection failed: {str(e)}")
    
    # Check document loaders
    print("\n📄 Document Loaders Check:")
    try:
        loader = DocumentLoader()
        print("   ✅ Document loader initialized")
        
        # Check if we can create a test document
        from langchain.schema import Document
        test_doc = Document(page_content="Test content", metadata={"source": "test"})
        print("   ✅ Test document created")
        
    except Exception as e:
        print(f"   ❌ Document loader failed: {str(e)}")
    
    # Check document splitters
    print("\n✂️ Document Splitters Check:")
    try:
        splitter = DocumentSplitter()
        print("   ✅ Document splitter initialized")
        
        # Test splitting
        from langchain.schema import Document
        test_docs = [Document(page_content="This is a test document with some content to split.", metadata={"source": "test"})]
        chunks = splitter.split_documents(test_docs)
        print(f"   ✅ Test splitting: {len(chunks)} chunks created")
        
    except Exception as e:
        print(f"   ❌ Document splitter failed: {str(e)}")
    
    # Check RAG service
    print("\n🧠 RAG Service Check:")
    try:
        rag_service = RAGService()
        if rag_service.embeddings:
            print("   ✅ RAG service initialized")
            
            # Test embedding generation
            test_text = "Test text for embedding"
            embedding = rag_service.get_embedding(test_text)
            print(f"   ✅ Embedding generated: {len(embedding)} dimensions")
        else:
            print("   ❌ RAG service not properly configured")
    except Exception as e:
        print(f"   ❌ RAG service failed: {str(e)}")
    
    # Check storage bucket
    print("\n📦 Storage Bucket Check:")
    try:
        # Check if api-docs bucket exists
        buckets = supabase.storage.list_buckets()
        bucket_names = []
        
        # Handle different response formats - Supabase returns SyncBucket objects
        if isinstance(buckets, list):
            # Extract names from SyncBucket objects
            bucket_names = [bucket.name for bucket in buckets if hasattr(bucket, 'name')]
        elif hasattr(buckets, 'data'):
            bucket_names = [bucket.get('name', '') for bucket in buckets.data if isinstance(bucket, dict)]
        
        if 'api-docs' in bucket_names:
            print("   ✅ api-docs bucket exists")
            
            # Check if there are any files
            try:
                files = supabase.storage.from_("api-docs").list()
                if isinstance(files, list):
                    file_count = len(files)
                elif hasattr(files, 'data'):
                    file_count = len(files.data)
                else:
                    file_count = 0
                    
                print(f"   Files in bucket: {file_count}")
                
                if file_count > 0:
                    print("   Sample files:")
                    sample_files = files[:3] if isinstance(files, list) else files.data[:3]
                    for file in sample_files:
                        if isinstance(file, dict):
                            print(f"     - {file.get('name', 'unknown')}")
            except Exception as e:
                print(f"   ⚠️ Could not list files: {str(e)}")
        else:
            print("   ❌ api-docs bucket not found")
            print("   Available buckets:", bucket_names)
    except Exception as e:
        print(f"   ❌ Storage check failed: {str(e)}")
    
    # Check embedding worker
    print("\n⚙️ Embedding Worker Check:")
    try:
        worker = EmbeddingWorker()
        print("   ✅ Embedding worker initialized")
        
        # Check if Kafka consumer is connected
        if worker.consumer:
            print("   ✅ Kafka consumer connected")
        else:
            print("   ❌ Kafka consumer not connected")
            
    except Exception as e:
        print(f"   ❌ Embedding worker failed: {str(e)}")
    
    # Summary and recommendations
    print("\n📊 Summary:")
    print(f"   Documents: {doc_count}")
    print(f"   Chunks: {chunk_count}")
    
    if doc_count > 0 and chunk_count == 0:
        print("\n🔍 DIAGNOSIS: Documents exist but no chunks!")
        print("   This indicates the document processing pipeline is not working.")
        print("   Possible causes:")
        print("   1. Embedding worker is not running")
        print("   2. Kafka events are not being sent/received")
        print("   3. Document processing is failing")
        print("   4. Chunk storage is failing")
        
        print("\n🛠️ RECOMMENDATIONS:")
        print("   1. Check if embedding worker is running: docker-compose logs embedding-worker")
        print("   2. Check Kafka logs: docker-compose logs kafka")
        print("   3. Check for processing errors in the logs")
        print("   4. Try uploading a new document and watch the logs")
        
    elif doc_count == 0:
        print("\n🔍 DIAGNOSIS: No documents uploaded!")
        print("   This is expected if no documents have been uploaded yet.")
        print("   Try uploading a document through the frontend or API.")
        
    else:
        print("\n✅ Pipeline appears to be working correctly!")
    
    print("\n✅ Debug complete!")

if __name__ == "__main__":
    debug_document_pipeline() 