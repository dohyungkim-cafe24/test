'use client';

/**
 * Authentication guard component
 * @file AuthGuard.tsx
 * @feature F001 - User Authentication
 * @acceptance-criteria AC-005
 */

import React, { useEffect } from 'react';
import { useRouter, usePathname } from 'next/navigation';
import Box from '@mui/material/Box';
import CircularProgress from '@mui/material/CircularProgress';
import Typography from '@mui/material/Typography';
import { useAuth } from '@/lib/auth/hooks';

export interface AuthGuardProps {
  /** Protected content to render when authenticated */
  children: React.ReactNode;
  /** Redirect path when not authenticated (default: /login) */
  loginPath?: string;
  /** Loading component to show while checking auth */
  loadingComponent?: React.ReactNode;
}

/**
 * Default loading component
 */
function DefaultLoading() {
  return (
    <Box
      display="flex"
      flexDirection="column"
      alignItems="center"
      justifyContent="center"
      minHeight="100vh"
      gap={2}
    >
      <CircularProgress size={48} />
      <Typography variant="body2" color="text.secondary">
        Loading...
        <span style={{ marginLeft: 4 }}>로딩 중...</span>
      </Typography>
    </Box>
  );
}

/**
 * Authentication guard
 * Redirects to login page if user is not authenticated
 * Preserves original destination in redirect parameter
 */
export function AuthGuard({
  children,
  loginPath = '/login',
  loadingComponent,
}: AuthGuardProps) {
  const { isAuthenticated, isLoading } = useAuth();
  const router = useRouter();
  const pathname = usePathname();

  useEffect(() => {
    if (!isLoading && !isAuthenticated) {
      // Preserve original destination in redirect parameter
      const redirectParam = encodeURIComponent(pathname);
      router.replace(`${loginPath}?redirect=${redirectParam}`);
    }
  }, [isAuthenticated, isLoading, pathname, router, loginPath]);

  // Show loading state while checking authentication
  if (isLoading) {
    return <>{loadingComponent || <DefaultLoading />}</>;
  }

  // Don't render children until authenticated
  if (!isAuthenticated) {
    return <>{loadingComponent || <DefaultLoading />}</>;
  }

  return <>{children}</>;
}
