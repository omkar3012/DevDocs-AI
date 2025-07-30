# Storage Integration Guide

This guide explains how DevDocs AI integrates Supabase Storage with the backend processing pipeline while maintaining proper separation of concerns.

## 🏗️ Architecture Overview

```
┌─────────────────┐    Upload File    ┌─────────────────┐
│   Frontend      │ ──────────────► │    Backend      │
│   (Vercel)      │                 │   (Render)      │
│                 │                 │                 │
│ - File Upload   │                 │ - Store in      │
│ - Document List │                 │   Supabase      │
│ - Status Check  │                 │ - Emit Kafka    │
└─────────────────┘                 └─────────────────┘
         │                                   │
         │                                   ▼
         │                          ┌─────────────────┐
         │                          │   Supabase      │
         │                          │   Storage       │
         │                          └─────────────────┘
         │                                   │
         ▼                                   ▼
┌─────────────────┐                 ┌─────────────────┐
│   Supabase      │                 │   Kafka         │
│   Database      │                 │   Event         │
│   - Metadata    │                 └─────────────────┘
│   - Status      │                           │
└─────────────────┘                           ▼
                                              │
                                    ┌─────────────────┐
                                    │   Worker        │
                                    │   (Processing)  │
                                    │                 │
                                    │ - Download File │
                                    │ - Chunk Text    │
                                    │ - Create Embed  │
                                    │ - Store Chunks  │
                                    └─────────────────┘
```

## 🔄 Complete Flow

### 1. File Upload Process

**Frontend (DocumentUpload.tsx)**:
```typescript
// User selects file
const formData = new FormData();
formData.append('file', file);
formData.append('user_id', userId);

// Send to backend
const result = await api.uploadDocument(formData);
```

**Backend (api.py)**:
```python
# 1. Validate file type
# 2. Generate unique ID
# 3. Upload to Supabase Storage
supabase.storage.from_("api-docs").upload(
    path=storage_path,
    file=file_content
)

# 4. Store metadata in database
document_data = {
    "id": doc_id,
    "name": file.filename,
    "type": doc_type,
    "storage_path": storage_path,
    "user_id": user_id,
    "status": "processing"
}
supabase.table("api_documents").insert(document_data)

# 5. Emit Kafka event
kafka_event = {
    "doc_id": doc_id,
    "storage_path": storage_path,
    "doc_type": doc_type
}
kafka_producer.send_message("api-doc-upload", kafka_event)
```

### 2. Document Processing (Worker)

**Embedding Worker (embedding_worker.py)**:
```python
# 1. Listen to Kafka events
# 2. Download file from Supabase Storage
file_content = supabase.storage.from_("api-docs").download(storage_path)

# 3. Process document (chunk, embed)
chunks = splitter.split_documents(documents)

# 4. Store chunks with embeddings
for chunk in chunks:
    embedding = rag_service.get_embedding(chunk["text"])
    chunk_data = {
        "doc_id": doc_id,
        "chunk_text": chunk["text"],
        "embedding": embedding
    }
    supabase.table("api_chunks").insert(chunk_data)

# 5. Update document status
supabase.table("api_documents").update(
    {"status": "ready"}
).eq("id", doc_id)
```

### 3. Document Management (Frontend)

**Document Listing (Dashboard.tsx)**:
```typescript
// Fetch documents from Supabase database
const { data, error } = await supabase
  .from('api_documents')
  .select('*')
  .eq('user_id', user.id)
  .order('created_at', { ascending: false });
```

**Status Checking (DocumentList.tsx)**:
```typescript
// Check processing status from backend
const status = await api.checkDocumentStatus(doc.id);
// Returns: { status: 'ready'|'processing'|'failed', chunk_count: number }
```

**Document Deletion (DocumentList.tsx)**:
```typescript
// 1. Delete from database
await supabase.from('api_documents').delete().eq('id', docId);

// 2. Delete from storage
await supabase.storage.from('api-docs').remove([storage_path]);

// 3. Delete chunks
await supabase.from('api_chunks').delete().eq('doc_id', docId);
```

## 🗄️ Database Schema

### api_documents Table
```sql
CREATE TABLE api_documents (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name TEXT NOT NULL,
    type TEXT NOT NULL,
    storage_path TEXT NOT NULL,
    user_id UUID NOT NULL,
    status TEXT DEFAULT 'processing',
    error TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
```

### api_chunks Table
```sql
CREATE TABLE api_chunks (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    doc_id UUID NOT NULL REFERENCES api_documents(id) ON DELETE CASCADE,
    chunk_text TEXT NOT NULL,
    metadata JSONB DEFAULT '{}',
    embedding vector(1536),
    chunk_index INTEGER DEFAULT 0,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
```

## 🔧 Key Integration Points

### 1. Frontend-Backend Communication
- **Upload**: Frontend → Backend (file + metadata)
- **Status**: Frontend → Backend (check processing status)
- **Chat**: Frontend → Backend (RAG queries)

### 2. Frontend-Supabase Communication
- **Document List**: Frontend → Supabase (fetch metadata)
- **Document Delete**: Frontend → Supabase (delete metadata + storage)

### 3. Backend-Supabase Communication
- **File Storage**: Backend → Supabase Storage
- **Metadata Storage**: Backend → Supabase Database
- **Chunk Storage**: Worker → Supabase Database

### 4. Worker-Supabase Communication
- **File Download**: Worker → Supabase Storage
- **Chunk Storage**: Worker → Supabase Database
- **Status Update**: Worker → Supabase Database

## 🚀 Benefits of This Architecture

### 1. **Separation of Concerns**
- Frontend handles UI and user interactions
- Backend handles file processing and API calls
- Worker handles heavy processing tasks
- Supabase handles storage and database

### 2. **Scalability**
- Frontend and backend can scale independently
- Worker can be scaled based on processing load
- Supabase handles storage scaling automatically

### 3. **Reliability**
- File storage is handled by Supabase (reliable)
- Processing is asynchronous (non-blocking)
- Status tracking ensures transparency

### 4. **Security**
- Files are stored securely in Supabase Storage
- Database access is controlled by RLS policies
- API keys are managed securely

## 🔍 Troubleshooting

### Common Issues

1. **CORS Errors**
   - Ensure `FRONTEND_URL` is set in backend environment
   - Check that Vercel domain is in CORS allowlist

2. **File Upload Failures**
   - Verify Supabase storage bucket exists
   - Check storage permissions
   - Ensure file size limits are appropriate

3. **Processing Failures**
   - Check Kafka connection
   - Verify worker is running
   - Check document status in database

4. **Chunk Storage Issues**
   - Ensure `api_chunks` table exists
   - Verify vector extension is enabled
   - Check embedding dimensions match

### Debug Commands

```bash
# Check document status
curl https://your-backend.onrender.com/status/{doc_id}

# Check Supabase storage
supabase storage ls api-docs

# Check database tables
supabase db diff

# Check Kafka events
kafka-console-consumer --bootstrap-server localhost:9092 --topic api-doc-upload
```

## 📋 Migration Checklist

- [ ] Run database migrations
- [ ] Create Supabase storage bucket
- [ ] Set up Kafka (if using)
- [ ] Configure environment variables
- [ ] Test file upload flow
- [ ] Test document processing
- [ ] Test chat functionality
- [ ] Test document deletion

This architecture ensures that your DevDocs AI application properly integrates Supabase storage while maintaining clean separation between frontend, backend, and processing components. 