-- Fix match_documents function to work with current setup
-- This migration ensures the function exists with correct parameters
-- Split into smaller parts to avoid memory issues

-- Drop the old function if it exists with wrong signature
DROP FUNCTION IF EXISTS match_documents(VECTOR(384), FLOAT, INT, JSONB);
DROP FUNCTION IF EXISTS match_chunks(VECTOR(1536), FLOAT, INT, UUID);

-- Create or replace the match_documents function for 1536 dimensions (OpenAI)
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

-- Grant execute permission on the function
GRANT EXECUTE ON FUNCTION match_documents TO authenticated;
GRANT EXECUTE ON FUNCTION match_documents TO anon;

-- Add status column to api_documents if it doesn't exist
ALTER TABLE api_documents ADD COLUMN IF NOT EXISTS status TEXT DEFAULT 'processing';
ALTER TABLE api_documents ADD COLUMN IF NOT EXISTS error TEXT;

-- Create index on status for faster queries (lightweight operation)
CREATE INDEX IF NOT EXISTS idx_api_documents_status ON api_documents(status); 