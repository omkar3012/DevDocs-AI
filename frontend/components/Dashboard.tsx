'use client';

import React, { useState, useEffect } from 'react';
import { User } from '@supabase/supabase-js';
import DocumentUpload from './DocumentUpload';
import ChatInterface from './ChatInterface';
import DocumentList from './DocumentList';
import Sidebar from './Sidebar';
import { LogOut, Upload, MessageSquare, FileText, Settings } from 'lucide-react';
import { db } from '../utils/supabase';

interface DashboardProps {
  session: any;
  supabase: any;
}

type TabType = 'upload' | 'chat' | 'documents' | 'settings';

export default function Dashboard({ session, supabase }: DashboardProps) {
  const [activeTab, setActiveTab] = useState<TabType>('upload');
  const [selectedDocument, setSelectedDocument] = useState<any>(null);
  const [documents, setDocuments] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);

  const user: User = session.user;

  useEffect(() => {
    fetchDocuments();
  }, [user.id]);

  const fetchDocuments = async () => {
    try {
      const documents = await db.getDocuments(user.id);
      setDocuments(documents);
    } catch (error) {
      console.error('Error fetching documents:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleSignOut = async () => {
    await supabase.auth.signOut();
  };

  const handleDocumentUploaded = () => {
    fetchDocuments();
    setActiveTab('documents');
  };

  const handleDocumentSelect = (document: any) => {
    setSelectedDocument(document);
    setActiveTab('chat');
  };

  const renderTabContent = () => {
    switch (activeTab) {
      case 'upload':
        return (
          <DocumentUpload
            supabase={supabase}
            userId={user.id}
            onUploadComplete={handleDocumentUploaded}
          />
        );
      case 'chat':
        return (
          <ChatInterface
            supabase={supabase}
            userId={user.id}
            selectedDocument={selectedDocument}
            documents={documents}
          />
        );
      case 'documents':
        return (
          <DocumentList
            documents={documents}
            onDocumentSelect={handleDocumentSelect}
            onDocumentDelete={fetchDocuments}
            loading={loading}
            userId={user.id}
          />
        );
      case 'settings':
        return (
          <div className="p-6">
            <h2 className="text-2xl font-bold mb-4">Settings</h2>
            <div className="bg-white rounded-lg shadow p-6">
              <div className="mb-4">
                <h3 className="text-lg font-semibold mb-2">Account Information</h3>
                <p className="text-gray-600">Email: {user.email}</p>
                <p className="text-gray-600">User ID: {user.id}</p>
              </div>
              <button
                onClick={handleSignOut}
                className="flex items-center gap-2 px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700 transition-colors"
              >
                <LogOut size={16} />
                Sign Out
              </button>
            </div>
          </div>
        );
      default:
        return null;
    }
  };

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white shadow-sm border-b">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center h-16">
            <div className="flex items-center">
              <h1 className="text-xl font-bold text-gray-900">DevDocs AI</h1>
            </div>
            <div className="flex items-center gap-4">
              <span className="text-sm text-gray-600">
                Welcome, {user.email}
              </span>
              <button
                onClick={handleSignOut}
                className="flex items-center gap-2 px-3 py-2 text-sm text-gray-600 hover:text-gray-900 transition-colors"
              >
                <LogOut size={16} />
                Sign Out
              </button>
            </div>
          </div>
        </div>
      </header>

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
        <div className="flex gap-6">
          {/* Sidebar */}
          <Sidebar
            activeTab={activeTab}
            onTabChange={setActiveTab}
            documentCount={documents.length}
          />

          {/* Main Content */}
          <div className="flex-1">
            {renderTabContent()}
          </div>
        </div>
      </div>
    </div>
  );
} 