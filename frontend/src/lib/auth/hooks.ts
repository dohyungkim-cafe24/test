'use client';

/**
 * Authentication hooks
 * @file hooks.ts
 * @feature F001 - User Authentication
 */

import { useContext } from 'react';
import { AuthContext, AuthContextValue } from './context';

/**
 * Hook to access authentication state and methods
 * @returns Authentication context value
 * @throws Error if used outside AuthProvider
 */
export function useAuth(): AuthContextValue {
  const context = useContext(AuthContext);

  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }

  return context;
}

/**
 * Hook to check if user is authenticated
 * @returns True if user is authenticated, false otherwise
 */
export function useIsAuthenticated(): boolean {
  const { isAuthenticated, isLoading } = useAuth();
  return !isLoading && isAuthenticated;
}

/**
 * Hook to get current user
 * @returns Current user or null if not authenticated
 */
export function useUser() {
  const { user, isLoading } = useAuth();
  return { user, isLoading };
}
