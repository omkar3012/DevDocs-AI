/**
 * Session storage utilities for DevDocs AI
 * Handles storing and retrieving user session data from localStorage
 */

const SESSION_KEY = 'devdocs-session';

export interface StoredSession {
  access_token: string;
  refresh_token: string;
  user: {
    id: string;
    email: string;
    user_metadata?: any;
  };
  expires_at?: number;
}

export const sessionStorage = {
  /**
   * Store session data in localStorage
   */
  setSession: (session: any): void => {
    if (typeof window === 'undefined') return;
    
    try {
      localStorage.setItem(SESSION_KEY, JSON.stringify(session));
    } catch (error) {
      console.error('Error storing session:', error);
    }
  },

  /**
   * Retrieve session data from localStorage
   */
  getSession: (): StoredSession | null => {
    if (typeof window === 'undefined') return null;
    
    try {
      const stored = localStorage.getItem(SESSION_KEY);
      if (!stored) return null;
      
      const session = JSON.parse(stored);
      return session;
    } catch (error) {
      console.error('Error retrieving session:', error);
      sessionStorage.clearSession();
      return null;
    }
  },

  /**
   * Clear session data from localStorage
   */
  clearSession: (): void => {
    if (typeof window === 'undefined') return;
    
    try {
      localStorage.removeItem(SESSION_KEY);
    } catch (error) {
      console.error('Error clearing session:', error);
    }
  },

  /**
   * Check if session exists and is valid
   */
  hasValidSession: (): boolean => {
    const session = sessionStorage.getSession();
    if (!session) return false;
    
    // Check if session has expired
    if (session.expires_at && Date.now() > session.expires_at * 1000) {
      sessionStorage.clearSession();
      return false;
    }
    
    return true;
  }
}; 