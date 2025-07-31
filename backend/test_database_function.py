#!/usr/bin/env python3
"""
Test script to verify the database function exists and works correctly
"""

import os
import sys
from dotenv import load_dotenv

# Add the current directory to the path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from supabase_client import get_supabase_client

load_dotenv()

def test_database_function():
    """Test if the match_documents function exists and works"""
    try:
        supabase = get_supabase_client()
        
        # Test 1: Check if the function exists
        print("🔍 Testing if match_documents function exists...")
        
        # Create a dummy embedding (1536 dimensions)
        dummy_embedding = [0.1] * 1536
        
        # Try to call the function
        result = supabase.rpc(
            "match_documents",
            {
                "query_embedding": dummy_embedding,
                "match_threshold": 0.1,
                "match_count": 5,
                "filter": {}
            }
        ).execute()
        
        print("✅ match_documents function exists and works!")
        print(f"📊 Result: {len(result.data)} chunks found")
        
        return True
        
    except Exception as e:
        print(f"❌ Error testing match_documents function: {str(e)}")
        
        # Try to check what functions exist
        try:
            print("\n🔍 Checking what functions exist...")
            
            # Try to list functions (this might not work with Supabase client)
            # But we can try different function names
            
            functions_to_try = [
                "match_documents",
                "match_chunks", 
                "match_vectors",
                "similarity_search"
            ]
            
            for func_name in functions_to_try:
                try:
                    result = supabase.rpc(
                        func_name,
                        {
                            "query_embedding": [0.1] * 1536,
                            "match_threshold": 0.1,
                            "match_count": 1,
                            "filter": {}
                        }
                    ).execute()
                    print(f"✅ Function '{func_name}' exists!")
                except Exception as func_error:
                    print(f"❌ Function '{func_name}' does not exist: {str(func_error)[:100]}...")
                    
        except Exception as list_error:
            print(f"❌ Could not check functions: {str(list_error)}")
        
        return False

def test_table_structure():
    """Test if the api_chunks table has the correct structure"""
    try:
        supabase = get_supabase_client()
        
        print("\n🔍 Testing api_chunks table structure...")
        
        # Try to select from the table
        result = supabase.table("api_chunks").select("id, doc_id, chunk_text, embedding").limit(1).execute()
        
        print("✅ api_chunks table exists!")
        print(f"📊 Table has {len(result.data)} rows")
        
        if result.data:
            # Check the structure of the first row
            first_row = result.data[0]
            print(f"📋 Table columns: {list(first_row.keys())}")
            
            # Check embedding dimension
            if 'embedding' in first_row and first_row['embedding']:
                embedding_length = len(first_row['embedding'])
                print(f"🔢 Embedding dimension: {embedding_length}")
                
                if embedding_length == 1536:
                    print("✅ Embedding dimension is correct (1536)")
                else:
                    print(f"⚠️  Embedding dimension is {embedding_length}, expected 1536")
        
        return True
        
    except Exception as e:
        print(f"❌ Error testing table structure: {str(e)}")
        return False

def main():
    """Main test function"""
    print("🧪 Testing Database Function and Structure")
    print("=" * 50)
    
    # Test table structure
    table_ok = test_table_structure()
    
    # Test function
    function_ok = test_database_function()
    
    print("\n" + "=" * 50)
    print("📋 Test Results:")
    print(f"   Table Structure: {'✅ PASS' if table_ok else '❌ FAIL'}")
    print(f"   Function: {'✅ PASS' if function_ok else '❌ FAIL'}")
    
    if table_ok and function_ok:
        print("\n🎉 All tests passed! Database is ready.")
    else:
        print("\n⚠️  Some tests failed. Check the database setup.")
        print("\n💡 To fix the function issue, run the migration:")
        print("   supabase db reset")
        print("   # or apply the specific migration:")
        print("   # supabase/migrations/008_fix_match_function.sql")

if __name__ == "__main__":
    main() 