#!/usr/bin/env python3
"""
Test script for OpenAI integration
Verifies embeddings and LLM generation work correctly
"""

import os
import sys
from dotenv import load_dotenv

# Add the current directory to the path so we can import our modules
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from rag_service import RAGService

def test_openai_integration():
    """Test OpenAI embeddings and LLM generation"""
    print("🧪 Testing OpenAI Integration...")
    
    # Load environment variables
    load_dotenv()
    
    # Check if OpenAI API key is configured
    token = os.getenv("OPENAI_API_KEY")
    if not token or token == "your_openai_api_key_here":
        print("❌ OPENAI_API_KEY not configured in .env file")
        print("   Please add your OpenAI API key to the .env file")
        return False
    
    try:
        # Initialize RAG service
        print("📦 Initializing RAG service...")
        rag_service = RAGService()
        
        # Test embeddings
        print("🔍 Testing embeddings...")
        test_text = "How do I authenticate with the API?"
        embedding = rag_service.get_embedding(test_text)
        
        if embedding and len(embedding) > 0:
            print(f"✅ Embeddings working! Vector dimension: {len(embedding)}")
        else:
            print("❌ Embeddings failed")
            return False
        
        # Test LLM generation (if configured)
        if rag_service.llm:
            print("🤖 Testing LLM generation...")
            test_question = "What is the purpose of this API?"
            test_context = "This API provides authentication and user management functionality."
            
            # Create a simple prompt
            prompt = f"""
            Context: {test_context}
            
            Question: {test_question}
            
            Answer:"""
            
            try:
                response = rag_service.llm(prompt)
                if response and len(response.strip()) > 0:
                    print(f"✅ LLM generation working!")
                    print(f"   Response: {response[:100]}...")
                else:
                    print("❌ LLM generation returned empty response")
                    return False
            except Exception as e:
                print(f"❌ LLM generation failed: {str(e)}")
                return False
        else:
            print("⚠️  LLM not configured (mock mode)")
        
        print("🎉 All tests passed! OpenAI integration is working correctly.")
        return True
        
    except Exception as e:
        print(f"❌ Test failed with error: {str(e)}")
        return False

if __name__ == "__main__":
    success = test_openai_integration()
    sys.exit(0 if success else 1) 