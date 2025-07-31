'use client';

import React from 'react';
import { Clock, CheckCircle, AlertCircle, RefreshCw } from 'lucide-react';
import toast from 'react-hot-toast';
import { api } from '../utils/api';

interface ProcessingStatusProps {
  docId: string;
  status: string;
  chunkCount: number;
  onStatusUpdate: (newStatus: any) => void;
}

export default function ProcessingStatus({ docId, status, chunkCount, onStatusUpdate }: ProcessingStatusProps) {
  const [isProcessing, setIsProcessing] = React.useState(false);

  const handleRetry = async () => {
    setIsProcessing(true);
    try {
      await api.processDocument(docId);
      toast.success('Document processing triggered');
      
      // Wait a moment then check status
      setTimeout(async () => {
        try {
          const newStatus = await api.checkDocumentStatus(docId);
          onStatusUpdate(newStatus);
        } catch (error) {
          console.error('Failed to check status after retry:', error);
        }
      }, 2000);
      
    } catch (error) {
      toast.error('Failed to trigger processing');
      console.error('Retry failed:', error);
    } finally {
      setIsProcessing(false);
    }
  };

  switch (status) {
    case 'ready':
      return (
        <div className="flex items-center gap-2 text-sm">
          <CheckCircle size={14} className="text-green-600" />
          <span className="text-green-600">Ready ({chunkCount} chunks)</span>
        </div>
      );
      
    case 'processing':
      return (
        <div className="flex items-center gap-2 text-sm">
          <Clock size={14} className="text-yellow-600" />
          <span className="text-yellow-600">Processing...</span>
          <button
            onClick={handleRetry}
            disabled={isProcessing}
            className="text-xs px-2 py-1 bg-blue-600 text-white rounded hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-1"
          >
            {isProcessing ? (
              <>
                <RefreshCw size={10} className="animate-spin" />
                Retrying...
              </>
            ) : (
              'Retry'
            )}
          </button>
        </div>
      );
      
    case 'failed':
      return (
        <div className="flex items-center gap-2 text-sm">
          <AlertCircle size={14} className="text-red-600" />
          <span className="text-red-600">Failed</span>
          <button
            onClick={handleRetry}
            disabled={isProcessing}
            className="text-xs px-2 py-1 bg-red-600 text-white rounded hover:bg-red-700 disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-1"
          >
            {isProcessing ? (
              <>
                <RefreshCw size={10} className="animate-spin" />
                Retrying...
              </>
            ) : (
              'Retry'
            )}
          </button>
        </div>
      );
      
    default:
      return (
        <div className="flex items-center gap-2 text-sm">
          <Clock size={14} className="text-gray-400" />
          <span className="text-gray-400">Checking status...</span>
        </div>
      );
  }
} 