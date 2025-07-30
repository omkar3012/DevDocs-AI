-- Add missing fields for document processing pipeline
-- This migration adds fields that might be missing from the original schema

-- Add status and error fields to api_documents if they don't exist
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_name = 'api_documents' 
        AND column_name = 'status'
    ) THEN
        ALTER TABLE api_documents ADD COLUMN status TEXT DEFAULT 'uploaded';
    END IF;
    
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_name = 'api_documents' 
        AND column_name = 'error'
    ) THEN
        ALTER TABLE api_documents ADD COLUMN error TEXT;
    END IF;
    
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_name = 'api_documents' 
        AND column_name = 'chunk_count'
    ) THEN
        ALTER TABLE api_documents ADD COLUMN chunk_count INTEGER DEFAULT 0;
    END IF;
    
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_name = 'api_documents' 
        AND column_name = 'processed_at'
    ) THEN
        ALTER TABLE api_documents ADD COLUMN processed_at TIMESTAMP WITH TIME ZONE;
    END IF;
END $$;

-- Add missing fields to api_chunks if they don't exist
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_name = 'api_chunks' 
        AND column_name = 'id'
    ) THEN
        ALTER TABLE api_chunks ADD COLUMN id UUID PRIMARY KEY DEFAULT gen_random_uuid();
    END IF;
    
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_name = 'api_chunks' 
        AND column_name = 'created_at'
    ) THEN
        ALTER TABLE api_chunks ADD COLUMN created_at TIMESTAMP WITH TIME ZONE DEFAULT now();
    END IF;
END $$;

-- Update existing documents to have proper status
UPDATE api_documents 
SET status = 'uploaded' 
WHERE status IS NULL;

-- Create index on status for better querying
CREATE INDEX IF NOT EXISTS idx_api_documents_status ON api_documents(status);

-- Create index on chunk_index for better ordering
CREATE INDEX IF NOT EXISTS idx_api_chunks_index ON api_chunks(chunk_index);

-- Grant necessary permissions
GRANT ALL ON api_documents TO authenticated;
GRANT ALL ON api_chunks TO authenticated;
GRANT ALL ON api_documents TO service_role;
GRANT ALL ON api_chunks TO service_role; 