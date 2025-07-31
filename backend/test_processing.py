#!/usr/bin/env python3
"""
Test script to debug document processing issues
"""

import os
import sys
from dotenv import load_dotenv

# Add the current directory to the path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from supabase_client import get_supabase_client

load_dotenv()

def test_documents_processing():
    """Test if documents are being processed properly"""
    try:
        supabase = get_supabase_client()
        
        print("🔍 Checking documents and their processing status...")
        
        # Get all documents
        docs_result = supabase.table("api_documents").select("*").execute()
        documents = docs_result.data
        
        print(f"📊 Found {len(documents)} documents")
        
        for doc in documents:
            doc_id = doc['id']
            doc_name = doc['name']
            doc_status = doc.get('status', 'unknown')
            
            # Check chunks for this document
            chunks_result = supabase.table("api_chunks").select("id").eq("doc_id", doc_id).execute()
            chunk_count = len(chunks_result.data)
            
            print(f"\n📄 Document: {doc_name}")
            print(f"   ID: {doc_id}")
            print(f"   Status: {doc_status}")
            print(f"   Chunks: {chunk_count}")
            print(f"   Storage Path: {doc.get('storage_path', 'N/A')}")
            print(f"   Type: {doc.get('type', 'N/A')}")
            
            if chunk_count == 0 and doc_status != 'failed':
                print(f"   ⚠️  This document has no chunks but isn't marked as failed!")
                
                # Try to manually process one document to see what fails
                if doc == documents[0]:  # Test the first document
                    print(f"\n🔧 Testing manual processing for: {doc_name}")
                    test_manual_processing(doc)
        
        return True
        
    except Exception as e:
        print(f"❌ Error checking documents: {str(e)}")
        return False

def test_manual_processing(document):
    """Test manual processing of a document to see what fails"""
    try:
        from utils.loaders import DocumentLoader
        from utils.splitters import DocumentSplitter
        from rag_service import get_rag_service
        import tempfile
        
        supabase = get_supabase_client()
        loader = DocumentLoader()
        splitter = DocumentSplitter()
        
        doc_id = document['id']
        storage_path = document['storage_path']
        doc_type = document['type']
        filename = document['name']
        
        print(f"🔄 Step 1: Downloading file from storage...")
        try:
            file_content = supabase.storage.from_("api-docs").download(storage_path)
            print(f"✅ Downloaded {len(file_content)} bytes")
        except Exception as e:
            print(f"❌ Download failed: {str(e)}")
            return
        
        print(f"🔄 Step 2: Creating temporary file...")
        try:
            with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(filename)[1]) as temp_file:
                temp_file.write(file_content)
                temp_file_path = temp_file.name
            print(f"✅ Temporary file created: {temp_file_path}")
        except Exception as e:
            print(f"❌ Temp file creation failed: {str(e)}")
            return
        
        print(f"🔄 Step 3: Loading document...")
        try:
            if doc_type == "openapi":
                documents = loader.load_openapi(temp_file_path)
            elif doc_type == "pdf":
                documents = loader.load_pdf(temp_file_path)
            elif doc_type == "markdown":
                documents = loader.load_markdown(temp_file_path)
            else:
                raise ValueError(f"Unsupported document type: {doc_type}")
            
            print(f"✅ Loaded {len(documents)} document sections")
        except Exception as e:
            print(f"❌ Document loading failed: {str(e)}")
            os.unlink(temp_file_path)
            return
        
        print(f"🔄 Step 4: Splitting into chunks...")
        try:
            chunks = splitter.split_documents(documents)
            print(f"✅ Created {len(chunks)} chunks")
        except Exception as e:
            print(f"❌ Document splitting failed: {str(e)}")
            os.unlink(temp_file_path)
            return
        
        print(f"🔄 Step 5: Testing embedding creation...")
        try:
            rag_service = get_rag_service()
            if len(chunks) > 0:
                test_embedding = rag_service.get_embedding(chunks[0]["text"][:100])  # Test with first 100 chars
                print(f"✅ Created test embedding with {len(test_embedding)} dimensions")
            else:
                print("⚠️  No chunks to test embedding with")
        except Exception as e:
            print(f"❌ Embedding creation failed: {str(e)}")
            os.unlink(temp_file_path)
            return
        
        print(f"🔄 Step 6: Testing database insertion...")
        try:
            if len(chunks) > 0:
                # Test inserting one chunk
                embedding = rag_service.get_embedding(chunks[0]["text"])
                chunk_data = {
                    "doc_id": doc_id,
                    "chunk_text": chunks[0]["text"],
                    "metadata": chunks[0].get("metadata", {}),
                    "embedding": embedding,
                    "chunk_index": 0
                }
                
                result = supabase.table("api_chunks").insert(chunk_data).execute()
                if result.data:
                    print(f"✅ Successfully inserted test chunk")
                    # Clean up the test chunk
                    supabase.table("api_chunks").delete().eq("id", result.data[0]["id"]).execute()
                else:
                    print(f"❌ Failed to insert test chunk")
        except Exception as e:
            print(f"❌ Database insertion failed: {str(e)}")
        
        # Clean up
        os.unlink(temp_file_path)
        print(f"✅ Cleanup completed")
        
    except Exception as e:
        print(f"❌ Manual processing test failed: {str(e)}")

def main():
    """Main test function"""
    print("🧪 Testing Document Processing")
    print("=" * 50)
    
    test_documents_processing()

if __name__ == "__main__":
    main()