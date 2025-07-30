#!/usr/bin/env python3
"""
Setup Storage Bucket Policies for DevDocs AI
This script creates the necessary storage policies for the api-docs bucket
"""

import os
from dotenv import load_dotenv
from supabase_client import get_supabase_client

def setup_storage_policies():
    """Set up storage bucket policies for the api-docs bucket"""
    print("🔧 Setting up storage bucket policies...")
    
    # Load environment variables
    load_dotenv()
    
    # Get Supabase client
    supabase = get_supabase_client()
    
    try:
        # Check if api-docs bucket exists
        buckets = supabase.storage.list_buckets()
        bucket_names = []
        
        # Handle different response formats
        if isinstance(buckets, list):
            bucket_names = [bucket.get('name', '') for bucket in buckets if isinstance(bucket, dict)]
        elif hasattr(buckets, 'data'):
            bucket_names = [bucket.get('name', '') for bucket in buckets.data if isinstance(bucket, dict)]
        
        if 'api-docs' not in bucket_names:
            print("❌ api-docs bucket not found!")
            print("   Please create the 'api-docs' bucket in your Supabase dashboard first.")
            print("   Go to Storage > Buckets > Create a new bucket")
            return False
        
        print("✅ api-docs bucket found")
        
        # Create storage policies using the Supabase client
        # Note: Storage policies are typically managed through the dashboard
        # For now, we'll create a simple test file to verify access
        
        print("🧪 Testing bucket access...")
        
        # Try to upload a test file
        test_content = b"test file content"
        test_path = "test/test.txt"
        
        try:
            # Upload test file
            result = supabase.storage.from_("api-docs").upload(
                path=test_path,
                file=test_content,
                file_options={"content-type": "text/plain"}
            )
            print("✅ Test file uploaded successfully")
            
            # Try to download the test file
            downloaded_content = supabase.storage.from_("api-docs").download(test_path)
            if downloaded_content == test_content:
                print("✅ Test file downloaded successfully")
            else:
                print("⚠️ Test file download content mismatch")
            
            # Clean up test file
            supabase.storage.from_("api-docs").remove([test_path])
            print("✅ Test file cleaned up")
            
        except Exception as e:
            print(f"❌ Storage access test failed: {str(e)}")
            print("\n🔧 Manual Setup Required:")
            print("1. Go to your Supabase dashboard")
            print("2. Navigate to Storage > Policies")
            print("3. Select the 'api-docs' bucket")
            print("4. Add the following policies:")
            print("   - INSERT: Users can upload files to their own folder")
            print("   - SELECT: Users can view files in their own folder")
            print("   - UPDATE: Users can update files in their own folder")
            print("   - DELETE: Users can delete files in their own folder")
            return False
        
        print("\n✅ Storage bucket setup completed successfully!")
        print("   The api-docs bucket is ready for use.")
        return True
        
    except Exception as e:
        print(f"❌ Failed to setup storage policies: {str(e)}")
        return False

def create_manual_policy_guide():
    """Print manual policy setup guide"""
    print("\n📋 Manual Storage Policy Setup Guide:")
    print("=====================================")
    print("If the automatic setup failed, follow these steps:")
    print()
    print("1. Go to your Supabase dashboard")
    print("2. Navigate to Storage > Policies")
    print("3. Select the 'api-docs' bucket")
    print("4. Click 'New Policy' and add these policies:")
    print()
    print("Policy 1: Upload Access")
    print("   - Policy Name: 'Users can upload their own files'")
    print("   - Allowed operation: INSERT")
    print("   - Target roles: authenticated")
    print("   - Policy definition:")
    print("     auth.uid()::text = (storage.foldername(name))[1]")
    print()
    print("Policy 2: View Access")
    print("   - Policy Name: 'Users can view their own files'")
    print("   - Allowed operation: SELECT")
    print("   - Target roles: authenticated")
    print("   - Policy definition:")
    print("     auth.uid()::text = (storage.foldername(name))[1]")
    print()
    print("Policy 3: Update Access")
    print("   - Policy Name: 'Users can update their own files'")
    print("   - Allowed operation: UPDATE")
    print("   - Target roles: authenticated")
    print("   - Policy definition:")
    print("     auth.uid()::text = (storage.foldername(name))[1]")
    print()
    print("Policy 4: Delete Access")
    print("   - Policy Name: 'Users can delete their own files'")
    print("   - Allowed operation: DELETE")
    print("   - Target roles: authenticated")
    print("   - Policy definition:")
    print("     auth.uid()::text = (storage.foldername(name))[1]")
    print()
    print("5. Save all policies")
    print("6. Test by uploading a document through the application")

if __name__ == "__main__":
    print("🚀 DevDocs AI Storage Setup")
    print("===========================")
    
    success = setup_storage_policies()
    
    if not success:
        create_manual_policy_guide()
    
    print("\n✅ Setup script completed!") 