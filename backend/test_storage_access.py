#!/usr/bin/env python3
"""
Comprehensive Storage Access Test for DevDocs AI
Tests different authentication methods and provides detailed diagnostics
"""

import os
import sys
from dotenv import load_dotenv

# Add the current directory to the path so we can import our modules
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from supabase_client import get_supabase_client, get_supabase_anon_client

def test_storage_access():
    """Test storage access with different authentication methods"""
    print("🔍 Testing Supabase Storage Access")
    print("==================================")
    
    # Load environment variables
    load_dotenv()
    
    # Check environment variables
    print("\n📋 Environment Variables Check:")
    supabase_url = os.getenv("SUPABASE_URL")
    service_key = os.getenv("SUPABASE_SERVICE_ROLE_KEY")
    anon_url = os.getenv("NEXT_PUBLIC_SUPABASE_URL")
    anon_key = os.getenv("NEXT_PUBLIC_SUPABASE_ANON_KEY")
    
    print(f"   Service Role URL: {'✅ Set' if supabase_url else '❌ Not set'}")
    print(f"   Service Role Key: {'✅ Set' if service_key else '❌ Not set'}")
    print(f"   Anonymous URL: {'✅ Set' if anon_url else '❌ Not set'}")
    print(f"   Anonymous Key: {'✅ Set' if anon_key else '❌ Not set'}")
    
    # Test with service role client
    print("\n🔑 Testing with Service Role Client:")
    try:
        service_client = get_supabase_client()
        
        # Test bucket listing
        print("   Testing bucket listing...")
        buckets = service_client.storage.list_buckets()
        
        # Handle different response formats
        bucket_names = []
        if isinstance(buckets, list):
            bucket_names = [bucket.get('name', '') for bucket in buckets if isinstance(bucket, dict)]
        elif hasattr(buckets, 'data'):
            bucket_names = [bucket.get('name', '') for bucket in buckets.data if isinstance(bucket, dict)]
        
        print(f"   Available buckets: {bucket_names}")
        
        if 'api-docs' in bucket_names:
            print("   ✅ api-docs bucket found with service role")
            
            # Test bucket access
            try:
                files = service_client.storage.from_("api-docs").list()
                print("   ✅ Can list files in api-docs bucket")
                
                # Try to upload a test file
                test_content = b"test file content"
                test_path = "test/service-role-test.txt"
                
                try:
                    result = service_client.storage.from_("api-docs").upload(
                        path=test_path,
                        file=test_content,
                        file_options={"content-type": "text/plain"}
                    )
                    print("   ✅ Can upload files with service role")
                    
                    # Clean up
                    service_client.storage.from_("api-docs").remove([test_path])
                    print("   ✅ Can delete files with service role")
                    
                except Exception as e:
                    print(f"   ❌ Upload failed with service role: {str(e)}")
                    
            except Exception as e:
                print(f"   ❌ Cannot list files in api-docs bucket: {str(e)}")
        else:
            print("   ❌ api-docs bucket not found with service role")
            
    except Exception as e:
        print(f"   ❌ Service role client failed: {str(e)}")
    
    # Test with anonymous client
    print("\n👤 Testing with Anonymous Client:")
    try:
        anon_client = get_supabase_anon_client()
        
        # Test bucket listing
        print("   Testing bucket listing...")
        buckets = anon_client.storage.list_buckets()
        
        # Handle different response formats
        bucket_names = []
        if isinstance(buckets, list):
            bucket_names = [bucket.get('name', '') for bucket in buckets if isinstance(bucket, dict)]
        elif hasattr(buckets, 'data'):
            bucket_names = [bucket.get('name', '') for bucket in buckets.data if isinstance(bucket, dict)]
        
        print(f"   Available buckets: {bucket_names}")
        
        if 'api-docs' in bucket_names:
            print("   ✅ api-docs bucket found with anonymous client")
            
            # Test bucket access
            try:
                files = anon_client.storage.from_("api-docs").list()
                print("   ✅ Can list files in api-docs bucket")
            except Exception as e:
                print(f"   ❌ Cannot list files in api-docs bucket: {str(e)}")
        else:
            print("   ❌ api-docs bucket not found with anonymous client")
            
    except Exception as e:
        print(f"   ❌ Anonymous client failed: {str(e)}")
    
    # Test direct API call
    print("\n🌐 Testing Direct API Call:")
    try:
        import requests
        
        # Test bucket listing via direct API
        headers = {
            'Authorization': f'Bearer {service_key}',
            'apikey': service_key
        }
        
        response = requests.get(f"{supabase_url}/storage/v1/bucket", headers=headers)
        
        if response.status_code == 200:
            buckets_data = response.json()
            bucket_names = [bucket.get('name', '') for bucket in buckets_data if isinstance(bucket, dict)]
            print(f"   ✅ Direct API call successful")
            print(f"   Available buckets: {bucket_names}")
            
            if 'api-docs' in bucket_names:
                print("   ✅ api-docs bucket found via direct API")
            else:
                print("   ❌ api-docs bucket not found via direct API")
        else:
            print(f"   ❌ Direct API call failed: {response.status_code}")
            print(f"   Response: {response.text}")
            
    except Exception as e:
        print(f"   ❌ Direct API call failed: {str(e)}")
    
    # Provide recommendations
    print("\n💡 Recommendations:")
    print("===================")
    
    if 'api-docs' not in bucket_names:
        print("1. Create the 'api-docs' bucket in your Supabase dashboard")
        print("   - Go to Storage > Buckets > Create a new bucket")
        print("   - Name: api-docs")
        print("   - Keep it private (uncheck 'Public bucket')")
        print()
        print("2. Set up storage policies:")
        print("   - Go to Storage > Policies")
        print("   - Select the api-docs bucket")
        print("   - Create policies for INSERT, SELECT, DELETE operations")
        print("   - Use 'true' as the policy definition for testing")
    else:
        print("✅ The api-docs bucket exists!")
        print("   If you're still having issues, check the storage policies.")
        print("   Make sure authenticated users can INSERT, SELECT, and DELETE.")
    
    print("\n🔧 Next Steps:")
    print("1. Create the bucket if it doesn't exist")
    print("2. Set up basic storage policies")
    print("3. Run this test again to verify access")
    print("4. Test document upload through the application")

if __name__ == "__main__":
    test_storage_access() 