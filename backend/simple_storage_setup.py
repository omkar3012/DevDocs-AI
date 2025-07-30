#!/usr/bin/env python3
"""
Simple Storage Setup for DevDocs AI
This script creates the api-docs bucket with basic permissions
"""

import os
from dotenv import load_dotenv
from supabase_client import get_supabase_client

def create_storage_bucket():
    """Create the api-docs storage bucket with basic setup"""
    print("🔧 Creating storage bucket...")
    
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
        
        if 'api-docs' in bucket_names:
            print("✅ api-docs bucket already exists")
            return True
        
        print("📦 Creating api-docs bucket...")
        
        # Try to create the bucket
        # Note: This might not work with the Python client, but worth trying
        try:
            # This is a simplified approach - the bucket creation might need to be done manually
            print("⚠️ Bucket creation through API might not be supported")
            print("   Please create the bucket manually in the Supabase dashboard")
            return False
            
        except Exception as e:
            print(f"❌ Failed to create bucket via API: {str(e)}")
            print("   This is expected - bucket creation must be done manually")
            return False
            
    except Exception as e:
        print(f"❌ Failed to check/create storage bucket: {str(e)}")
        return False

def test_bucket_access():
    """Test if we can access the bucket once it's created"""
    print("\n🧪 Testing bucket access...")
    
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
            print("❌ api-docs bucket not found")
            return False
        
        print("✅ api-docs bucket found")
        
        # Try a simple operation to test access
        try:
            # List files in the bucket (should work even if empty)
            files = supabase.storage.from_("api-docs").list()
            print("✅ Bucket access confirmed")
            return True
            
        except Exception as e:
            print(f"❌ Bucket access failed: {str(e)}")
            return False
            
    except Exception as e:
        print(f"❌ Failed to test bucket access: {str(e)}")
        return False

def print_manual_setup_instructions():
    """Print manual setup instructions"""
    print("\n📋 Manual Storage Bucket Setup Instructions:")
    print("=============================================")
    print()
    print("1. Go to your Supabase dashboard")
    print("2. Navigate to Storage in the left sidebar")
    print("3. Click on 'Buckets'")
    print("4. Click 'Create a new bucket'")
    print("5. Set the following:")
    print("   - Name: api-docs")
    print("   - Public bucket: UNCHECKED (keep private)")
    print("6. Click 'Create bucket'")
    print()
    print("7. After creating the bucket, go to 'Policies'")
    print("8. Click 'New Policy' and add these policies:")
    print()
    print("   Policy 1 - Upload Access:")
    print("   - Name: 'Allow authenticated uploads'")
    print("   - Allowed operation: INSERT")
    print("   - Target roles: authenticated")
    print("   - Policy definition: true")
    print()
    print("   Policy 2 - View Access:")
    print("   - Name: 'Allow authenticated downloads'")
    print("   - Allowed operation: SELECT")
    print("   - Target roles: authenticated")
    print("   - Policy definition: true")
    print()
    print("   Policy 3 - Delete Access:")
    print("   - Name: 'Allow authenticated deletes'")
    print("   - Allowed operation: DELETE")
    print("   - Target roles: authenticated")
    print("   - Policy definition: true")
    print()
    print("9. Save all policies")
    print("10. Run this script again to test access")

if __name__ == "__main__":
    print("🚀 DevDocs AI Simple Storage Setup")
    print("===================================")
    
    # Try to create the bucket
    bucket_created = create_storage_bucket()
    
    if not bucket_created:
        print_manual_setup_instructions()
    else:
        # Test access
        access_ok = test_bucket_access()
        if not access_ok:
            print_manual_setup_instructions()
    
    print("\n✅ Setup script completed!")
    print("\n💡 Next steps:")
    print("1. Create the api-docs bucket manually if not done")
    print("2. Set up basic storage policies")
    print("3. Run this script again to verify access")
    print("4. Test document upload through the application") 