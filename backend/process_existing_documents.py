#!/usr/bin/env python3
"""
Manual document processing script
Processes existing documents that haven't been chunked yet
"""

import os
import sys
import tempfile
from dotenv import load_dotenv

# Add the current directory to the path so we can import our modules
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from supabase_client import get_supabase_client
from utils.loaders import DocumentLoader
from utils.splitters import DocumentSplitter
from langchain_openai import OpenAIEmbeddings

def process_existing_documents():
    """Process all documents that haven't been chunked yet"""
    print("🔄 Processing existing documents...")
    
    # Load environment variables
    load_dotenv()
    
    # Initialize services
    supabase = get_supabase_client()
    loader = DocumentLoader()
    splitter = DocumentSplitter()
    
    # Initialize embeddings directly
    openai_api_key = os.getenv("OPENAI_API_KEY")
    if not openai_api_key or openai_api_key == "your_openai_api_key_here":
        print("❌ OpenAI API key not configured")
        return
    
    try:
        embeddings = OpenAIEmbeddings()
        print("✅ Embeddings initialized")
    except Exception as e:
        print(f"❌ Failed to initialize embeddings: {str(e)}")
        return
    
    # Get all documents that haven't been processed
    result = supabase.table("api_documents").select("*").eq("status", "uploaded").execute()
    
    if not result.data:
        print("✅ No documents need processing")
        return
    
    print(f"📄 Found {len(result.data)} documents to process")
    
    for doc in result.data:
        try:
            print(f"\n🔄 Processing: {doc['name']} (ID: {doc['id']})")
            
            # Download file from storage
            file_content = supabase.storage.from_("api-docs").download(doc['storage_path'])
            
            # Save to temporary file
            with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(doc['name'])[1]) as temp_file:
                temp_file.write(file_content)
                temp_file_path = temp_file.name
            
            try:
                # Load document based on type
                if doc['type'] == "openapi":
                    documents = loader.load_openapi(temp_file_path)
                elif doc['type'] == "pdf":
                    documents = loader.load_pdf(temp_file_path)
                elif doc['type'] == "markdown":
                    documents = loader.load_markdown(temp_file_path)
                else:
                    raise ValueError(f"Unsupported document type: {doc['type']}")
                
                print(f"   📖 Loaded {len(documents)} document sections")
                
                # Split documents into chunks
                chunks = splitter.split_documents(documents)
                print(f"   ✂️ Split into {len(chunks)} chunks")
                
                # Store chunks with embeddings
                chunk_count = 0
                failed_chunks = 0
                
                for i, chunk in enumerate(chunks):
                    try:
                        # Get embedding for chunk text
                        embedding = embeddings.embed_query(chunk["text"])
                        
                        # Verify embedding dimensions
                        if len(embedding) != 384:
                            print(f"   ⚠️ Chunk {i} has wrong embedding dimension: {len(embedding)} (expected 384)")
                            failed_chunks += 1
                            continue
                        
                        # Prepare chunk data
                        chunk_data = {
                            "doc_id": doc['id'],
                            "chunk_text": chunk["text"],
                            "metadata": chunk.get("metadata", {}),
                            "embedding": embedding,
                            "chunk_index": i
                        }
                        
                        # Insert into database
                        result = supabase.table("api_chunks").insert(chunk_data).execute()
                        
                        if result.data:
                            chunk_count += 1
                            if chunk_count % 50 == 0:  # Progress indicator
                                print(f"   📊 Processed {chunk_count}/{len(chunks)} chunks...")
                        else:
                            print(f"   ⚠️ Failed to store chunk {i}: {result}")
                            failed_chunks += 1
                            
                    except Exception as e:
                        print(f"   ⚠️ Error processing chunk {i}: {str(e)}")
                        failed_chunks += 1
                        continue
                
                # Update document status
                if chunk_count > 0:
                    status = "processed"
                    error_msg = None
                else:
                    status = "failed"
                    error_msg = f"Failed to process any chunks. {failed_chunks} chunks failed."
                
                supabase.table("api_documents").update({
                    "status": status,
                    "chunk_count": chunk_count,
                    "error": error_msg
                }).eq("id", doc['id']).execute()
                
                print(f"   ✅ Successfully processed {chunk_count} chunks")
                if failed_chunks > 0:
                    print(f"   ⚠️ {failed_chunks} chunks failed")
                
            finally:
                # Clean up temporary file
                os.unlink(temp_file_path)
                
        except Exception as e:
            print(f"   ❌ Error processing document {doc['id']}: {str(e)}")
            
            # Update document status to failed
            supabase.table("api_documents").update({
                "status": "failed",
                "error": str(e)
            }).eq("id", doc['id']).execute()
    
    print("\n✅ Document processing complete!")

if __name__ == "__main__":
    process_existing_documents() 