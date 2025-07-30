-- Fix vector dimensions migration
-- This migration properly updates the embedding column to use 384 dimensions

-- First, backup existing data (if any)
CREATE TABLE IF NOT EXISTS api_chunks_backup AS 
SELECT * FROM api_chunks;

-- Drop the existing table
DROP TABLE IF EXISTS api_chunks CASCADE;

-- Recreate the table with correct vector dimensions
CREATE TABLE api_chunks (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    doc_id UUID NOT NULL REFERENCES api_documents(id) ON DELETE CASCADE,
    chunk_text TEXT NOT NULL,
    metadata JSONB DEFAULT '{}',
    embedding VECTOR(384),  -- Correct dimension for Hugging Face
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