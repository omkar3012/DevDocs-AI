'use client';

import React, { useState, useCallback } from 'react';
import { useDropzone } from 'react-dropzone';
import { Upload, FileText, File, AlertCircle, CheckCircle } from 'lucide-react';
import toast from 'react-hot-toast';

interface DocumentUploadProps {
  supabase: any;
  userId: string;
  onUploadComplete: () => void;
}

export default function DocumentUpload({ supabase, userId, onUploadComplete }: DocumentUploadProps) {
  const [uploading, setUploading] = useState(false);
  const [uploadProgress, setUploadProgress] = useState(0);

  const onDrop = useCallback(async (acceptedFiles: File[]) => {
    setUploading(true);
    setUploadProgress(0);

    try {
      for (const file of acceptedFiles) {
        // Validate file type
        const allowedTypes = ['.yaml', '.yml', '.json', '.pdf', '.md', '.markdown'];
        const fileExtension = file.name.toLowerCase().substring(file.name.lastIndexOf('.'));
        
        if (!allowedTypes.includes(fileExtension)) {
          toast.error(`File type ${fileExtension} not supported`);
          continue;
        }

        // Determine document type
        const docTypeMap: { [key: string]: string } = {
          '.yaml': 'openapi', '.yml': 'openapi', '.json': 'openapi',
          '.pdf': 'pdf', '.md': 'markdown', '.markdown': 'markdown'
        };
        const docType = docTypeMap[fileExtension];

        // Upload to backend
        const formData = new FormData();
        formData.append('file', file);
        formData.append('user_id', userId);
        formData.append('version', ''); // Optional version field

        const response = await fetch('/api/upload', {
          method: 'POST',
          body: formData,
        });

        if (!response.ok) {
          throw new Error(`Upload failed: ${response.statusText}`);
        }

        const result = await response.json();
        toast.success(`${file.name} uploaded successfully!`);
        setUploadProgress((prev) => prev + (100 / acceptedFiles.length));
      }

      onUploadComplete();
    } catch (error) {
      console.error('Upload error:', error);
      toast.error('Upload failed. Please try again.');
    } finally {
      setUploading(false);
      setUploadProgress(0);
    }
  }, [userId, onUploadComplete]);

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      'application/json': ['.json'],
      'application/x-yaml': ['.yaml', '.yml'],
      'application/pdf': ['.pdf'],
      'text/markdown': ['.md', '.markdown'],
      'text/plain': ['.md', '.markdown']
    },
    multiple: true
  });

  return (
    <div className="p-6">
      <div className="max-w-2xl mx-auto">
        <div className="text-center mb-8">
          <h2 className="text-3xl font-bold text-gray-900 mb-4">Upload Documents</h2>
          <p className="text-gray-600">
            Upload API specifications, SDK manuals, or documentation files to start asking questions
          </p>
        </div>

        {/* Upload Area */}
        <div
          {...getRootProps()}
          className={`border-2 border-dashed rounded-lg p-8 text-center cursor-pointer transition-colors ${
            isDragActive
              ? 'border-blue-400 bg-blue-50'
              : 'border-gray-300 hover:border-gray-400'
          } ${uploading ? 'pointer-events-none opacity-50' : ''}`}
        >
          <input {...getInputProps()} />
          
          <div className="flex flex-col items-center">
            {uploading ? (
              <>
                <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mb-4"></div>
                <p className="text-lg font-medium text-gray-900 mb-2">Uploading...</p>
                <div className="w-full bg-gray-200 rounded-full h-2 mb-4">
                  <div
                    className="bg-blue-600 h-2 rounded-full transition-all duration-300"
                    style={{ width: `${uploadProgress}%` }}
                  ></div>
                </div>
                <p className="text-sm text-gray-600">{Math.round(uploadProgress)}% complete</p>
              </>
            ) : (
              <>
                <Upload size={48} className="text-gray-400 mb-4" />
                <p className="text-lg font-medium text-gray-900 mb-2">
                  {isDragActive ? 'Drop files here' : 'Drag & drop files here'}
                </p>
                <p className="text-gray-600 mb-4">or click to select files</p>
                
                <div className="flex flex-wrap justify-center gap-4 text-sm text-gray-500">
                  <div className="flex items-center gap-1">
                    <FileText size={16} />
                    <span>OpenAPI (YAML/JSON)</span>
                  </div>
                  <div className="flex items-center gap-1">
                    <File size={16} />
                    <span>PDF</span>
                  </div>
                  <div className="flex items-center gap-1">
                    <FileText size={16} />
                    <span>Markdown</span>
                  </div>
                </div>
              </>
            )}
          </div>
        </div>

        {/* Supported Formats */}
        <div className="mt-8 bg-blue-50 rounded-lg p-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-4 flex items-center gap-2">
            <CheckCircle size={20} className="text-green-600" />
            Supported Formats
          </h3>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div className="bg-white rounded-lg p-4">
              <h4 className="font-medium text-gray-900 mb-2">OpenAPI Specifications</h4>
              <p className="text-sm text-gray-600">YAML and JSON files containing API definitions</p>
              <div className="mt-2 text-xs text-gray-500">.yaml, .yml, .json</div>
            </div>
            <div className="bg-white rounded-lg p-4">
              <h4 className="font-medium text-gray-900 mb-2">PDF Documents</h4>
              <p className="text-sm text-gray-600">SDK manuals, guides, and technical documentation</p>
              <div className="mt-2 text-xs text-gray-500">.pdf</div>
            </div>
            <div className="bg-white rounded-lg p-4">
              <h4 className="font-medium text-gray-900 mb-2">Markdown Files</h4>
              <p className="text-sm text-gray-600">Developer guides and documentation</p>
              <div className="mt-2 text-xs text-gray-500">.md, .markdown</div>
            </div>
          </div>
        </div>

        {/* Tips */}
        <div className="mt-6 bg-yellow-50 rounded-lg p-4">
          <div className="flex items-start gap-3">
            <AlertCircle size={20} className="text-yellow-600 mt-0.5" />
            <div>
              <h4 className="font-medium text-gray-900 mb-1">Upload Tips</h4>
              <ul className="text-sm text-gray-600 space-y-1">
                <li>• Files are processed asynchronously - you'll be notified when ready</li>
                <li>• Maximum file size: 50MB per file</li>
                <li>• For OpenAPI specs, ensure they follow the 3.x specification</li>
                <li>• PDFs should be text-based (not scanned images)</li>
              </ul>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
} 