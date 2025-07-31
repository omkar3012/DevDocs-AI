# Manual Migration Guide

This guide helps you apply migrations manually to avoid memory issues on Supabase.

## 🚨 Memory Error Solution

If you get this error:
```
ERROR: 54000: memory required is 62 MB, maintenance_work_mem is 32 MB
```

Follow these steps to apply the migration manually:

## 🔧 Step-by-Step Manual Migration

### Step 1: Apply Lightweight Migration

First, apply the lightweight parts that don't require much memory:

```sql
-- Connect to your Supabase database via SQL Editor or psql

-- 1. Create the function (lightweight)
CREATE OR REPLACE FUNCTION match_documents(
    query_embedding VECTOR(1536),
    match_threshold FLOAT DEFAULT 0.78,
    match_count INT DEFAULT 5,
    filter JSONB DEFAULT '{}'
)
RETURNS TABLE (
    id UUID,
    doc_id UUID,
    chunk_text TEXT,
    metadata JSONB,
    chunk_index INTEGER,
    similarity FLOAT
)
LANGUAGE plpgsql
AS $$
BEGIN
    RETURN QUERY
    SELECT
        api_chunks.id,
        api_chunks.doc_id,
        api_chunks.chunk_text,
        api_chunks.metadata,
        api_chunks.chunk_index,
        1 - (api_chunks.embedding <=> query_embedding) AS similarity
    FROM api_chunks
    WHERE 1 - (api_chunks.embedding <=> query_embedding) > match_threshold
    AND (
        CASE 
            WHEN filter->>'doc_id' IS NOT NULL 
            THEN api_chunks.doc_id = (filter->>'doc_id')::UUID
            ELSE TRUE
        END
    )
    ORDER BY api_chunks.embedding <=> query_embedding
    LIMIT match_count;
END;
$$;

-- 2. Grant permissions
GRANT EXECUTE ON FUNCTION match_documents TO authenticated;
GRANT EXECUTE ON FUNCTION match_documents TO anon;

-- 3. Add status columns (lightweight)
ALTER TABLE api_documents ADD COLUMN IF NOT EXISTS status TEXT DEFAULT 'processing';
ALTER TABLE api_documents ADD COLUMN IF NOT EXISTS error TEXT;

-- 4. Create status index (lightweight)
CREATE INDEX IF NOT EXISTS idx_api_documents_status ON api_documents(status);
```

### Step 2: Check Current Structure

Check what you currently have:

```sql
-- Check if api_chunks table exists
SELECT EXISTS (
    SELECT FROM information_schema.tables 
    WHERE table_name = 'api_chunks'
);

-- Check embedding column type
SELECT column_name, data_type 
FROM information_schema.columns 
WHERE table_name = 'api_chunks' AND column_name = 'embedding';

-- Check existing indexes
SELECT indexname, indexdef 
FROM pg_indexes 
WHERE tablename = 'api_chunks';
```

### Step 3: Fix Vector Structure (if needed)

Only run this if you have no data or are sure about the change:

```sql
-- Only if table is empty or you're sure about the change
ALTER TABLE api_chunks ALTER COLUMN embedding TYPE VECTOR(1536);
```

### Step 4: Create Vector Index (Heavy Operation)

This is the operation that requires more memory. Try these approaches:

#### Option A: Create with Lower Memory Usage
```sql
-- Try with reduced memory usage
CREATE INDEX CONCURRENTLY idx_api_chunks_embedding 
ON api_chunks USING ivfflat (embedding vector_cosine_ops) 
WITH (lists = 25);  -- Very low lists value
```

#### Option B: Create Without Concurrently
```sql
-- Remove CONCURRENTLY to use less memory
CREATE INDEX idx_api_chunks_embedding 
ON api_chunks USING ivfflat (embedding vector_cosine_ops) 
WITH (lists = 50);
```

#### Option C: Skip Index Creation
```sql
-- If you can't create the index, the function will still work
-- but vector searches will be slower
-- You can create the index later when you have more memory
```

## 🚀 Alternative: Use Supabase CLI with Higher Memory

If you have access to Supabase CLI, you can try:

```bash
# Set higher memory for the session
export PGCONNECT_TIMEOUT=60
export PGOPTIONS="-c maintenance_work_mem=128MB"

# Then run the migration
supabase db push
```

## 🔍 Verify the Fix

After applying the migration, test it:

```sql
-- Test the function
SELECT * FROM match_documents(
    ARRAY[0.1, 0.1, 0.1, ...]::vector(1536),  -- 1536 zeros
    0.1,
    5,
    '{}'::jsonb
);
```

## 📋 Migration Checklist

- [ ] Function `match_documents` created successfully
- [ ] Permissions granted
- [ ] Status columns added to `api_documents`
- [ ] Status index created
- [ ] Vector column type is correct (1536 dimensions)
- [ ] Vector index created (optional, for performance)
- [ ] Function test passes

## 🆘 If You Still Have Issues

### For Free Tier Users:
1. **Skip the vector index** - The function will work without it
2. **Use the app without the index** - Searches will be slower but functional
3. **Upgrade to Pro** - Get more memory for heavy operations

### For Pro Users:
1. **Contact Supabase support** - They can increase memory limits
2. **Use a different approach** - Create indexes during off-peak hours
3. **Split the operation** - Create indexes on smaller batches

## 💡 Performance Notes

- **Without vector index**: Searches work but are slower
- **With vector index**: Searches are fast and optimized
- **You can add the index later** when you have more memory or during low-usage periods

The most important part is getting the `match_documents` function working - the index is just for performance optimization. 