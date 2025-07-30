-- Drop the old index with wrong dimensions
DROP INDEX IF EXISTS idx_api_chunks_embedding;

-- Update the embedding column to use 384 dimensions (Hugging Face)
ALTER TABLE api_chunks ALTER COLUMN embedding TYPE VECTOR(384);

-- Create the match_documents function for vector similarity search
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

-- Create new index with correct dimensions
CREATE INDEX idx_api_chunks_embedding ON api_chunks USING ivfflat (embedding vector_cosine_ops) WITH (lists = 100);

-- Grant execute permission on the function
GRANT EXECUTE ON FUNCTION match_documents TO authenticated;
GRANT EXECUTE ON FUNCTION match_documents TO anon; 