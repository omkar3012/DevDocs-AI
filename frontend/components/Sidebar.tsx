'use client';

import React from 'react';
import { Upload, MessageSquare, FileText, Settings } from 'lucide-react';

interface SidebarProps {
  activeTab: 'upload' | 'chat' | 'documents' | 'settings';
  onTabChange: (tab: 'upload' | 'chat' | 'documents' | 'settings') => void;
  documentCount: number;
}

export default function Sidebar({ activeTab, onTabChange, documentCount }: SidebarProps) {
  const tabs = [
    {
      id: 'upload',
      label: 'Upload',
      icon: Upload,
      description: 'Upload API specs and docs'
    },
    {
      id: 'chat',
      label: 'Chat',
      icon: MessageSquare,
      description: 'Ask questions about your docs'
    },
    {
      id: 'documents',
      label: 'Documents',
      icon: FileText,
      description: `Manage your documents (${documentCount})`
    },
    {
      id: 'settings',
      label: 'Settings',
      icon: Settings,
      description: 'Account and preferences'
    }
  ];

  return (
    <div className="w-64 bg-white rounded-lg shadow-sm border">
      <div className="p-4">
        <h2 className="text-lg font-semibold text-gray-900 mb-4">Navigation</h2>
        <nav className="space-y-2">
          {tabs.map((tab) => {
            const Icon = tab.icon;
            const isActive = activeTab === tab.id;
            
            return (
              <button
                key={tab.id}
                onClick={() => onTabChange(tab.id as 'upload' | 'chat' | 'documents' | 'settings')}
                className={`w-full flex items-center gap-3 px-3 py-2 rounded-lg text-left transition-colors ${
                  isActive
                    ? 'bg-blue-50 text-blue-700 border border-blue-200'
                    : 'text-gray-600 hover:bg-gray-50 hover:text-gray-900'
                }`}
              >
                <Icon size={20} />
                <div>
                  <div className="font-medium">{tab.label}</div>
                  <div className="text-xs text-gray-500">{tab.description}</div>
                </div>
              </button>
            );
          })}
        </nav>
      </div>
    </div>
  );
} 