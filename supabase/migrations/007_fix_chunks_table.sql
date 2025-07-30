-- Fix chunks table structure and ensure proper indexing
-- This migration ensures the api_chunks table exists with correct structure

-- Create api_chunks table if it doesn't exist
CREATE TABLE IF NOT EXISTS api_chunks (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    doc_id UUID NOT NULL REFERENCES api_documents(id) ON DELETE CASCADE,
    chunk_text TEXT NOT NULL,
    metadata JSONB DEFAULT '{}',
    embedding vector(1536),
    chunk_index INTEGER DEFAULT 0,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create indexes for better performance
CREATE INDEX IF NOT EXISTS idx_api_chunks_doc_id ON api_chunks(doc_id);
CREATE INDEX IF NOT EXISTS idx_api_chunks_embedding ON api_chunks USING ivfflat (embedding vector_cosine_ops);

-- Create the match_chunks function if it doesn't exist
CREATE OR REPLACE FUNCTION match_chunks(
    query_embedding vector(1536),
    match_threshold float DEFAULT 0.1,
    match_count int DEFAULT 5,
    doc_id uuid DEFAULT NULL
)
RETURNS TABLE (
    id uuid,
    chunk_text text,
    metadata jsonb,
    similarity float
)
LANGUAGE plpgsql
AS $$
BEGIN
    RETURN QUERY
    SELECT 
        api_chunks.id,
        api_chunks.chunk_text,
        api_chunks.metadata,
        1 - (api_chunks.embedding <=> query_embedding) AS similarity
    FROM api_chunks
    WHERE 
        (doc_id IS NULL OR api_chunks.doc_id = match_chunks.doc_id)
        AND 1 - (api_chunks.embedding <=> query_embedding) > match_threshold
    ORDER BY api_chunks.embedding <=> query_embedding
    LIMIT match_count;
END;
$$;

-- Add status column to api_documents if it doesn't exist
ALTER TABLE api_documents ADD COLUMN IF NOT EXISTS status TEXT DEFAULT 'processing';
ALTER TABLE api_documents ADD COLUMN IF NOT EXISTS error TEXT;

-- Create index on status for faster queries
CREATE INDEX IF NOT EXISTS idx_api_documents_status ON api_documents(status); 