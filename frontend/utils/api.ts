// API configuration for DevDocs AI
const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'https://devdocs-ai.onrender.com';

export const apiConfig = {
  baseUrl: API_BASE_URL,
  endpoints: {
    upload: `${API_BASE_URL}/upload`,
    ask: `${API_BASE_URL}/ask`,
    askStream: `${API_BASE_URL}/ask/stream`,
    documents: `${API_BASE_URL}/documents`,
    feedback: `${API_BASE_URL}/feedback`,
    search: `${API_BASE_URL}/search`,
    analytics: `${API_BASE_URL}/analytics`,
    status: `${API_BASE_URL}/status`,
  }
};

// Helper function to make API calls
export const apiCall = async (endpoint: string, options: RequestInit = {}) => {
  const url = `${API_BASE_URL}${endpoint}`;
  
  const response = await fetch(url, {
    ...options,
    headers: {
      'Content-Type': 'application/json',
      ...options.headers,
    },
  });

  if (!response.ok) {
    throw new Error(`API call failed: ${response.statusText}`);
  }

  return response.json();
};

// Specific API functions
export const api = {
  // Upload document
  uploadDocument: async (formData: FormData) => {
    const response = await fetch(`${API_BASE_URL}/upload`, {
      method: 'POST',
      body: formData,
    });
    
    if (!response.ok) {
      throw new Error(`Upload failed: ${response.statusText}`);
    }
    
    return response.json();
  },

  // Ask question
  askQuestion: async (question: string, docId: string, userId: string) => {
    const response = await fetch(`${API_BASE_URL}/ask`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        question,
        doc_id: docId,
        user_id: userId,
      }),
    });

    if (!response.ok) {
      throw new Error(`Failed to get answer: ${response.statusText}`);
    }

    return response.json();
  },

  // Get documents for user (from backend - for processing status)
  getDocuments: async (userId: string) => {
    const response = await fetch(`${API_BASE_URL}/documents/${userId}`);
    
    if (!response.ok) {
      throw new Error(`Failed to fetch documents: ${response.statusText}`);
    }
    
    return response.json();
  },

  // Check document processing status
  checkDocumentStatus: async (docId: string) => {
    const response = await fetch(`${API_BASE_URL}/status/${docId}`);
    
    if (!response.ok) {
      throw new Error(`Failed to check document status: ${response.statusText}`);
    }
    
    return response.json();
  },

  // Process document manually
  processDocument: async (docId: string) => {
    const response = await fetch(`${API_BASE_URL}/process/${docId}`, {
      method: 'POST',
    });
    
    if (!response.ok) {
      throw new Error(`Failed to process document: ${response.statusText}`);
    }
    
    return response.json();
  },

  // Submit feedback
  submitFeedback: async (feedback: {
    query: string;
    answer: string;
    wasHelpful: boolean;
    notes?: string;
    docId?: string;
    userId?: string;
  }) => {
    const response = await fetch(`${API_BASE_URL}/feedback`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        query: feedback.query,
        answer: feedback.answer,
        was_helpful: feedback.wasHelpful,
        notes: feedback.notes,
        doc_id: feedback.docId,
        user_id: feedback.userId,
      }),
    });

    if (!response.ok) {
      throw new Error(`Failed to submit feedback: ${response.statusText}`);
    }

    return response.json();
  },

  // Search chunks
  searchChunks: async (docId: string, query: string, limit: number = 10) => {
    const response = await fetch(`${API_BASE_URL}/search/${docId}?query=${encodeURIComponent(query)}&limit=${limit}`);
    
    if (!response.ok) {
      throw new Error(`Search failed: ${response.statusText}`);
    }
    
    return response.json();
  },

  // Get analytics
  getAnalytics: async (userId: string) => {
    const response = await fetch(`${API_BASE_URL}/analytics/${userId}`);
    
    if (!response.ok) {
      throw new Error(`Failed to get analytics: ${response.statusText}`);
    }
    
    return response.json();
  },

  // Debug: Force process all documents
  debugProcessAllDocuments: async (userId: string) => {
    const response = await fetch(`${API_BASE_URL}/debug/process-all/${userId}`, {
      method: 'POST',
    });
    
    if (!response.ok) {
      throw new Error(`Failed to debug process documents: ${response.statusText}`);
    }
    
    return response.json();
  },
}; 