-- Complete Database Reset for DevDocs AI with Hugging Face Integration
-- WARNING: This will delete all existing data and recreate the database schema
-- Run this script in your Supabase SQL Editor

-- Step 1: Enable pgvector extension
CREATE EXTENSION IF NOT EXISTS vector;

-- Step 2: Drop existing tables (if they exist)
DROP TABLE IF EXISTS query_logs CASCADE;
DROP TABLE IF EXISTS qa_feedback CASCADE;
DROP TABLE IF EXISTS api_chunks CASCADE;
DROP TABLE IF EXISTS api_documents CASCADE;

-- Step 3: Create tables with correct schema
CREATE TABLE api_documents (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name TEXT NOT NULL,
    version TEXT,
    type TEXT NOT NULL CHECK (type IN ('openapi', 'markdown', 'pdf')),
    storage_path TEXT NOT NULL,
    user_id UUID REFERENCES auth.users(id),
    status TEXT DEFAULT 'uploaded',
    error TEXT,
    chunk_count INTEGER DEFAULT 0,
    processed_at TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT now(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT now()
);

CREATE TABLE api_chunks (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    doc_id UUID NOT NULL REFERENCES api_documents(id) ON DELETE CASCADE,
    chunk_text TEXT NOT NULL,
    metadata JSONB DEFAULT '{}',
    embedding VECTOR(1536),  -- Correct dimension for OpenAI
    chunk_index INTEGER,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT now()
);

CREATE TABLE qa_feedback (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    query TEXT NOT NULL,
    answer TEXT NOT NULL,
    was_helpful BOOLEAN,
    notes TEXT,
    user_id UUID REFERENCES auth.users(id),
    doc_id UUID REFERENCES api_documents(id),
    timestamp TIMESTAMP WITH TIME ZONE DEFAULT now()
);

CREATE TABLE query_logs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    query TEXT NOT NULL,
    doc_id UUID REFERENCES api_documents(id),
    user_id UUID REFERENCES auth.users(id),
    response_time_ms INTEGER,
    chunk_count INTEGER,
    timestamp TIMESTAMP WITH TIME ZONE DEFAULT now()
);

-- Step 4: Create the match_documents function for vector search
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

-- Step 5: Create indexes
CREATE INDEX idx_api_documents_user_id ON api_documents(user_id);
CREATE INDEX idx_api_documents_type ON api_documents(type);
CREATE INDEX idx_api_documents_status ON api_documents(status);
CREATE INDEX idx_api_chunks_doc_id ON api_chunks(doc_id);
CREATE INDEX idx_api_chunks_index ON api_chunks(chunk_index);
CREATE INDEX idx_api_chunks_embedding ON api_chunks USING ivfflat (embedding vector_cosine_ops) WITH (lists = 100);
CREATE INDEX idx_qa_feedback_user_id ON qa_feedback(user_id);
CREATE INDEX idx_qa_feedback_doc_id ON qa_feedback(doc_id);
CREATE INDEX idx_query_logs_timestamp ON query_logs(timestamp);

-- Step 6: Create triggers
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = now();
    RETURN NEW;
END;
$$ language 'plpgsql';

CREATE TRIGGER update_api_documents_updated_at 
    BEFORE UPDATE ON api_documents 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Step 7: Enable RLS
ALTER TABLE api_documents ENABLE ROW LEVEL SECURITY;
ALTER TABLE api_chunks ENABLE ROW LEVEL SECURITY;
ALTER TABLE qa_feedback ENABLE ROW LEVEL SECURITY;
ALTER TABLE query_logs ENABLE ROW LEVEL SECURITY;

-- Step 8: Create RLS policies
CREATE POLICY "Users can view their own documents" ON api_documents
    FOR SELECT USING (auth.uid() = user_id);

CREATE POLICY "Users can insert their own documents" ON api_documents
    FOR INSERT WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can update their own documents" ON api_documents
    FOR UPDATE USING (auth.uid() = user_id);

CREATE POLICY "Users can delete their own documents" ON api_documents
    FOR DELETE USING (auth.uid() = user_id);

CREATE POLICY "Users can view chunks of their documents" ON api_chunks
    FOR SELECT USING (
        EXISTS (
            SELECT 1 FROM api_documents 
            WHERE api_documents.id = api_chunks.doc_id 
            AND api_documents.user_id = auth.uid()
        )
    );

CREATE POLICY "Users can view their own feedback" ON qa_feedback
    FOR SELECT USING (auth.uid() = user_id);

CREATE POLICY "Users can insert their own feedback" ON qa_feedback
    FOR INSERT WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can view their own query logs" ON query_logs
    FOR SELECT USING (auth.uid() = user_id);

CREATE POLICY "Users can insert their own query logs" ON query_logs
    FOR INSERT WITH CHECK (auth.uid() = user_id);

-- Step 9: Grant permissions
GRANT EXECUTE ON FUNCTION match_documents TO authenticated;
GRANT EXECUTE ON FUNCTION match_documents TO anon;
GRANT EXECUTE ON FUNCTION match_documents TO service_role;
GRANT ALL ON api_documents TO authenticated;
GRANT ALL ON api_chunks TO authenticated;
GRANT ALL ON qa_feedback TO authenticated;
GRANT ALL ON query_logs TO authenticated;
GRANT ALL ON api_documents TO service_role;
GRANT ALL ON api_chunks TO service_role;
GRANT ALL ON qa_feedback TO service_role;
GRANT ALL ON query_logs TO service_role;

-- Success message
SELECT 'Database reset completed successfully! All tables recreated with correct vector dimensions (384).' AS status; 