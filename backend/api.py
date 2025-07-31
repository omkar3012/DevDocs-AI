"""
Main FastAPI application for DevDocs AI
Handles file uploads, RAG-based Q&A, and feedback collection
"""

import os
import time
import uuid
import json
from typing import List, Optional
from datetime import datetime

from fastapi import FastAPI, HTTPException, Depends, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field
import httpx

from supabase_client import get_supabase_client
from rag_service import get_rag_service
from kafka_producer import KafkaProducer
from utils.loaders import DocumentLoader
from utils.splitters import DocumentSplitter
import tempfile

app = FastAPI(title="DevDocs AI API", version="1.0.0")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000", 
        "http://frontend:3000",
        "https://dev-docs-d6x8kasmn-omkar-ranes-projects.vercel.app",
        os.getenv("FRONTEND_URL", "https://dev-docs-d6x8kasmn-omkar-ranes-projects.vercel.app")
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize services
supabase = get_supabase_client()
kafka_producer = KafkaProducer()
loader = DocumentLoader()
splitter = DocumentSplitter()

# Pydantic models
class AskRequest(BaseModel):
    question: str = Field(..., min_length=1, description="The question to ask about the document")
    doc_id: str = Field(..., description="The document ID to search in")
    user_id: Optional[str] = Field(None, description="The user ID making the request")

class FeedbackRequest(BaseModel):
    query: str
    answer: str
    was_helpful: bool
    notes: Optional[str] = None
    doc_id: Optional[str] = None
    user_id: Optional[str] = None

class DocumentResponse(BaseModel):
    id: str
    name: str
    version: Optional[str]
    type: str
    created_at: datetime

async def process_document_immediately(doc_id: str, storage_path: str, doc_type: str, user_id: str, filename: str):
    """Process a document immediately: load, chunk, embed, and store"""
    try:
        print(f"🔄 Processing document immediately: {filename} (ID: {doc_id})")
        
        # Download file from Supabase Storage
        file_content = supabase.storage.from_("api-docs").download(storage_path)
        
        # Save to temporary file
        with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(filename)[1]) as temp_file:
            temp_file.write(file_content)
            temp_file_path = temp_file.name
        
        try:
            # Load document based on type
            if doc_type == "openapi":
                documents = loader.load_openapi(temp_file_path)
            elif doc_type == "pdf":
                documents = loader.load_pdf(temp_file_path)
            elif doc_type == "markdown":
                documents = loader.load_markdown(temp_file_path)
            else:
                raise ValueError(f"Unsupported document type: {doc_type}")
            
            # Split documents into chunks
            chunks = splitter.split_documents(documents)
            
            # Create embeddings and store in database
            rag_service = get_rag_service()
            
            for i, chunk in enumerate(chunks):
                # Get embedding for chunk text
                embedding = rag_service.get_embedding(chunk["text"])
                
                # Prepare chunk data
                chunk_data = {
                    "doc_id": doc_id,
                    "chunk_text": chunk["text"],
                    "metadata": chunk.get("metadata", {}),
                    "embedding": embedding,
                    "chunk_index": i
                }
                
                # Insert into database
                result = supabase.table("api_chunks").insert(chunk_data).execute()
                
                if not result.data:
                    print(f"⚠️  Failed to store chunk {i} for document {doc_id}")
            
            # Update document status to ready
            supabase.table("api_documents").update(
                {"status": "ready"}
            ).eq("id", doc_id).execute()
            
            print(f"✅ Successfully processed {len(chunks)} chunks for document {doc_id}")
            
        finally:
            # Clean up temporary file
            os.unlink(temp_file_path)
            
    except Exception as e:
        print(f"❌ Error processing document {doc_id}: {str(e)}")
        # Update document status to failed
        supabase.table("api_documents").update(
            {"status": "failed", "error": str(e)}
        ).eq("id", doc_id).execute()
        raise

@app.get("/")
async def root():
    """Health check endpoint"""
    return {"message": "DevDocs AI API is running", "version": "1.0.0"}

@app.post("/upload")
async def upload_document(
    file: UploadFile = File(...),
    user_id: str = Form(...),
    version: Optional[str] = Form(None)
):
    """
    Upload a document (OpenAPI spec, PDF, or Markdown)
    Stores file in Supabase Storage and emits Kafka event for processing
    """
    try:
        # Validate file type
        allowed_types = ['.yaml', '.yml', '.json', '.pdf', '.md', '.markdown']
        file_extension = os.path.splitext(file.filename)[1].lower()
        
        if file_extension not in allowed_types:
            raise HTTPException(
                status_code=400, 
                detail=f"File type {file_extension} not supported. Allowed: {allowed_types}"
            )

        # Determine document type
        doc_type_map = {
            '.yaml': 'openapi', '.yml': 'openapi', '.json': 'openapi',
            '.pdf': 'pdf', '.md': 'markdown', '.markdown': 'markdown'
        }
        doc_type = doc_type_map[file_extension]

        # Generate unique ID and storage path
        doc_id = str(uuid.uuid4())
        storage_path = f"documents/{user_id}/{doc_id}/{file.filename}"

        # Upload file to Supabase Storage
        file_content = await file.read()
        supabase.storage.from_("api-docs").upload(
            path=storage_path,
            file=file_content,
            file_options={"content-type": file.content_type}
        )

        # Store document metadata in database
        document_data = {
            "id": doc_id,
            "name": file.filename,
            "version": version,
            "type": doc_type,
            "storage_path": storage_path,
            "user_id": user_id
        }
        
        result = supabase.table("api_documents").insert(document_data).execute()
        
        if not result.data:
            raise HTTPException(status_code=500, detail="Failed to store document metadata")

        # Try to emit Kafka event for processing (if available)
        try:
            kafka_event = {
                "doc_id": doc_id,
                "storage_path": storage_path,
                "doc_type": doc_type,
                "user_id": user_id,
                "filename": file.filename
            }
            
            kafka_producer.send_message("api-doc-upload", kafka_event)
            print(f"✅ Kafka event sent for document {doc_id}")
        except Exception as e:
            print(f"⚠️  Kafka event failed: {str(e)}")
            # Continue without Kafka - we'll process immediately

        # Process document immediately if Kafka is not available
        try:
            await process_document_immediately(doc_id, storage_path, doc_type, user_id, file.filename)
            print(f"✅ Document processed immediately: {doc_id}")
        except Exception as e:
            print(f"❌ Immediate processing failed: {str(e)}")
            import traceback
            traceback.print_exc()
            # Update document status to failed
            supabase.table("api_documents").update(
                {"status": "failed", "error": str(e)}
            ).eq("id", doc_id).execute()
            print(f"📝 Document {doc_id} marked as failed due to processing error")

        return {
            "message": "Document uploaded successfully",
            "doc_id": doc_id,
            "status": "processing"
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Upload failed: {str(e)}")

@app.get("/documents/{user_id}")
async def get_documents(user_id: str):
    """Get all documents for a user"""
    try:
        result = supabase.table("api_documents").select("*").eq("user_id", user_id).execute()
        return {"documents": result.data}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch documents: {str(e)}")

@app.post("/ask")
async def ask_question(request: AskRequest):
    """
    Ask a question about a specific document using RAG
    Returns streaming response with answer and sources
    """
    try:
        start_time = time.time()
        
        # Validate query
        if not request.question.strip():
            raise HTTPException(status_code=400, detail="Empty query not allowed")
        
        print(f"🔍 Processing query: '{request.question}' for document: {request.doc_id}")
        
        # Get document info
        doc_result = supabase.table("api_documents").select("*").eq("id", request.doc_id).execute()
        if not doc_result.data:
            raise HTTPException(status_code=404, detail="Document not found")
        
        document = doc_result.data[0]
        
        # Get answer using RAG service
        rag_service = get_rag_service()
        answer, sources, chunk_count = await rag_service.get_answer(
            question=request.question,
            doc_id=request.doc_id,
            user_id=request.user_id
        )
        
        response_time = int((time.time() - start_time) * 1000)
        
        print(f"✅ Query processed successfully. Found {chunk_count} chunks, response time: {response_time}ms")
        
        # Log query for analytics
        log_data = {
            "query": request.question,
            "doc_id": request.doc_id,
            "user_id": request.user_id,
            "response_time_ms": response_time,
            "chunk_count": chunk_count
        }
        
        supabase.table("query_logs").insert(log_data).execute()
        
        return {
            "answer": answer,
            "sources": sources,
            "document": document,
            "response_time_ms": response_time,
            "chunk_count": chunk_count
        }

    except Exception as e:
        print(f"❌ Error processing query: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get answer: {str(e)}")

@app.post("/ask/stream")
async def ask_question_stream(request: AskRequest):
    """
    Stream the answer for better UX
    """
    try:
        async def generate_response():
            start_time = time.time()
            
            # Get document info
            doc_result = supabase.table("api_documents").select("*").eq("id", request.doc_id).execute()
            if not doc_result.data:
                yield f"data: {json.dumps({'error': 'Document not found'})}\n\n"
                return
            
            document = doc_result.data[0]
            
            # Stream answer using RAG service
            rag_service = get_rag_service()
            async for chunk in rag_service.get_answer_stream(
                question=request.question,
                doc_id=request.doc_id,
                user_id=request.user_id
            ):
                yield f"data: {json.dumps(chunk)}\n\n"
            
            # Send final metadata
            response_time = int((time.time() - start_time) * 1000)
            yield f"data: {json.dumps({'metadata': {'response_time_ms': response_time}})}\n\n"
            
            # Log query
            log_data = {
                "query": request.question,
                "doc_id": request.doc_id,
                "user_id": request.user_id,
                "response_time_ms": response_time
            }
            supabase.table("query_logs").insert(log_data).execute()

        return StreamingResponse(
            generate_response(),
            media_type="text/plain",
            headers={"Cache-Control": "no-cache", "Connection": "keep-alive"}
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Streaming failed: {str(e)}")

@app.post("/feedback")
async def submit_feedback(request: FeedbackRequest):
    """Submit feedback for a Q&A interaction"""
    try:
        feedback_data = {
            "query": request.query,
            "answer": request.answer,
            "was_helpful": request.was_helpful,
            "notes": request.notes,
            "doc_id": request.doc_id,
            "user_id": request.user_id
        }
        
        result = supabase.table("qa_feedback").insert(feedback_data).execute()
        
        if not result.data:
            raise HTTPException(status_code=500, detail="Failed to store feedback")
        
        return {"message": "Feedback submitted successfully"}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to submit feedback: {str(e)}")

@app.get("/search/{doc_id}")
async def search_chunks(doc_id: str, query: str, limit: int = 10):
    """Search for relevant chunks in a document"""
    try:
        # Get chunks using vector similarity search
        result = supabase.rpc(
            "match_documents",
            {
                "query_embedding": get_rag_service().get_embedding(query),
                "match_count": limit,
                "filter": {"doc_id": doc_id}
            }
        ).execute()
        
        return {"chunks": result.data}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Search failed: {str(e)}")

@app.get("/status/{doc_id}")
async def get_document_status(doc_id: str):
    """Get document processing status and chunk count"""
    try:
        # Get document info
        doc_result = supabase.table("api_documents").select("*").eq("id", doc_id).execute()
        if not doc_result.data:
            raise HTTPException(status_code=404, detail="Document not found")
        
        document = doc_result.data[0]
        
        # Get chunk count
        chunks_result = supabase.table("api_chunks").select("id").eq("doc_id", doc_id).execute()
        chunk_count = len(chunks_result.data)
        
        # Determine status
        # Priority: Check chunk count first (most reliable indicator)
        if chunk_count > 0:
            status = "ready"
        elif document.get("status") == "failed":
            status = "failed"
        else:
            status = "processing"
        
        return {
            "doc_id": doc_id,
            "status": status,
            "chunk_count": chunk_count,
            "document": document
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Status check failed: {str(e)}")

@app.post("/process/{doc_id}")
async def process_document_manually(doc_id: str):
    """Manually trigger document processing"""
    try:
        # Get document info
        doc_result = supabase.table("api_documents").select("*").eq("id", doc_id).execute()
        if not doc_result.data:
            raise HTTPException(status_code=404, detail="Document not found")
        
        document = doc_result.data[0]
        
        # Check if already processed
        chunks_result = supabase.table("api_chunks").select("id").eq("doc_id", doc_id).execute()
        if len(chunks_result.data) > 0:
            return {"message": "Document already processed", "doc_id": doc_id, "status": "ready"}
        
        # Process the document
        await process_document_immediately(
            doc_id=doc_id,
            storage_path=document["storage_path"],
            doc_type=document["type"],
            user_id=document["user_id"],
            filename=document["name"]
        )
        
        return {"message": "Document processed successfully", "doc_id": doc_id, "status": "ready"}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Processing failed: {str(e)}")

@app.post("/debug/process-all/{user_id}")
async def debug_process_all_documents(user_id: str):
    """Debug endpoint: Force process all documents for a user that have no chunks"""
    try:
        # Get all documents for the user
        docs_result = supabase.table("api_documents").select("*").eq("user_id", user_id).execute()
        documents = docs_result.data
        
        processed_count = 0
        failed_count = 0
        results = []
        
        for doc in documents:
            doc_id = doc['id']
            doc_name = doc['name']
            
            # Check if document has chunks
            chunks_result = supabase.table("api_chunks").select("id").eq("doc_id", doc_id).execute()
            chunk_count = len(chunks_result.data)
            
            if chunk_count == 0:  # No chunks, needs processing
                try:
                    print(f"🔄 Force processing document: {doc_name} (ID: {doc_id})")
                    await process_document_immediately(
                        doc_id=doc_id,
                        storage_path=doc["storage_path"],
                        doc_type=doc["type"],
                        user_id=doc["user_id"],
                        filename=doc["name"]
                    )
                    processed_count += 1
                    results.append({
                        "doc_id": doc_id,
                        "name": doc_name,
                        "status": "processed"
                    })
                    print(f"✅ Successfully processed: {doc_name}")
                except Exception as e:
                    failed_count += 1
                    results.append({
                        "doc_id": doc_id,
                        "name": doc_name,
                        "status": "failed",
                        "error": str(e)
                    })
                    print(f"❌ Failed to process {doc_name}: {str(e)}")
            else:
                results.append({
                    "doc_id": doc_id,
                    "name": doc_name,
                    "status": "already_processed",
                    "chunk_count": chunk_count
                })
        
        return {
            "message": f"Processing complete: {processed_count} processed, {failed_count} failed",
            "total_documents": len(documents),
            "processed": processed_count,
            "failed": failed_count,
            "results": results
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Debug processing failed: {str(e)}")

@app.get("/analytics/{user_id}")
async def get_analytics(user_id: str):
    """Get analytics for a user's documents and queries"""
    try:
        # Get document count
        docs_result = supabase.table("api_documents").select("id").eq("user_id", user_id).execute()
        doc_count = len(docs_result.data)
        
        # Get query count
        queries_result = supabase.table("query_logs").select("id").eq("user_id", user_id).execute()
        query_count = len(queries_result.data)
        
        # Get average response time
        avg_time_result = supabase.rpc(
            "get_avg_response_time",
            {"user_id_param": user_id}
        ).execute()
        
        avg_response_time = avg_time_result.data[0]["avg_time"] if avg_time_result.data else 0
        
        return {
            "document_count": doc_count,
            "query_count": query_count,
            "avg_response_time_ms": avg_response_time
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Analytics failed: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 