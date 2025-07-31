# Database Function Fix Guide

This guide helps you fix the `match_chunks` function error that's preventing document processing and chat functionality.

## 🚨 Error Description

The error you're seeing:
```
Could not find the function public.match_chunks(doc_id, match_count, match_threshold, query_embedding) in the schema cache
```

This happens because:
1. The code is trying to call `match_chunks` function
2. But the database has `match_documents` function instead
3. The function parameters don't match

## 🔧 Fix Steps

### Step 1: Apply the Database Migration

Run the new migration to ensure the correct function exists:

```bash
# Option A: Apply the specific migration
supabase db push

# Option B: Reset the database (if you don't have important data)
supabase db reset

# Option C: Run the migration manually
psql -h your-supabase-host -U postgres -d postgres -f supabase/migrations/008_fix_match_function.sql
```

### Step 2: Verify the Fix

Run the test script to verify everything works:

```bash
cd backend
python test_database_function.py
```

Expected output:
```
🧪 Testing Database Function and Structure
==================================================
🔍 Testing api_chunks table structure...
✅ api_chunks table exists!
📊 Table has X rows
📋 Table columns: ['id', 'doc_id', 'chunk_text', 'embedding', ...]
🔢 Embedding dimension: 1536
✅ Embedding dimension is correct (1536)

🔍 Testing if match_documents function exists...
✅ match_documents function exists and works!
📊 Result: X chunks found

==================================================
📋 Test Results:
   Table Structure: ✅ PASS
   Function: ✅ PASS

🎉 All tests passed! Database is ready.
```

### Step 3: Test the Application

1. **Upload a document** and verify it processes correctly
2. **Try chatting** with the document to ensure RAG works
3. **Check the logs** for any remaining errors

## 🔍 What Was Fixed

### 1. Function Name Mismatch
- **Before**: Code called `match_chunks`
- **After**: Code calls `match_documents`

### 2. Function Parameters
- **Before**: `doc_id` parameter
- **After**: `filter` parameter with `{"doc_id": doc_id}`

### 3. Vector Dimensions
- **Before**: Mixed 384 and 1536 dimensions
- **After**: Consistent 1536 dimensions (OpenAI)

### 4. Database Structure
- **Before**: Inconsistent table structure
- **After**: Proper `api_chunks` table with correct columns

## 📋 Files Modified

### Backend Files
- `backend/rag_service.py` - Fixed function calls
- `backend/api.py` - Fixed search endpoint
- `backend/test_database_function.py` - Added test script

### Database Files
- `supabase/migrations/008_fix_match_function.sql` - New migration

## 🚀 Quick Fix Commands

If you want to fix this quickly:

```bash
# 1. Apply the migration
supabase db push

# 2. Test the fix
cd backend && python test_database_function.py

# 3. Restart your backend
# (if running locally or redeploy if on Render)

# 4. Test upload and chat
```

## 🔍 Troubleshooting

### If Migration Fails

```bash
# Check current database status
supabase db diff

# Reset database (WARNING: loses data)
supabase db reset

# Apply all migrations
supabase db push
```

### If Function Still Doesn't Work

```bash
# Check what functions exist
psql -h your-supabase-host -U postgres -d postgres -c "\df match*"

# Manually create the function
psql -h your-supabase-host -U postgres -d postgres -f supabase/migrations/008_fix_match_function.sql
```

### If Embedding Dimensions Are Wrong

```bash
# Check current dimensions
psql -h your-supabase-host -U postgres -d postgres -c "SELECT column_name, data_type FROM information_schema.columns WHERE table_name = 'api_chunks' AND column_name = 'embedding';"

# Fix dimensions
psql -h your-supabase-host -U postgres -d postgres -c "ALTER TABLE api_chunks ALTER COLUMN embedding TYPE VECTOR(1536);"
```

## 📊 Expected Database Structure

After the fix, your database should have:

### Tables
- `api_documents` - Document metadata
- `api_chunks` - Document chunks with embeddings

### Functions
- `match_documents(query_embedding, match_threshold, match_count, filter)` - Vector similarity search

### Columns in api_chunks
- `id` (UUID)
- `doc_id` (UUID) - References api_documents
- `chunk_text` (TEXT)
- `metadata` (JSONB)
- `embedding` (VECTOR(1536)) - OpenAI embeddings
- `chunk_index` (INTEGER)
- `created_at` (TIMESTAMP)

## ✅ Verification Checklist

- [ ] Migration applied successfully
- [ ] `match_documents` function exists
- [ ] `api_chunks` table has correct structure
- [ ] Embedding dimension is 1536
- [ ] Test script passes
- [ ] Document upload works
- [ ] Document processing works
- [ ] Chat functionality works
- [ ] No more function errors in logs

## 🆘 Still Having Issues?

If you're still seeing errors after following this guide:

1. **Check the logs** for the exact error message
2. **Run the test script** to see what's failing
3. **Verify your Supabase connection** and credentials
4. **Check if the migration was applied** correctly
5. **Contact support** with the specific error details

The most common issues are:
- Migration not applied
- Wrong Supabase credentials
- Network connectivity issues
- Database permissions problems 