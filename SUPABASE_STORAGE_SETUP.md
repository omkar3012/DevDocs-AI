# Supabase Storage Setup Guide

This guide explains how to set up Supabase storage for DevDocs AI to handle file uploads directly from the frontend.

## 🚀 Storage Architecture

```
┌─────────────────┐    Direct Upload    ┌─────────────────┐
│   Frontend      │ ──────────────────► │   Supabase      │
│   (Vercel)      │                     │   Storage       │
│                 │                     │                 │
│ - File Upload   │                     │ - api-docs      │
│ - Metadata DB   │                     │   bucket        │
│ - User Auth     │                     │ - File storage  │
└─────────────────┘                     └─────────────────┘
         │                                       │
         │                                       │
         ▼                                       ▼
┌─────────────────┐                     ┌─────────────────┐
│   Supabase      │                     │   Backend       │
│   Database      │                     │   (Render)      │
│                 │                     │                 │
│ - api_documents │                     │ - RAG Pipeline  │
│ - query_logs    │                     │ - Processing    │
│ - embeddings    │                     │ - Analytics     │
└─────────────────┘                     └─────────────────┘
```

## 📋 Prerequisites

- ✅ Supabase project created
- ✅ Database migrations run
- ✅ Vector extension enabled

## 🔧 Step 1: Create Storage Bucket

### 1.1 Via Supabase Dashboard

1. Go to your Supabase project dashboard
2. Navigate to **Storage** in the left sidebar
3. Click **Create a new bucket**
4. Configure the bucket:
   - **Name**: `api-docs`
   - **Public bucket**: ✅ Checked (for file access)
   - **File size limit**: 50MB (or your preferred limit)
   - **Allowed MIME types**: 
     - `application/json`
     - `application/x-yaml`
     - `application/yml`
     - `application/pdf`
     - `text/markdown`
     - `text/plain`

### 1.2 Via SQL (Alternative)

```sql
-- Create the storage bucket
INSERT INTO storage.buckets (id, name, public, file_size_limit, allowed_mime_types)
VALUES (
  'api-docs',
  'api-docs',
  true,
  52428800, -- 50MB in bytes
  ARRAY[
    'application/json',
    'application/x-yaml',
    'application/yml',
    'application/pdf',
    'text/markdown',
    'text/plain'
  ]
);
```

## 🔧 Step 2: Configure Storage Policies

### 2.1 Create Storage Policies

Run these SQL commands in your Supabase SQL editor:

```sql
-- Policy for users to upload their own files
CREATE POLICY "Users can upload their own files" ON storage.objects
FOR INSERT WITH CHECK (
  bucket_id = 'api-docs' AND
  auth.uid()::text = (storage.foldername(name))[1]
);

-- Policy for users to view their own files
CREATE POLICY "Users can view their own files" ON storage.objects
FOR SELECT USING (
  bucket_id = 'api-docs' AND
  auth.uid()::text = (storage.foldername(name))[1]
);

-- Policy for users to update their own files
CREATE POLICY "Users can update their own files" ON storage.objects
FOR UPDATE USING (
  bucket_id = 'api-docs' AND
  auth.uid()::text = (storage.foldername(name))[1]
);

-- Policy for users to delete their own files
CREATE POLICY "Users can delete their own files" ON storage.objects
FOR DELETE USING (
  bucket_id = 'api-docs' AND
  auth.uid()::text = (storage.foldername(name))[1]
);
```

### 2.2 Explanation of Policies

- **File Structure**: Files are stored as `documents/{user_id}/{doc_id}.{extension}`
- **User Isolation**: Each user can only access files in their own folder
- **Security**: Users cannot access other users' files
- **Flexibility**: Users can upload, view, update, and delete their own files

## 🔧 Step 3: Test Storage Setup

### 3.1 Test Upload via Dashboard

1. Go to **Storage** → **api-docs** bucket
2. Click **Upload file**
3. Upload a test file
4. Verify the file appears in the bucket

### 3.2 Test via Frontend

1. Deploy your frontend with the updated code
2. Try uploading a document
3. Check the browser console for any errors
4. Verify the file appears in Supabase storage

## 🔧 Step 4: Environment Variables

### Frontend (.env.local)

```bash
# Supabase Configuration
NEXT_PUBLIC_SUPABASE_URL=https://your-project.supabase.co
NEXT_PUBLIC_SUPABASE_ANON_KEY=your_anon_key

# Backend API URL (for RAG processing)
NEXT_PUBLIC_API_URL=https://your-backend.onrender.com
```

### Backend (.env)

```bash
# Supabase Configuration
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_SERVICE_ROLE_KEY=your_service_role_key

# OpenAI Configuration
OPENAI_API_KEY=your_openai_api_key

# Frontend URL (for CORS)
FRONTEND_URL=https://dev-docs-ai.vercel.app
```

## 🔧 Step 5: File Processing Flow

### 5.1 Upload Process

1. **Frontend**: User selects file
2. **Frontend**: File uploaded directly to Supabase storage
3. **Frontend**: Document metadata stored in database
4. **Backend**: Receives processing event (optional)
5. **Backend**: Downloads file from storage for processing
6. **Backend**: Processes file and stores embeddings

### 5.2 File Access

```typescript
// Get file URL for display/download
const fileUrl = storage.getFileUrl(filePath);

// Download file for processing
const { data, error } = await supabase.storage
  .from('api-docs')
  .download(filePath);
```

## 🔧 Step 6: Security Considerations

### 6.1 File Validation

- **File Types**: Only allow specific MIME types
- **File Size**: Limit file size to prevent abuse
- **File Content**: Validate file content before processing

### 6.2 Access Control

- **User Isolation**: Users can only access their own files
- **Authentication**: Require authentication for all operations
- **Authorization**: Check user permissions before operations

### 6.3 Data Protection

- **Encryption**: Files are encrypted at rest
- **Backup**: Regular backups of storage and database
- **Audit**: Log all file operations for security

## 🔧 Step 7: Troubleshooting

### Common Issues

#### 1. Upload Failures
**Symptoms**: Files fail to upload
**Solutions**:
- Check storage bucket exists and is public
- Verify storage policies are correct
- Check file size and type restrictions
- Ensure user is authenticated

#### 2. Access Denied Errors
**Symptoms**: "Access denied" when trying to access files
**Solutions**:
- Verify storage policies are applied
- Check user authentication
- Ensure file path matches user ID
- Check bucket permissions

#### 3. File Not Found
**Symptoms**: Files don't appear after upload
**Solutions**:
- Check file path structure
- Verify upload was successful
- Check storage bucket configuration
- Review error logs

### Debug Commands

```sql
-- Check storage bucket configuration
SELECT * FROM storage.buckets WHERE id = 'api-docs';

-- Check storage policies
SELECT * FROM storage.policies WHERE bucket_id = 'api-docs';

-- List files in bucket
SELECT * FROM storage.objects WHERE bucket_id = 'api-docs';
```

## 📊 Verification Checklist

- [ ] Storage bucket `api-docs` created
- [ ] Storage policies configured
- [ ] File uploads working from frontend
- [ ] Files accessible via Supabase dashboard
- [ ] User isolation working correctly
- [ ] File deletion working
- [ ] No CORS errors in browser console
- [ ] Environment variables set correctly

## 🎯 Benefits of Direct Storage

1. **Performance**: Faster uploads (no backend proxy)
2. **Scalability**: Supabase handles storage scaling
3. **Security**: Built-in access control and encryption
4. **Cost**: No additional storage costs
5. **Simplicity**: Fewer moving parts in the architecture

Your Supabase storage should now be properly configured for direct file uploads from the frontend! 🎉 