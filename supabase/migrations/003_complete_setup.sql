-- Complete setup migration for Hugging Face integration
-- This migration ensures all necessary functions and permissions are in place

-- Ensure pgvector extension is enabled
CREATE EXTENSION IF NOT EXISTS vector;

-- Update embedding column to 384 dimensions if it exists with different dimensions
DO $$
BEGIN
    IF EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_name = 'api_chunks' 
        AND column_name = 'embedding' 
        AND data_type = 'USER-DEFINED'
    ) THEN
        -- Check current dimensions and update if needed
        IF (SELECT COUNT(*) FROM pg_attribute 
            WHERE attrelid = 'api_chunks'::regclass 
            AND attname = 'embedding' 
            AND atttypid = (SELECT oid FROM pg_type WHERE typname = 'vector')) > 0 THEN
            
            -- Try to alter the column type
            BEGIN
                ALTER TABLE api_chunks ALTER COLUMN embedding TYPE VECTOR(384);
            EXCEPTION WHEN OTHERS THEN
                -- If there's data, we need to handle it differently
                RAISE NOTICE 'Column type change failed, may need manual intervention';
            END;
        END IF;
    END IF;
END $$;

-- Create or replace the match_documents function
CREATE OR REPLACE FUNCTION match_documents(
    query_embedding VECTOR(384),
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

-- Drop and recreate the vector index with correct dimensions
DROP INDEX IF EXISTS idx_api_chunks_embedding;
CREATE INDEX idx_api_chunks_embedding ON api_chunks USING ivfflat (embedding vector_cosine_ops) WITH (lists = 100);

-- Ensure proper permissions
GRANT EXECUTE ON FUNCTION match_documents TO authenticated;
GRANT EXECUTE ON FUNCTION match_documents TO anon;
GRANT EXECUTE ON FUNCTION match_documents TO service_role;

-- Create a helper function for similarity search
CREATE OR REPLACE FUNCTION similarity_search(
    query_embedding VECTOR(384),
    doc_id UUID DEFAULT NULL,
    limit_count INT DEFAULT 5
)
RETURNS TABLE (
    chunk_id UUID,
    chunk_text TEXT,
    similarity FLOAT
)
LANGUAGE plpgsql
AS $$
BEGIN
    RETURN QUERY
    SELECT
        api_chunks.id,
        api_chunks.chunk_text,
        1 - (api_chunks.embedding <=> query_embedding) AS similarity
    FROM api_chunks
    WHERE (doc_id IS NULL OR api_chunks.doc_id = doc_id)
    ORDER BY api_chunks.embedding <=> query_embedding
    LIMIT limit_count;
END;
$$;

-- Grant permissions on the helper function
GRANT EXECUTE ON FUNCTION similarity_search TO authenticated;
GRANT EXECUTE ON FUNCTION similarity_search TO anon;
GRANT EXECUTE ON FUNCTION similarity_search TO service_role; 