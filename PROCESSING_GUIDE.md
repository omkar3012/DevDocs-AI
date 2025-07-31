# Document Processing Guide

This guide explains how document processing works in DevDocs AI and how to troubleshoot processing issues.

## 🔄 Processing Flow

### 1. **Upload Phase**
```
User Uploads File → Backend Validates → Stores in Supabase → Triggers Processing
```

### 2. **Processing Phase**
```
Download from Storage → Load Document → Split into Chunks → Create Embeddings → Store in Database
```

### 3. **Status Updates**
```
Processing → Ready (with chunk count) or Failed (with error)
```

## 🚀 How Processing Works

### Immediate Processing (Primary Method)
When a document is uploaded, the backend immediately processes it:

1. **File Validation**: Check file type and size
2. **Storage**: Upload to Supabase Storage
3. **Metadata**: Store document info in database
4. **Processing**: Immediately chunk and embed the document
5. **Status Update**: Mark as "ready" or "failed"

### Kafka Processing (Fallback)
If immediate processing fails, Kafka events can trigger processing:

1. **Event Emission**: Send Kafka event for processing
2. **Worker Processing**: Background worker processes the document
3. **Status Update**: Update document status when complete

### Manual Processing (User Triggered)
Users can manually trigger processing for stuck documents:

1. **Retry Button**: Click "Retry" on processing/failed documents
2. **Manual Processing**: Backend processes the document
3. **Status Update**: Real-time status updates

## 🔧 Processing Components

### Backend Processing (`api.py`)
```python
async def process_document_immediately(doc_id, storage_path, doc_type, user_id, filename):
    # 1. Download from Supabase Storage
    file_content = supabase.storage.from_("api-docs").download(storage_path)
    
    # 2. Load document based on type
    if doc_type == "openapi":
        documents = loader.load_openapi(temp_file_path)
    elif doc_type == "pdf":
        documents = loader.load_pdf(temp_file_path)
    elif doc_type == "markdown":
        documents = loader.load_markdown(temp_file_path)
    
    # 3. Split into chunks
    chunks = splitter.split_documents(documents)
    
    # 4. Create embeddings and store
    for chunk in chunks:
        embedding = rag_service.get_embedding(chunk["text"])
        chunk_data = {
            "doc_id": doc_id,
            "chunk_text": chunk["text"],
            "embedding": embedding,
            "metadata": chunk.get("metadata", {})
        }
        supabase.table("api_chunks").insert(chunk_data)
    
    # 5. Update status
    supabase.table("api_documents").update({"status": "ready"})
```

### Frontend Status Tracking (`DocumentList.tsx`)
```typescript
// Auto-refresh processing documents
useEffect(() => {
  const interval = setInterval(() => {
    const processingDocs = documents.filter(doc => 
      documentStatuses[doc.id]?.status === 'processing'
    );
    
    if (processingDocs.length > 0) {
      checkDocumentStatuses();
    }
  }, 5000);
  
  return () => clearInterval(interval);
}, [documents, documentStatuses]);
```

## 📊 Processing Statuses

### Status Types
- **`processing`**: Document is being chunked and embedded
- **`ready`**: Document is processed and ready for chat
- **`failed`**: Processing failed (check error details)

### Status Indicators
- 🟡 **Processing**: Clock icon with "Processing..." text
- 🟢 **Ready**: Checkmark with chunk count
- 🔴 **Failed**: Alert icon with "Failed" text

## 🔍 Troubleshooting

### Common Issues

#### 1. **Document Stuck in "Processing"**
**Symptoms**: Document shows "Processing..." for more than 2 minutes
**Solutions**:
- Click the "Retry" button next to the document
- Check backend logs for processing errors
- Verify Supabase storage access

#### 2. **Processing Failed**
**Symptoms**: Document shows "Failed" status
**Solutions**:
- Click "Retry" to reprocess
- Check document format and size
- Verify OpenAI API key is valid

#### 3. **No Chunks Created**
**Symptoms**: Document shows "Ready" but 0 chunks
**Solutions**:
- Check if document content is readable
- Verify document type is supported
- Check embedding creation logs

#### 4. **Slow Processing**
**Symptoms**: Processing takes more than 30 seconds
**Solutions**:
- Check file size (should be under 10MB)
- Verify OpenAI API response times
- Check backend resource usage

### Debug Commands

#### Check Document Status
```bash
curl https://your-backend.onrender.com/status/{doc_id}
```

#### Manually Trigger Processing
```bash
curl -X POST https://your-backend.onrender.com/process/{doc_id}
```

#### Check Database
```sql
-- Check document status
SELECT id, name, status, error FROM api_documents WHERE id = 'your-doc-id';

-- Check chunks
SELECT COUNT(*) FROM api_chunks WHERE doc_id = 'your-doc-id';
```

#### Check Storage
```bash
# List files in storage
supabase storage ls api-docs

# Download and check file
supabase storage download api-docs/path/to/file
```

## 🛠️ Manual Processing

### Via Frontend
1. Go to Documents page
2. Find document with "Processing" or "Failed" status
3. Click "Retry" button
4. Wait for status to update

### Via API
```bash
# Trigger processing
curl -X POST https://your-backend.onrender.com/process/{doc_id}

# Check status
curl https://your-backend.onrender.com/status/{doc_id}
```

### Via Database
```sql
-- Reset document status to trigger reprocessing
UPDATE api_documents 
SET status = 'processing', error = NULL 
WHERE id = 'your-doc-id';

-- Delete existing chunks to force reprocessing
DELETE FROM api_chunks WHERE doc_id = 'your-doc-id';
```

## 📋 Processing Checklist

### Before Upload
- [ ] File format is supported (.pdf, .md, .yaml, .json)
- [ ] File size is reasonable (< 10MB)
- [ ] File content is readable

### During Processing
- [ ] Document appears in list with "Processing" status
- [ ] Status updates to "Ready" within 2 minutes
- [ ] Chunk count is greater than 0

### After Processing
- [ ] Document shows "Ready" status
- [ ] Chat interface works with the document
- [ ] Questions return relevant answers

## 🚨 Error Handling

### Backend Errors
- **Storage errors**: Check Supabase storage permissions
- **Database errors**: Check table structure and permissions
- **Embedding errors**: Check OpenAI API key and quota
- **Processing errors**: Check document format and content

### Frontend Errors
- **Status check errors**: Check API endpoint accessibility
- **Processing trigger errors**: Check backend processing endpoint
- **Display errors**: Check component rendering

## 📈 Performance Optimization

### Processing Speed
- **Small files** (< 1MB): Should process in < 30 seconds
- **Medium files** (1-5MB): Should process in < 2 minutes
- **Large files** (5-10MB): May take 2-5 minutes

### Optimization Tips
- Use smaller, focused documents
- Ensure good internet connection
- Monitor OpenAI API usage
- Check backend resource allocation

This processing system ensures that documents are immediately available for chat while providing fallback mechanisms for reliability. 