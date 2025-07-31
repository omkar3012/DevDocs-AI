'use client';

import React, { useState, useEffect } from 'react';
import { FileText, Trash2, Calendar, Download } from 'lucide-react';
import toast from 'react-hot-toast';
import { api } from '../utils/api';
import ProcessingStatus from './ProcessingStatus';

interface DocumentListProps {
  documents: any[];
  onDocumentSelect: (document: any) => void;
  onDocumentDelete: () => void;
  loading: boolean;
  supabase: any;
}

export default function DocumentList({ documents, onDocumentSelect, onDocumentDelete, loading, supabase }: DocumentListProps) {
  const [documentStatuses, setDocumentStatuses] = useState<{[key: string]: any}>({});

  // Check document processing status
  useEffect(() => {
    const checkDocumentStatuses = async () => {
      const statuses: {[key: string]: any} = {};
      
      for (const doc of documents) {
        try {
          const status = await api.checkDocumentStatus(doc.id);
          statuses[doc.id] = status;
        } catch (error) {
          console.warn(`Failed to check status for document ${doc.id}:`, error);
          statuses[doc.id] = { status: 'unknown', chunk_count: 0 };
        }
      }
      
      setDocumentStatuses(statuses);
    };

    if (documents.length > 0) {
      checkDocumentStatuses();
      
      // Auto-refresh processing documents every 5 seconds
      const interval = setInterval(() => {
        const processingDocs = documents.filter(doc => 
          documentStatuses[doc.id]?.status === 'processing'
        );
        
        if (processingDocs.length > 0) {
          checkDocumentStatuses();
        }
      }, 5000);
      
      return () => clearInterval(interval);
    }
  }, [documents, documentStatuses]);
  const handleDelete = async (docId: string) => {
    if (!confirm('Are you sure you want to delete this document?')) return;

    try {
      // Delete from Supabase database
      const { error: dbError } = await supabase
        .from('api_documents')
        .delete()
        .eq('id', docId);

      if (dbError) throw dbError;

      // Delete from Supabase storage (if file exists)
      const document = documents.find(doc => doc.id === docId);
      if (document?.storage_path) {
        const { error: storageError } = await supabase.storage
          .from('api-docs')
          .remove([document.storage_path]);

        if (storageError) {
          console.warn('Failed to delete file from storage:', storageError);
        }
      }

      // Delete chunks from database
      const { error: chunksError } = await supabase
        .from('api_chunks')
        .delete()
        .eq('doc_id', docId);

      if (chunksError) {
        console.warn('Failed to delete chunks:', chunksError);
      }

      toast.success('Document deleted successfully');
      onDocumentDelete();
    } catch (error) {
      console.error('Error deleting document:', error);
      toast.error('Failed to delete document');
    }
  };

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
    });
  };

  const getDocumentIcon = (type: string) => {
    switch (type) {
      case 'openapi':
        return '📋';
      case 'pdf':
        return '📄';
      case 'markdown':
        return '📝';
      default:
        return '📄';
    }
  };

  if (loading) {
    return (
      <div className="p-6">
        <div className="flex items-center justify-center">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
          <span className="ml-2 text-gray-600">Loading documents...</span>
        </div>
      </div>
    );
  }

  if (documents.length === 0) {
    return (
      <div className="p-6">
        <div className="text-center">
          <FileText size={64} className="text-gray-400 mx-auto mb-4" />
          <h2 className="text-2xl font-bold text-gray-900 mb-2">No Documents</h2>
          <p className="text-gray-600 mb-6">
            You haven't uploaded any documents yet. Start by uploading your first document.
          </p>
          <button
            onClick={() => window.location.href = '/upload'}
            className="px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
          >
            Upload Document
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="p-6">
      <div className="mb-6">
        <h2 className="text-2xl font-bold text-gray-900 mb-2">Your Documents</h2>
        <p className="text-gray-600">
          Manage your uploaded API specifications and documentation
        </p>
      </div>

      {/* Debug Processing Button */}
      {documents.length > 0 && (
        <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4 mb-6">
          <h3 className="text-sm font-medium text-yellow-800 mb-2">Debug Tools</h3>
          <button
            onClick={async () => {
              try {
                const userId = documents[0]?.user_id; // Get user ID from first document
                if (!userId) {
                  toast.error('No documents found to process');
                  return;
                }
                
                toast.loading('Force processing all documents...', { duration: 10000 });
                const result = await api.debugProcessAllDocuments(userId);
                
                toast.success(`Processing complete: ${result.processed} processed, ${result.failed} failed`);
                
                // Refresh document statuses after a short delay
                setTimeout(() => {
                  window.location.reload();
                }, 2000);
                
              } catch (error) {
                toast.error('Failed to force process documents');
                console.error('Debug processing error:', error);
              }
            }}
            className="px-4 py-2 bg-yellow-600 text-white rounded hover:bg-yellow-700 text-sm"
          >
            🔧 Force Process All Documents
          </button>
          <p className="text-xs text-yellow-600 mt-1">
            Use this if documents are stuck in "Processing" status
          </p>
        </div>
      )}

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {documents.map((document) => (
          <div
            key={document.id}
            className="bg-white rounded-lg shadow-sm border border-gray-200 hover:shadow-md transition-shadow"
          >
            <div className="p-6">
              <div className="flex items-start justify-between mb-4">
                <div className="flex items-center gap-3">
                  <span className="text-2xl">{getDocumentIcon(document.type)}</span>
                  <div>
                    <h3 className="font-semibold text-gray-900 truncate">
                      {document.name}
                    </h3>
                    <p className="text-sm text-gray-500 capitalize">
                      {document.type}
                    </p>
                  </div>
                </div>
                <button
                  onClick={() => handleDelete(document.id)}
                  className="p-1 text-gray-400 hover:text-red-600 transition-colors"
                  title="Delete document"
                >
                  <Trash2 size={16} />
                </button>
              </div>

              <div className="space-y-2 mb-4">
                <div className="flex items-center gap-2 text-sm text-gray-600">
                  <Calendar size={14} />
                  <span>Uploaded {formatDate(document.created_at)}</span>
                </div>
                {document.version && (
                  <div className="text-sm text-gray-600">
                    Version: {document.version}
                  </div>
                )}
                
                {/* Processing Status */}
                <ProcessingStatus
                  docId={document.id}
                  status={documentStatuses[document.id]?.status || 'unknown'}
                  chunkCount={documentStatuses[document.id]?.chunk_count || 0}
                  onStatusUpdate={(newStatus) => {
                    setDocumentStatuses(prev => ({
                      ...prev,
                      [document.id]: newStatus
                    }));
                  }}
                />
              </div>

              <div className="flex gap-2">
                <button
                  onClick={() => onDocumentSelect(document)}
                  className="flex-1 px-4 py-2 bg-blue-600 text-white text-sm rounded-lg hover:bg-blue-700 transition-colors"
                >
                  Chat
                </button>
                <button
                  onClick={() => window.open(`/api/documents/${document.id}/download`, '_blank')}
                  className="px-4 py-2 border border-gray-300 text-gray-700 text-sm rounded-lg hover:bg-gray-50 transition-colors"
                  title="Download original file"
                >
                  <Download size={16} />
                </button>
              </div>
            </div>
          </div>
        ))}
      </div>

      <div className="mt-8 bg-blue-50 rounded-lg p-4">
        <h3 className="font-medium text-gray-900 mb-2">Document Management Tips</h3>
        <ul className="text-sm text-gray-600 space-y-1">
          <li>• Documents are processed asynchronously after upload</li>
          <li>• You can chat with any document once processing is complete</li>
          <li>• Deleting a document removes all associated chunks and embeddings</li>
          <li>• Original files are stored securely in Supabase Storage</li>
        </ul>
      </div>
    </div>
  );
} 