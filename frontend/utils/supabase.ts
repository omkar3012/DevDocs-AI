import { createClient } from '@supabase/supabase-js';

const supabaseUrl = process.env.NEXT_PUBLIC_SUPABASE_URL!;
const supabaseAnonKey = process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY!;

export const supabase = createClient(supabaseUrl, supabaseAnonKey);

// Storage utility functions
export const storage = {
  // Upload file to Supabase storage
  uploadFile: async (file: File, userId: string, docId: string) => {
    const fileExt = file.name.split('.').pop();
    const fileName = `${docId}.${fileExt}`;
    const filePath = `documents/${userId}/${fileName}`;

    const { data, error } = await supabase.storage
      .from('api-docs')
      .upload(filePath, file, {
        cacheControl: '3600',
        upsert: false
      });

    if (error) {
      throw new Error(`Upload failed: ${error.message}`);
    }

    return { data, filePath };
  },

  // Get file URL
  getFileUrl: (filePath: string) => {
    const { data } = supabase.storage
      .from('api-docs')
      .getPublicUrl(filePath);
    
    return data.publicUrl;
  },

  // Delete file from storage
  deleteFile: async (filePath: string) => {
    const { error } = await supabase.storage
      .from('api-docs')
      .remove([filePath]);

    if (error) {
      throw new Error(`Delete failed: ${error.message}`);
    }
  },

  // List files for a user
  listUserFiles: async (userId: string) => {
    const { data, error } = await supabase.storage
      .from('api-docs')
      .list(`documents/${userId}`);

    if (error) {
      throw new Error(`List failed: ${error.message}`);
    }

    return data;
  }
};

// Database utility functions
export const db = {
  // Insert document metadata
  insertDocument: async (documentData: {
    id: string;
    name: string;
    version?: string;
    type: string;
    storage_path: string;
    user_id: string;
  }) => {
    const { data, error } = await supabase
      .from('api_documents')
      .insert(documentData)
      .select()
      .single();

    if (error) {
      throw new Error(`Database insert failed: ${error.message}`);
    }

    return data;
  },

  // Get documents for user
  getDocuments: async (userId: string) => {
    const { data, error } = await supabase
      .from('api_documents')
      .select('*')
      .eq('user_id', userId)
      .order('created_at', { ascending: false });

    if (error) {
      throw new Error(`Database query failed: ${error.message}`);
    }

    return data || [];
  },

  // Delete document
  deleteDocument: async (docId: string, userId: string) => {
    const { error } = await supabase
      .from('api_documents')
      .delete()
      .eq('id', docId)
      .eq('user_id', userId);

    if (error) {
      throw new Error(`Database delete failed: ${error.message}`);
    }
  }
}; 