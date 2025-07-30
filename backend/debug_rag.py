#!/usr/bin/env python3
"""
Debug script for RAG service
Helps diagnose issues with document processing and vector search
"""

import os
import sys
from dotenv import load_dotenv

# Add the current directory to the path so we can import our modules
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from rag_service import RAGService
from supabase_client import get_supabase_client

def debug_rag_system():
    """Debug the RAG system"""
    print("🔍 Debugging RAG System...")
    
    # Load environment variables
    load_dotenv()
    
    # Check environment variables
    print("\n📋 Environment Check:")
    openai_api_key = os.getenv("OPENAI_API_KEY")
    supabase_url = os.getenv("SUPABASE_URL")
    supabase_key = os.getenv("SUPABASE_SERVICE_ROLE_KEY")
    
    print(f"   OpenAI API Key: {'✅ Set' if openai_api_key and openai_api_key != 'your_openai_api_key_here' else '❌ Not set'}")
    print(f"   Supabase URL: {'✅ Set' if supabase_url else '❌ Not set'}")
    print(f"   Supabase Key: {'✅ Set' if supabase_key else '❌ Not set'}")
    
    # Initialize RAG service
    print("\n🔧 Initializing RAG Service...")
    rag_service = RAGService()
    
    if not rag_service.embeddings:
        print("❌ RAG service not properly configured")
        return
    
    print("✅ RAG service initialized")
    
    # Test embeddings
    print("\n🧠 Testing Embeddings...")
    test_text = "How is AI being used for coaching?"
    embedding = rag_service.get_embedding(test_text)
    print(f"   Embedding dimension: {len(embedding)}")
    print(f"   Embedding sample: {embedding[:5]}...")
    
    # Check database connection
    print("\n🗄️ Checking Database...")
    try:
        supabase = get_supabase_client()
        
        # Check if tables exist
        result = supabase.table("api_documents").select("count", count="exact").execute()
        doc_count = result.count if result.count is not None else 0
        print(f"   Documents in database: {doc_count}")
        
        result = supabase.table("api_chunks").select("count", count="exact").execute()
        chunk_count = result.count if result.count is not None else 0
        print(f"   Chunks in database: {chunk_count}")
        
        # Get sample documents
        if doc_count > 0:
            docs = supabase.table("api_documents").select("*").limit(3).execute()
            print(f"   Sample documents:")
            for doc in docs.data:
                print(f"     - {doc['name']} (ID: {doc['id']})")
        
        # Get sample chunks
        if chunk_count > 0:
            chunks = supabase.table("api_chunks").select("*").limit(3).execute()
            print(f"   Sample chunks:")
            for chunk in chunks.data:
                print(f"     - Chunk {chunk['chunk_index']} (ID: {chunk['id']})")
                print(f"       Text: {chunk['chunk_text'][:100]}...")
                print(f"       Has embedding: {'✅' if chunk['embedding'] else '❌'}")
        
    except Exception as e:
        print(f"❌ Database connection failed: {str(e)}")
        return
    
    # Test vector search if we have documents
    if doc_count > 0 and chunk_count > 0:
        print("\n🔍 Testing Vector Search...")
        
        # Get first document
        docs = supabase.table("api_documents").select("*").limit(1).execute()
        if docs.data:
            doc_id = docs.data[0]['id']
            doc_name = docs.data[0]['name']
            
            print(f"   Testing with document: {doc_name} (ID: {doc_id})")
            
            # Test search
            chunks = rag_service.search_similar_chunks(test_text, doc_id, limit=3)
            print(f"   Found {len(chunks)} similar chunks")
            
            for i, chunk in enumerate(chunks):
                print(f"     Chunk {i+1}:")
                print(f"       Similarity: {chunk['similarity_score']:.3f}")
                print(f"       Content: {chunk['content'][:100]}...")
            
            # Test full answer generation
            print(f"\n🤖 Testing Answer Generation...")
            answer, sources, chunk_count = await rag_service.get_answer(test_text, doc_id)
            print(f"   Answer: {answer}")
            print(f"   Sources: {len(sources)}")
            print(f"   Chunks used: {chunk_count}")
    
    print("\n✅ Debug complete!")

if __name__ == "__main__":
    import asyncio
    asyncio.run(debug_rag_system()) 