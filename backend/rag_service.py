"""
RAG Service for DevDocs AI
Handles embeddings, vector search, and answer generation using OpenAI
"""

import os
import numpy as np
import re
from typing import List, Dict, Tuple, Any, AsyncGenerator, Optional
from dotenv import load_dotenv
from supabase_client import get_supabase_client
from collections import Counter

# Try to import NLTK, but make it optional
try:
    import nltk
    from nltk.tokenize import sent_tokenize, word_tokenize
    from nltk.corpus import stopwords
    from nltk.stem import WordNetLemmatizer
    
    # Download required NLTK data
    try:
        nltk.data.find('tokenizers/punkt')
    except LookupError:
        nltk.download('punkt')
    try:
        nltk.data.find('corpora/stopwords')
    except LookupError:
        nltk.download('stopwords')
    try:
        nltk.data.find('corpora/wordnet')
    except LookupError:
        nltk.download('wordnet')
    
    NLTK_AVAILABLE = True
except ImportError:
    NLTK_AVAILABLE = False
    print("ℹ️  NLTK not available - will use simple summarizer")

from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import SupabaseVectorStore
from langchain.chains import RetrievalQA
from langchain.prompts import PromptTemplate
from langchain_openai import ChatOpenAI
from pydantic import BaseModel, Field

load_dotenv()

if NLTK_AVAILABLE:
    class IntelligentSummarizer:
        """Intelligent summarizer that works without external LLM"""
        
        def __init__(self):
            self.lemmatizer = WordNetLemmatizer()
            self.stop_words = set(stopwords.words('english'))
        
        def extract_keywords(self, text: str, top_k: int = 10) -> List[str]:
            """Extract key terms from text"""
            # Tokenize and clean
            words = word_tokenize(text.lower())
            words = [self.lemmatizer.lemmatize(word) for word in words if word.isalnum() and word not in self.stop_words]
            
            # Count frequencies
            word_freq = Counter(words)
            return [word for word, freq in word_freq.most_common(top_k)]
        
        def extract_relevant_sentences(self, text: str, question: str, max_sentences: int = 5) -> List[str]:
            """Extract sentences most relevant to the question"""
            sentences = sent_tokenize(text)
            
            # Score sentences based on keyword overlap with question
            question_keywords = set(self.extract_keywords(question, 20))
            
            sentence_scores = []
            for sentence in sentences:
                sentence_keywords = set(self.extract_keywords(sentence, 20))
                overlap = len(question_keywords.intersection(sentence_keywords))
                sentence_scores.append((sentence, overlap))
            
            # Sort by relevance and return top sentences
            sentence_scores.sort(key=lambda x: x[1], reverse=True)
            return [sentence for sentence, score in sentence_scores[:max_sentences] if score > 0]
        
        def generate_answer(self, context: str, question: str, chunks: List[Dict]) -> str:
            """Generate an intelligent answer without external LLM"""
            
            # Extract question type
            question_lower = question.lower()
            if any(word in question_lower for word in ['what', 'how', 'why', 'when', 'where']):
                question_type = 'information'
            elif any(word in question_lower for word in ['list', 'name', 'examples', 'features']):
                question_type = 'list'
            elif any(word in question_lower for word in ['compare', 'difference', 'versus']):
                question_type = 'comparison'
            else:
                question_type = 'general'
            
            # Extract relevant information based on question type
            if question_type == 'information':
                relevant_sentences = self.extract_relevant_sentences(context, question, 3)
                if relevant_sentences:
                    answer = f"Based on the documentation, here's what I found:\n\n"
                    for i, sentence in enumerate(relevant_sentences, 1):
                        answer += f"{i}. {sentence.strip()}\n\n"
                else:
                    answer = f"I found {len(chunks)} relevant sections in the documentation, but couldn't extract specific information to answer your question. Here are the key sections:\n\n"
                    for i, chunk in enumerate(chunks[:3], 1):
                        answer += f"{i}. {chunk['chunk_text'][:150]}...\n\n"
            
            elif question_type == 'list':
                keywords = self.extract_keywords(context, 15)
                answer = f"Based on the documentation, here are the key points:\n\n"
                for i, keyword in enumerate(keywords[:8], 1):
                    answer += f"{i}. {keyword.title()}\n"
                answer += f"\nI found {len(chunks)} relevant sections with detailed information about these topics."
            
            elif question_type == 'comparison':
                answer = f"I found {len(chunks)} relevant sections that might contain comparison information. Here are the key sections:\n\n"
                for i, chunk in enumerate(chunks[:3], 1):
                    answer += f"{i}. {chunk['chunk_text'][:200]}...\n\n"
            
            else:  # general
                # Create a comprehensive summary
                answer = f"Based on the documentation, I found {len(chunks)} relevant sections. Here's a comprehensive overview:\n\n"
                
                # Group chunks by similarity and create sections
                for i, chunk in enumerate(chunks[:5], 1):
                    answer += f"**Section {i}** (Relevance: {chunk['similarity_score']:.2f}):\n"
                    answer += f"{chunk['chunk_text'][:250]}...\n\n"
            
            answer += "\n---\n*This response was generated using semantic search and intelligent text analysis. For more detailed information, please review the specific sections in the documentation.*"
            
            return answer

class SimpleIntelligentSummarizer:
    """Simple intelligent summarizer that works without NLTK"""
    
    def __init__(self):
        # Simple stop words list
        self.stop_words = {
            'a', 'an', 'and', 'are', 'as', 'at', 'be', 'by', 'for', 'from', 'has', 'he', 
            'in', 'is', 'it', 'its', 'of', 'on', 'that', 'the', 'to', 'was', 'will', 'with',
            'i', 'you', 'your', 'we', 'they', 'them', 'this', 'these', 'those', 'but', 'or',
            'if', 'then', 'else', 'when', 'where', 'why', 'how', 'all', 'any', 'both', 'each',
            'few', 'more', 'most', 'other', 'some', 'such', 'no', 'nor', 'not', 'only', 'own',
            'same', 'so', 'than', 'too', 'very', 'can', 'will', 'just', 'should', 'now'
        }
    
    def extract_keywords(self, text: str, top_k: int = 10) -> List[str]:
        """Extract key terms from text using simple word frequency"""
        # Simple tokenization
        words = re.findall(r'\b[a-zA-Z]+\b', text.lower())
        words = [word for word in words if word not in self.stop_words and len(word) > 2]
        
        # Count frequencies
        word_freq = Counter(words)
        return [word for word, freq in word_freq.most_common(top_k)]
    
    def extract_relevant_sentences(self, text: str, question: str, max_sentences: int = 5) -> List[str]:
        """Extract sentences most relevant to the question"""
        # Simple sentence splitting
        sentences = re.split(r'[.!?]+', text)
        sentences = [s.strip() for s in sentences if s.strip()]
        
        # Score sentences based on keyword overlap with question
        question_keywords = set(self.extract_keywords(question, 20))
        
        sentence_scores = []
        for sentence in sentences:
            sentence_keywords = set(self.extract_keywords(sentence, 20))
            overlap = len(question_keywords.intersection(sentence_keywords))
            sentence_scores.append((sentence, overlap))
        
        # Sort by relevance and return top sentences
        sentence_scores.sort(key=lambda x: x[1], reverse=True)
        return [sentence for sentence, score in sentence_scores[:max_sentences] if score > 0]
    
    def generate_answer(self, context: str, question: str, chunks: List[Dict]) -> str:
        """Generate an intelligent answer without external LLM"""
        
        # Extract question type
        question_lower = question.lower()
        if any(word in question_lower for word in ['what', 'how', 'why', 'when', 'where']):
            question_type = 'information'
        elif any(word in question_lower for word in ['list', 'name', 'examples', 'features']):
            question_type = 'list'
        elif any(word in question_lower for word in ['compare', 'difference', 'versus']):
            question_type = 'comparison'
        else:
            question_type = 'general'
        
        # Extract relevant information based on question type
        if question_type == 'information':
            relevant_sentences = self.extract_relevant_sentences(context, question, 3)
            if relevant_sentences:
                answer = f"Based on the documentation, here's what I found:\n\n"
                for i, sentence in enumerate(relevant_sentences, 1):
                    answer += f"{i}. {sentence.strip()}\n\n"
            else:
                answer = f"I found {len(chunks)} relevant sections in the documentation, but couldn't extract specific information to answer your question. Here are the key sections:\n\n"
                for i, chunk in enumerate(chunks[:3], 1):
                    answer += f"{i}. {chunk['chunk_text'][:150]}...\n\n"
        
        elif question_type == 'list':
            keywords = self.extract_keywords(context, 15)
            answer = f"Based on the documentation, here are the key points:\n\n"
            for i, keyword in enumerate(keywords[:8], 1):
                answer += f"{i}. {keyword.title()}\n"
            answer += f"\nI found {len(chunks)} relevant sections with detailed information about these topics."
        
        elif question_type == 'comparison':
            answer = f"I found {len(chunks)} relevant sections that might contain comparison information. Here are the key sections:\n\n"
            for i, chunk in enumerate(chunks[:3], 1):
                answer += f"{i}. {chunk['chunk_text'][:200]}...\n\n"
        
        else:  # general
            # Create a comprehensive summary
            answer = f"Based on the documentation, I found {len(chunks)} relevant sections. Here's a comprehensive overview:\n\n"
            
            # Group chunks by similarity and create sections
            for i, chunk in enumerate(chunks[:5], 1):
                answer += f"**Section {i}** (Relevance: {chunk['similarity_score']:.2f}):\n"
                answer += f"{chunk['chunk_text'][:250]}...\n\n"
        
        answer += "\n---\n*This response was generated using semantic search and intelligent text analysis. For more detailed information, please review the specific sections in the documentation.*"
        
        return answer

class RAGService:
    def __init__(self):
        # Initialize embeddings
        try:
            self.embeddings = OpenAIEmbeddings()
            print("✅ Embeddings initialized successfully")
        except Exception as e:
            print(f"⚠️  Warning: Failed to initialize embeddings: {str(e)}")
            self.embeddings = None
        
        # Initialize vector store
        try:
            self.vector_store = SupabaseVectorStore(
                client=get_supabase_client(),
                embedding=self.embeddings,
                table_name="api_chunks",
                query_name="match_documents"
            )
            print("✅ Vector store initialized successfully")
        except Exception as e:
            print(f"⚠️  Warning: Failed to initialize vector store: {str(e)}")
            self.vector_store = None
        
        # Initialize retriever
        self.retriever = None
        if self.vector_store:
            try:
                self.retriever = self.vector_store.as_retriever(
                    search_kwargs={"k": 5, "score_threshold": 0.1}
                )
                print("✅ Retriever initialized successfully")
            except Exception as e:
                print(f"⚠️  Warning: Failed to initialize retriever: {str(e)}")
        
        # Initialize Intelligent Summarizer (LLM-free alternative)
        if NLTK_AVAILABLE:
            try:
                self.summarizer = IntelligentSummarizer()
                print("✅ Intelligent Summarizer initialized successfully")
            except Exception as e:
                print(f"⚠️  NLTK-based summarizer failed, using simple summarizer: {str(e)}")
                self.summarizer = SimpleIntelligentSummarizer()
                print("✅ Simple Intelligent Summarizer initialized successfully")
        else:
            self.summarizer = SimpleIntelligentSummarizer()
            print("✅ Simple Intelligent Summarizer initialized successfully")
        
        # Try to initialize OpenAI LLM
        self.llm = None
        try:
            # Check if we have a valid OpenAI API key
            openai_api_key = os.getenv("OPENAI_API_KEY")
            if openai_api_key and openai_api_key != "your_openai_api_key_here":
                self.llm = ChatOpenAI(
                    model_name="gpt-3.5-turbo",
                    temperature=0.2,
                    max_tokens=1000
                )
                print("✅ OpenAI LLM initialized successfully")
            else:
                print("ℹ️  No valid OpenAI API key found - using intelligent summarizer")
                
        except Exception as e:
            print(f"ℹ️  LLM initialization failed - using intelligent summarizer: {str(e)}")
        
        # Define prompt template for text generation
        self.prompt_template = """Based on the following documentation context, please answer the user's question clearly and accurately.

Documentation Context:
{context}

User Question: {question}

Answer:"""
        
        # Initialize RetrievalQA chain (only if LLM is available)
        self.qa_chain = None
        if self.llm and self.retriever:
            try:
                self.qa_chain = RetrievalQA.from_chain_type(
                    llm=self.llm,
                    chain_type="stuff",
                    retriever=self.retriever,
                    return_source_documents=True
                )
                print("✅ QA Chain initialized successfully")
            except Exception as e:
                print(f"⚠️  Warning: Failed to initialize QA chain: {str(e)}")

    def get_embedding(self, text: str) -> List[float]:
        """Get embedding for a text string"""
        if not self.embeddings:
            # Return a mock embedding (zeros) - OpenAI embeddings are 1536 dimensions
            return [0.0] * 1536
        return self.embeddings.embed_query(text)

    async def get_answer(
        self, 
        question: str, 
        doc_id: str, 
        user_id: str = None
    ) -> Tuple[str, List[Dict], int]:
        """
        Get answer for a question using RAG
        Returns: (answer, sources, chunk_count)
        """
        # Check if RAG service is properly configured
        if not self.vector_store:
            return "⚠️  RAG service is not configured. Please set up Supabase credentials to use this feature.", [], 0
        
        try:
            print(f"🔍 Searching for answer to: '{question}' in document: {doc_id}")
            
            # Get query embedding
            query_embedding = self.get_embedding(question)
            
            # Use direct call to match_chunks with lower threshold
            supabase = get_supabase_client()
            result = supabase.rpc(
                "match_chunks",
                {
                    "query_embedding": query_embedding,
                    "match_threshold": 0.1,  # Lower threshold for better recall
                    "match_count": 5,
                    "doc_id": doc_id
                }
            ).execute()
            
            if not result.data:
                print(f"📊 No relevant chunks found")
                return "I couldn't find any relevant information in the documentation to answer your question. Please try rephrasing your question or ensure the document contains relevant content.", [], 0
            
            print(f"📊 Found {len(result.data)} relevant chunks")
            
            # Create context from documents
            context = "\n\n".join([chunk['chunk_text'] for chunk in result.data])
            print(f"📝 Context length: {len(context)} characters")
            
            # Generate answer - try LLM first, then intelligent summarizer
            answer = None
            
            # Try LLM if available
            if self.llm:
                try:
                    print("🤖 Attempting LLM generation...")
                    response = self.llm.invoke(
                        self.prompt_template.format(context=context, question=question)
                    )
                    answer = response.content
                    print("✅ Generated answer using LLM")
                except Exception as e:
                    print(f"⚠️  LLM failed: {str(e)}")
                    import traceback
                    print(f"🔍 LLM Error Details:")
                    traceback.print_exc()
            
            # Fall back to intelligent summarizer if LLM failed or not available
            if not answer:
                try:
                    print("🧠 Using intelligent summarizer...")
                    answer = self.summarizer.generate_answer(context, question, result.data)
                    print("✅ Generated answer using intelligent summarizer")
                except Exception as e:
                    print(f"⚠️  Intelligent summarizer failed: {str(e)}")
                    # Final fallback to simple summary
                    answer = f"Based on the documentation, I found {len(result.data)} relevant sections. Here's a summary of the key information:\n\n"
                    for i, chunk in enumerate(result.data[:3]):  # Use first 3 chunks
                        answer += f"{i+1}. {chunk['chunk_text'][:200]}...\n\n"
                    answer += "For more detailed information, please review the specific sections in the documentation."
            
            # Extract sources
            sources = []
            for chunk in result.data:
                source = {
                    "content": chunk['chunk_text'][:200] + "..." if len(chunk['chunk_text']) > 200 else chunk['chunk_text'],
                    "metadata": chunk['metadata'],
                    "similarity_score": chunk['similarity']
                }
                sources.append(source)
            
            print(f"✅ Generated answer with {len(sources)} sources")
            return answer, sources, len(result.data)
            
        except Exception as e:
            print(f"❌ Error in RAG service: {str(e)}")
            import traceback
            traceback.print_exc()
            return f"❌ Error getting answer: {str(e)}", [], 0

    async def get_answer_stream(
        self, 
        question: str, 
        doc_id: str, 
        user_id: str = None
    ) -> AsyncGenerator[Dict[str, Any], None]:
        """
        Stream answer for better UX
        """
        try:
            print(f"🔍 Streaming search for: '{question}' in document: {doc_id}")
            
            # Get query embedding
            query_embedding = self.get_embedding(question)
            
            # Use direct call to match_documents with lower threshold
            supabase = get_supabase_client()
            result = supabase.rpc(
                "match_documents",
                {
                    "query_embedding": query_embedding,
                    "match_threshold": 0.1,  # Lower threshold for better recall
                    "match_count": 5,
                    "filter": {"doc_id": doc_id}
                }
            ).execute()
            
            if not result.data:
                print(f"📊 No relevant chunks found")
                yield {"type": "answer", "content": "I couldn't find any relevant information in the documentation to answer your question. Please try rephrasing your question or ensure the document contains relevant content."}
                return
            
            print(f"📊 Found {len(result.data)} relevant chunks")
            
            # Send sources first
            sources = []
            for chunk in result.data:
                source = {
                    "content": chunk['chunk_text'][:200] + "..." if len(chunk['chunk_text']) > 200 else chunk['chunk_text'],
                    "metadata": chunk['metadata'],
                    "similarity_score": chunk['similarity']
                }
                sources.append(source)
            
            yield {"type": "sources", "content": sources}
            
            # Create context from documents
            context = "\n\n".join([chunk['chunk_text'] for chunk in result.data])
            
            # Stream answer - try LLM first, then intelligent summarizer
            answer_content = None
            
            # Try LLM if available
            if self.llm:
                try:
                    print("🤖 Attempting LLM generation (stream)...")
                    response = self.llm.invoke(
                        self.prompt_template.format(context=context, question=question)
                    )
                    answer_content = response.content
                    print("✅ Generated streaming answer using LLM")
                except Exception as e:
                    print(f"⚠️  LLM failed: {str(e)}")
                    import traceback
                    print(f"🔍 LLM Error Details:")
                    traceback.print_exc()
            
            # Fall back to intelligent summarizer if LLM failed or not available
            if not answer_content:
                try:
                    print("🧠 Using intelligent summarizer (stream)...")
                    answer_content = self.summarizer.generate_answer(context, question, result.data)
                    print("✅ Generated streaming answer using intelligent summarizer")
                except Exception as e:
                    print(f"⚠️  Intelligent summarizer failed: {str(e)}")
                    # Final fallback to simple summary
                    answer_content = f"Based on the documentation, I found {len(result.data)} relevant sections. Here's a summary of the key information:\n\n"
                    for i, chunk in enumerate(result.data[:3]):  # Use first 3 chunks
                        answer_content += f"{i+1}. {chunk['chunk_text'][:200]}...\n\n"
                    answer_content += "For more detailed information, please review the specific sections in the documentation."
            
            # Send answer
            yield {"type": "answer", "content": answer_content}
            
        except Exception as e:
            yield {"type": "error", "content": f"Sorry, I encountered an error: {str(e)}"}

    def search_similar_chunks(
        self, 
        query: str, 
        doc_id: str, 
        limit: int = 10
    ) -> List[Dict]:
        """Search for similar chunks in a document"""
        try:
            print(f"🔍 Searching similar chunks for: '{query}' in document: {doc_id}")
            
            # Get query embedding
            query_embedding = self.get_embedding(query)
            
            # Use direct call to match_documents with lower threshold
            supabase = get_supabase_client()
            result = supabase.rpc(
                "match_documents",
                {
                    "query_embedding": query_embedding,
                    "match_threshold": 0.1,  # Lower threshold for better recall
                    "match_count": limit,
                    "filter": {"doc_id": doc_id}
                }
            ).execute()
            
            if not result.data:
                print(f"📊 No similar chunks found")
                return []
            
            print(f"📊 Found {len(result.data)} similar chunks")
            
            # Format results
            chunks = []
            for chunk_data in result.data:
                chunk = {
                    "content": chunk_data['chunk_text'],
                    "metadata": chunk_data['metadata'],
                    "similarity_score": chunk_data['similarity']
                }
                chunks.append(chunk)
            
            return chunks
            
        except Exception as e:
            print(f"❌ Error searching chunks: {str(e)}")
            import traceback
            traceback.print_exc()
            return []

    def get_document_chunks(self, doc_id: str) -> List[Dict]:
        """Get all chunks for a document"""
        try:
            print(f"📄 Getting all chunks for document: {doc_id}")
            
            # Use a generic query to get all chunks for the document
            # This is a fallback method for when we need all chunks
            results = self.vector_store.similarity_search(
                "document content",  # Generic query to get chunks
                k=1000,  # Large number to get all chunks
                filter={"doc_id": doc_id}
            )
            
            if not results:
                print(f"📊 No chunks found in database for document {doc_id}")
                return []
            
            print(f"📊 Found {len(results)} chunks in database")
            
            # Format results
            chunks = []
            for doc in results:
                chunk = {
                    "id": doc.metadata.get("id"),
                    "content": doc.page_content,
                    "metadata": doc.metadata,
                    "chunk_index": doc.metadata.get("chunk_index")
                }
                chunks.append(chunk)
            
            # Sort by chunk index
            chunks.sort(key=lambda x: x.get("chunk_index", 0))
            
            return chunks
            
        except Exception as e:
            print(f"❌ Error getting document chunks: {str(e)}")
            return []

# Global instance - will be initialized lazily
_rag_service_instance = None

def get_rag_service() -> RAGService:
    """Get or create RAG service instance"""
    global _rag_service_instance
    if _rag_service_instance is None:
        _rag_service_instance = RAGService()
    return _rag_service_instance 