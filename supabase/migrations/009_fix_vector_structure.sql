-- Fix vector structure and indexes (heavy operations)
-- This migration should be run separately to avoid memory issues
-- Run this after the main migration is successful

-- Ensure the api_chunks table has the correct structure
-- Only run this if the table exists and has data
DO $$
BEGIN
    -- Check if table exists and has the wrong embedding type
    IF EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_name = 'api_chunks' 
        AND column_name = 'embedding' 
        AND data_type != 'USER-DEFINED'
    ) THEN
        -- Only alter if there's no data or if we're sure about the change
        IF NOT EXISTS (SELECT 1 FROM api_chunks LIMIT 1) THEN
            ALTER TABLE api_chunks ALTER COLUMN embedding TYPE VECTOR(1536);
            RAISE NOTICE 'Changed embedding column to VECTOR(1536)';
        ELSE
            RAISE NOTICE 'Table has data, skipping embedding type change. Run manually if needed.';
        END IF;
    END IF;
END $$;

-- Create vector index only if it doesn't exist
-- This is the heavy operation that requires more memory
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM pg_indexes 
        WHERE indexname = 'idx_api_chunks_embedding'
    ) THEN
        -- Create the index with minimal memory usage
        CREATE INDEX CONCURRENTLY idx_api_chunks_embedding 
        ON api_chunks USING ivfflat (embedding vector_cosine_ops) 
        WITH (lists = 50);  -- Reduced lists for lower memory usage
        RAISE NOTICE 'Created vector index successfully';
    ELSE
        RAISE NOTICE 'Vector index already exists';
    END IF;
EXCEPTION
    WHEN OTHERS THEN
        RAISE NOTICE 'Failed to create vector index: %', SQLERRM;
        RAISE NOTICE 'You may need to run this manually with higher memory settings';
END $$; 