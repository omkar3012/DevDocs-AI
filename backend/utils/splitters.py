"""
Document Splitters for DevDocs AI
Handles splitting documents into chunks for better retrieval
"""

from typing import List, Dict, Any
from langchain.schema import Document
from langchain.text_splitter import RecursiveCharacterTextSplitter

class DocumentSplitter:
    def __init__(self, chunk_size: int = 800, chunk_overlap: int = 100):
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            length_function=len,
            separators=["\n\n", "\n", " ", ""]
        )

    def split_documents(self, documents: List[Document]) -> List[Dict[str, Any]]:
        """Split documents into chunks"""
        chunks = []
        
        for doc in documents:
            # Split the document content
            doc_chunks = self.text_splitter.split_text(doc.page_content)
            
            # Create chunk objects with metadata
            for i, chunk_text in enumerate(doc_chunks):
                chunk = {
                    "text": chunk_text,
                    "metadata": {
                        **doc.metadata,
                        "chunk_index": i,
                        "total_chunks": len(doc_chunks)
                    }
                }
                chunks.append(chunk)
        
        return chunks

    def split_text(self, text: str, metadata: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        """Split a single text into chunks"""
        chunks = self.text_splitter.split_text(text)
        
        result = []
        for i, chunk_text in enumerate(chunks):
            chunk = {
                "text": chunk_text,
                "metadata": {
                    **(metadata or {}),
                    "chunk_index": i,
                    "total_chunks": len(chunks)
                }
            }
            result.append(chunk)
        
        return result

    def split_openapi_spec(self, spec: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Specialized splitter for OpenAPI specifications"""
        chunks = []
        
        # Split info section
        if 'info' in spec:
            info_text = f"API Information:\nTitle: {spec['info'].get('title', 'N/A')}\nVersion: {spec['info'].get('version', 'N/A')}\nDescription: {spec['info'].get('description', 'N/A')}"
            info_chunks = self.split_text(info_text, {"type": "api_info", "section": "info"})
            chunks.extend(info_chunks)
        
        # Split paths section
        if 'paths' in spec:
            for path, methods in spec['paths'].items():
                for method, details in methods.items():
                    if isinstance(method, str) and method.upper() in ['GET', 'POST', 'PUT', 'DELETE', 'PATCH']:
                        path_text = self._format_endpoint_text(method, path, details)
                        path_chunks = self.split_text(
                            path_text, 
                            {
                                "type": "endpoint",
                                "method": method.upper(),
                                "path": path,
                                "section": "paths"
                            }
                        )
                        chunks.extend(path_chunks)
        
        # Split schemas section
        if 'components' in spec and 'schemas' in spec['components']:
            for schema_name, schema in spec['components']['schemas'].items():
                schema_text = self._format_schema_text(schema_name, schema)
                schema_chunks = self.split_text(
                    schema_text,
                    {
                        "type": "schema",
                        "schema_name": schema_name,
                        "section": "components/schemas"
                    }
                )
                chunks.extend(schema_chunks)
        
        return chunks

    def _format_endpoint_text(self, method: str, path: str, details: Dict[str, Any]) -> str:
        """Format endpoint information as text"""
        text = f"Endpoint: {method.upper()} {path}\n"
        text += f"Summary: {details.get('summary', 'N/A')}\n"
        text += f"Description: {details.get('description', 'N/A')}\n"
        
        # Add parameters
        if 'parameters' in details:
            text += "Parameters:\n"
            for param in details['parameters']:
                text += f"- {param.get('name', 'N/A')} ({param.get('in', 'N/A')}): {param.get('description', 'N/A')}\n"
        
        # Add request body
        if 'requestBody' in details:
            text += f"Request Body: {details['requestBody'].get('description', 'N/A')}\n"
        
        # Add responses
        if 'responses' in details:
            text += "Responses:\n"
            for status, response in details['responses'].items():
                text += f"- {status}: {response.get('description', 'N/A')}\n"
        
        return text

    def _format_schema_text(self, schema_name: str, schema: Dict[str, Any]) -> str:
        """Format schema information as text"""
        text = f"Schema: {schema_name}\n"
        text += f"Type: {schema.get('type', 'N/A')}\n"
        text += f"Description: {schema.get('description', 'N/A')}\n"
        
        if 'properties' in schema:
            text += "Properties:\n"
            for prop_name, prop_details in schema['properties'].items():
                text += f"- {prop_name} ({prop_details.get('type', 'N/A')}): {prop_details.get('description', 'N/A')}\n"
        
        return text 