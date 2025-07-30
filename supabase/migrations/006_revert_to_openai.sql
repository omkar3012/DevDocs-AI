-- Revert to OpenAI migration
-- This migration updates the embedding column to use 1536 dimensions for OpenAI

-- First, backup existing data (if any)
CREATE TABLE IF NOT EXISTS api_chunks_backup AS 
SELECT * FROM api_chunks;

-- Drop the existing table
DROP TABLE IF EXISTS api_chunks CASCADE;

-- Recreate the table with correct vector dimensions for OpenAI
CREATE TABLE api_chunks (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    doc_id UUID NOT NULL REFERENCES api_documents(id) ON DELETE CASCADE,
    chunk_text TEXT NOT NULL,
    metadata JSONB DEFAULT '{}',
    embedding VECTOR(1536),  -- Correct dimension for OpenAI
    chunk_index INTEGER,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT now()
);

-- Create indexes
CREATE INDEX idx_api_chunks_doc_id ON api_chunks(doc_id);
CREATE INDEX idx_api_chunks_index ON api_chunks(chunk_index);
CREATE INDEX idx_api_chunks_embedding ON api_chunks USING ivfflat (embedding vector_cosine_ops) WITH (lists = 100);

-- Enable RLS
ALTER TABLE api_chunks ENABLE ROW LEVEL SECURITY;

-- Create RLS policy
CREATE POLICY "Users can view chunks of their documents" ON api_chunks
    FOR SELECT USING (
        EXISTS (
            SELECT 1 FROM api_documents 
            WHERE api_documents.id = api_chunks.doc_id 
            AND api_documents.user_id = auth.uid()
        )
    );

-- Grant permissions
GRANT ALL ON api_chunks TO authenticated;
GRANT ALL ON api_chunks TO service_role;

-- Drop the backup table (since we're starting fresh)
DROP TABLE IF EXISTS api_chunks_backup;

-- Update all documents to have 'uploaded' status so they can be reprocessed
UPDATE api_documents 
SET status = 'uploaded', 
    chunk_count = 0, 
    error = NULL 
WHERE status IN ('processed', 'failed');

-- Create or replace the match_documents function for 1536 dimensions
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