"""
Document Loaders for DevDocs AI
Handles loading different document types (OpenAPI, PDF, Markdown)
"""

import os
import yaml
import json
from typing import List, Dict, Any
from langchain.schema import Document
from langchain_community.document_loaders import PyPDFLoader, TextLoader

class DocumentLoader:
    def __init__(self):
        pass

    def load_openapi(self, file_path: str) -> List[Document]:
        """Load OpenAPI specification file (YAML/JSON)"""
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                if file_path.endswith(('.yaml', '.yml')):
                    spec = yaml.safe_load(file)
                elif file_path.endswith('.json'):
                    spec = json.load(file)
                else:
                    raise ValueError("Unsupported OpenAPI file format")
            
            documents = []
            
            # Extract OpenAPI spec components
            if 'info' in spec:
                info_text = f"API Information:\nTitle: {spec['info'].get('title', 'N/A')}\nVersion: {spec['info'].get('version', 'N/A')}\nDescription: {spec['info'].get('description', 'N/A')}"
                documents.append(Document(
                    page_content=info_text,
                    metadata={"type": "api_info", "section": "info"}
                ))
            
            # Extract paths
            if 'paths' in spec:
                for path, methods in spec['paths'].items():
                    for method, details in methods.items():
                        if isinstance(method, str) and method.upper() in ['GET', 'POST', 'PUT', 'DELETE', 'PATCH']:
                            path_text = f"Endpoint: {method.upper()} {path}\n"
                            path_text += f"Summary: {details.get('summary', 'N/A')}\n"
                            path_text += f"Description: {details.get('description', 'N/A')}\n"
                            
                            # Add parameters
                            if 'parameters' in details:
                                path_text += "Parameters:\n"
                                for param in details['parameters']:
                                    path_text += f"- {param.get('name', 'N/A')} ({param.get('in', 'N/A')}): {param.get('description', 'N/A')}\n"
                            
                            # Add request body
                            if 'requestBody' in details:
                                path_text += f"Request Body: {details['requestBody'].get('description', 'N/A')}\n"
                            
                            # Add responses
                            if 'responses' in details:
                                path_text += "Responses:\n"
                                for status, response in details['responses'].items():
                                    path_text += f"- {status}: {response.get('description', 'N/A')}\n"
                            
                            documents.append(Document(
                                page_content=path_text,
                                metadata={
                                    "type": "endpoint",
                                    "method": method.upper(),
                                    "path": path,
                                    "section": "paths"
                                }
                            ))
            
            # Extract schemas/components
            if 'components' in spec and 'schemas' in spec['components']:
                for schema_name, schema in spec['components']['schemas'].items():
                    schema_text = f"Schema: {schema_name}\n"
                    schema_text += f"Type: {schema.get('type', 'N/A')}\n"
                    schema_text += f"Description: {schema.get('description', 'N/A')}\n"
                    
                    if 'properties' in schema:
                        schema_text += "Properties:\n"
                        for prop_name, prop_details in schema['properties'].items():
                            schema_text += f"- {prop_name} ({prop_details.get('type', 'N/A')}): {prop_details.get('description', 'N/A')}\n"
                    
                    documents.append(Document(
                        page_content=schema_text,
                        metadata={
                            "type": "schema",
                            "schema_name": schema_name,
                            "section": "components/schemas"
                        }
                    ))
            
            return documents
            
        except Exception as e:
            raise Exception(f"Error loading OpenAPI spec: {str(e)}")

    def load_pdf(self, file_path: str) -> List[Document]:
        """Load PDF document"""
        try:
            loader = PyPDFLoader(file_path)
            documents = loader.load()
            
            # Add metadata about the document
            for doc in documents:
                doc.metadata.update({
                    "type": "pdf",
                    "file_path": file_path,
                    "page_number": doc.metadata.get("page", 1)
                })
            
            return documents
            
        except Exception as e:
            raise Exception(f"Error loading PDF: {str(e)}")

    def load_markdown(self, file_path: str) -> List[Document]:
        """Load Markdown document"""
        try:
            loader = TextLoader(file_path, encoding='utf-8')
            documents = loader.load()
            
            # Add metadata about the document
            for doc in documents:
                doc.metadata.update({
                    "type": "markdown",
                    "file_path": file_path
                })
            
            return documents
            
        except Exception as e:
            raise Exception(f"Error loading Markdown: {str(e)}")

    def load_document(self, file_path: str, doc_type: str) -> List[Document]:
        """Load document based on type"""
        if doc_type == "openapi":
            return self.load_openapi(file_path)
        elif doc_type == "pdf":
            return self.load_pdf(file_path)
        elif doc_type == "markdown":
            return self.load_markdown(file_path)
        else:
            raise ValueError(f"Unsupported document type: {doc_type}") 