-- Storage Bucket Setup for DevDocs AI
-- Run this script in your Supabase SQL Editor after creating the 'api-docs' bucket

-- Enable Row Level Security on storage.objects
ALTER TABLE storage.objects ENABLE ROW LEVEL SECURITY;

-- Policy for users to upload their own files
CREATE POLICY "Users can upload their own files" ON storage.objects
    FOR INSERT WITH CHECK (
        bucket_id = 'api-docs' AND 
        auth.uid()::text = (storage.foldername(name))[1]
    );

-- Policy for users to view their own files
CREATE POLICY "Users can view their own files" ON storage.objects
    FOR SELECT USING (
        bucket_id = 'api-docs' AND 
        auth.uid()::text = (storage.foldername(name))[1]
    );

-- Policy for users to update their own files
CREATE POLICY "Users can update their own files" ON storage.objects
    FOR UPDATE USING (
        bucket_id = 'api-docs' AND 
        auth.uid()::text = (storage.foldername(name))[1]
    );

-- Policy for users to delete their own files
CREATE POLICY "Users can delete their own files" ON storage.objects
    FOR DELETE USING (
        bucket_id = 'api-docs' AND 
        auth.uid()::text = (storage.foldername(name))[1]
    );

-- Success message
SELECT 'Storage bucket policies created successfully!' AS status; 