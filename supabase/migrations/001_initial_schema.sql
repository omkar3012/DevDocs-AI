-- Enable pgvector extension for embeddings
CREATE EXTENSION IF NOT EXISTS vector;

-- Create api_documents table for storing document metadata
CREATE TABLE api_documents (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name TEXT NOT NULL,
    version TEXT,
    type TEXT NOT NULL CHECK (type IN ('openapi', 'markdown', 'pdf')),
    storage_path TEXT NOT NULL,
    user_id UUID REFERENCES auth.users(id),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT now(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT now()
);

-- Create api_chunks table for storing document chunks with embeddings
CREATE TABLE api_chunks (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    doc_id UUID NOT NULL REFERENCES api_documents(id) ON DELETE CASCADE,
    chunk_text TEXT NOT NULL,
    metadata JSONB DEFAULT '{}',
    embedding VECTOR(384),
    chunk_index INTEGER,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT now()
);

-- Create qa_feedback table for storing user feedback
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

-- Create query_logs table for analytics
CREATE TABLE query_logs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    query TEXT NOT NULL,
    doc_id UUID REFERENCES api_documents(id),
    user_id UUID REFERENCES auth.users(id),
    response_time_ms INTEGER,
    chunk_count INTEGER,
    timestamp TIMESTAMP WITH TIME ZONE DEFAULT now()
);

-- Create indexes for better performance
CREATE INDEX idx_api_documents_user_id ON api_documents(user_id);
CREATE INDEX idx_api_documents_type ON api_documents(type);
CREATE INDEX idx_api_chunks_doc_id ON api_chunks(doc_id);
CREATE INDEX idx_api_chunks_embedding ON api_chunks USING ivfflat (embedding vector_cosine_ops) WITH (lists = 100);
CREATE INDEX idx_qa_feedback_user_id ON qa_feedback(user_id);
CREATE INDEX idx_qa_feedback_doc_id ON qa_feedback(doc_id);
CREATE INDEX idx_query_logs_timestamp ON query_logs(timestamp);

-- Create updated_at trigger function
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = now();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Create trigger for api_documents
CREATE TRIGGER update_api_documents_updated_at 
    BEFORE UPDATE ON api_documents 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Enable Row Level Security (RLS)
ALTER TABLE api_documents ENABLE ROW LEVEL SECURITY;
ALTER TABLE api_chunks ENABLE ROW LEVEL SECURITY;
ALTER TABLE qa_feedback ENABLE ROW LEVEL SECURITY;
ALTER TABLE query_logs ENABLE ROW LEVEL SECURITY;

-- Create RLS policies
CREATE POLICY "Users can view their own documents" ON api_documents
    FOR SELECT USING (auth.uid() = user_id);

CREATE POLICY "Users can insert their own documents" ON api_documents
    FOR INSERT WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can update their own documents" ON api_documents
    FOR UPDATE USING (auth.uid() = user_id);

CREATE POLICY "Users can delete their own documents" ON api_documents
    FOR DELETE USING (auth.uid() = user_id);

-- Chunks are readable by document owners
CREATE POLICY "Users can view chunks of their documents" ON api_chunks
    FOR SELECT USING (
        EXISTS (
            SELECT 1 FROM api_documents 
            WHERE api_documents.id = api_chunks.doc_id 
            AND api_documents.user_id = auth.uid()
        )
    );

-- Feedback policies
CREATE POLICY "Users can view their own feedback" ON qa_feedback
    FOR SELECT USING (auth.uid() = user_id);

CREATE POLICY "Users can insert their own feedback" ON qa_feedback
    FOR INSERT WITH CHECK (auth.uid() = user_id);

-- Query logs policies
CREATE POLICY "Users can view their own query logs" ON query_logs
    FOR SELECT USING (auth.uid() = user_id);

CREATE POLICY "Users can insert their own query logs" ON query_logs
    FOR INSERT WITH CHECK (auth.uid() = user_id); 