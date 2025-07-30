"""
Supabase client configuration for DevDocs AI
Handles database connections and storage operations
"""

import os
from supabase import create_client, Client
from dotenv import load_dotenv

load_dotenv()

def get_supabase_client() -> Client:
    """Get configured Supabase client"""
    supabase_url = os.getenv("SUPABASE_URL")
    supabase_key = os.getenv("SUPABASE_SERVICE_ROLE_KEY")
    
    # Check if we have placeholder values
    if (not supabase_url or not supabase_key or 
        supabase_url == "your_supabase_url_here" or 
        supabase_key == "your_supabase_service_role_key_here"):
        print("⚠️  Warning: Supabase not configured. Using mock client for development.")
        return create_mock_supabase_client()
    
    try:
        return create_client(supabase_url, supabase_key)
    except Exception as e:
        print(f"⚠️  Warning: Failed to create Supabase client: {str(e)}. Using mock client for development.")
        return create_mock_supabase_client()

def create_mock_supabase_client() -> Client:
    """Create a mock Supabase client for development when Supabase is not configured"""
    # Create a minimal mock client that won't crash the application
    class MockSupabaseClient:
        def __init__(self):
            self.storage = MockStorage()
            self.table = lambda name: MockTable()
        
        def __getattr__(self, name):
            # Return a no-op function for any method calls
            return lambda *args, **kwargs: None
    
    class MockStorage:
        def from_(self, bucket):
            return MockBucket()
    
    class MockBucket:
        def upload(self, path, file, **kwargs):
            print(f"Mock: Uploading {path} to storage")
            return {"path": path}
        
        def download(self, path):
            print(f"Mock: Downloading {path} from storage")
            return b"mock file content"
    
    class MockTable:
        def insert(self, data, **kwargs):
            print(f"Mock: Inserting data into table")
            return {"data": data}
        
        def select(self, *args, **kwargs):
            print(f"Mock: Selecting from table")
            return {"data": []}
        
        def update(self, data, **kwargs):
            print(f"Mock: Updating table")
            return {"data": data}
        
        def delete(self, **kwargs):
            print(f"Mock: Deleting from table")
            return {"data": []}
    
    return MockSupabaseClient()

def get_supabase_anon_client() -> Client:
    """Get Supabase client with anonymous key for frontend operations"""
    supabase_url = os.getenv("NEXT_PUBLIC_SUPABASE_URL")
    supabase_key = os.getenv("NEXT_PUBLIC_SUPABASE_ANON_KEY")
    
    # Check if we have placeholder values
    if (not supabase_url or not supabase_key or 
        supabase_url == "your_supabase_url_here" or 
        supabase_key == "your_supabase_anon_key_here"):
        print("⚠️  Warning: Supabase anonymous client not configured. Using mock client for development.")
        return create_mock_supabase_client()
    
    try:
        return create_client(supabase_url, supabase_key)
    except Exception as e:
        print(f"⚠️  Warning: Failed to create Supabase anonymous client: {str(e)}. Using mock client for development.")
        return create_mock_supabase_client() 