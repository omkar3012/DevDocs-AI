'use client';

import React, { useState, useEffect } from 'react';
import { createClient } from '@supabase/supabase-js';
import { Auth } from '@supabase/auth-ui-react';
import { ThemeSupa } from '@supabase/auth-ui-shared';
import Dashboard from '../components/Dashboard';
import toast from 'react-hot-toast';
import { sessionStorage } from '../utils/sessionStorage';

const supabaseUrl = process.env.NEXT_PUBLIC_SUPABASE_URL;
const supabaseAnonKey = process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY;

// Only create client if environment variables are available and not placeholder values
const supabase = (supabaseUrl && supabaseAnonKey && 
                 supabaseUrl !== 'your_supabase_url_here' && 
                 supabaseAnonKey !== 'your_supabase_anon_key_here')
  ? createClient(supabaseUrl, supabaseAnonKey)
  : null;

export default function Home() {
  const [session, setSession] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [isClient, setIsClient] = useState(false);

  // Check if we're on the client side
  useEffect(() => {
    setIsClient(true);
  }, []);

  useEffect(() => {
    if (!supabase) {
      setLoading(false);
      return;
    }

    // Check for existing session in localStorage (client-side only)
    if (isClient) {
      const storedSession = sessionStorage.getSession();
      if (storedSession) {
        setSession(storedSession);
        setLoading(false);
      }
    }

    // Get initial session from Supabase
    supabase.auth.getSession().then(({ data: { session } }) => {
      if (session && isClient) {
        // Store session in localStorage
        sessionStorage.setSession(session);
        setSession(session);
      } else if (session) {
        setSession(session);
      }
      setLoading(false);
    });

    // Listen for auth changes
    const {
      data: { subscription },
    } = supabase.auth.onAuthStateChange((_event, session) => {
      if (session && isClient) {
        // Store session in localStorage
        sessionStorage.setSession(session);
        toast.success('Welcome to DevDocs AI!');
      } else if (session) {
        toast.success('Welcome to DevDocs AI!');
      } else if (isClient) {
        // Clear session from localStorage on logout
        sessionStorage.clearSession();
      }
      setSession(session);
    });

    return () => subscription.unsubscribe();
  }, [supabase]);

  // Show loading while determining client-side status
  if (!isClient) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-blue-50 to-indigo-100">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto"></div>
          <p className="mt-4 text-gray-600">Initializing...</p>
        </div>
      </div>
    );
  }

  if (!supabase) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-blue-50 to-indigo-100">
        <div className="text-center">
          <div className="text-red-600 text-xl mb-4">⚠️ Configuration Error</div>
          <p className="text-gray-600">Missing Supabase environment variables. Please check your .env.local file.</p>
        </div>
      </div>
    );
  }

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-blue-50 to-indigo-100">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto"></div>
          <p className="mt-4 text-gray-600">Loading DevDocs AI...</p>
        </div>
      </div>
    );
  }

  if (!session) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 flex items-center justify-center p-4">
        <div className="max-w-md w-full bg-white rounded-lg shadow-lg p-8">
          <div className="text-center mb-8">
            <h1 className="text-3xl font-bold text-gray-900 mb-2">DevDocs AI</h1>
            <p className="text-gray-600">
              RAG-Powered Developer Documentation Assistant
            </p>
          </div>
          
          <Auth
            supabaseClient={supabase}
            appearance={{
              theme: ThemeSupa,
              variables: {
                default: {
                  colors: {
                    brand: '#3b82f6',
                    brandAccent: '#2563eb',
                  },
                },
              },
            }}
            providers={['github', 'google']}
            redirectTo={`${window.location.origin}/auth/callback`}
          />
          
          <div className="mt-8 text-center text-sm text-gray-500">
            <p>Upload API specs, SDK manuals, and ask questions naturally</p>
          </div>
        </div>
      </div>
    );
  }

  return <Dashboard session={session} supabase={supabase} />;
} 