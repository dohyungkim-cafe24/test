'use client';

/**
 * Login page
 * @file page.tsx
 * @feature F001 - User Authentication
 */

import React, { Suspense, useEffect } from 'react';
import Box from '@mui/material/Box';
import Container from '@mui/material/Container';
import Typography from '@mui/material/Typography';
import Alert from '@mui/material/Alert';
import Paper from '@mui/material/Paper';
import CircularProgress from '@mui/material/CircularProgress';
import { useRouter, useSearchParams } from 'next/navigation';
import { LoginButtons } from '@/components/auth/LoginButton';
import { useAuth } from '@/lib/auth/hooks';

function LoginContent() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const { isAuthenticated, isLoading } = useAuth();

  // Get redirect path and error from query params
  const redirectPath = searchParams.get('redirect') || '/dashboard';
  const error = searchParams.get('error');
  const errorDescription = searchParams.get('error_description');

  // Redirect to dashboard (or original destination) if already authenticated
  useEffect(() => {
    if (!isLoading && isAuthenticated) {
      router.push(decodeURIComponent(redirectPath));
    }
  }, [isAuthenticated, isLoading, router, redirectPath]);

  // Map error codes to user-friendly messages
  const getErrorMessage = (errorCode: string | null): string | null => {
    if (!errorCode) return null;

    const errorMessages: Record<string, string> = {
      access_denied: 'Login cancelled. Please try again.',
      cancelled: 'Login cancelled. Please try again.',
      oauth_error: 'Authentication failed. Please try again.',
      invalid_state: 'Security validation failed. Please try again.',
    };

    return (
      errorMessages[errorCode] ||
      errorDescription ||
      'An error occurred. Please try again.'
    );
  };

  const errorMessage = getErrorMessage(error);

  return (
    <Paper
      elevation={0}
      sx={{
        p: 4,
        display: 'flex',
        flexDirection: 'column',
        alignItems: 'center',
        borderRadius: 3,
        border: '1px solid',
        borderColor: 'divider',
      }}
    >
      {/* Logo / Title */}
      <Typography
        variant="h4"
        component="h1"
        gutterBottom
        sx={{ color: 'primary.main', fontWeight: 700 }}
      >
        PunchAnalytics
      </Typography>

      <Typography
        variant="body1"
        color="text.secondary"
        sx={{ mb: 4, textAlign: 'center' }}
      >
        Sign in to analyze your boxing technique
        <br />
        <span style={{ fontSize: '0.9em' }}>
          로그인하여 복싱 기술을 분석하세요
        </span>
      </Typography>

      {/* Error Alert */}
      {errorMessage && (
        <Alert severity="error" sx={{ mb: 3, width: '100%' }}>
          {errorMessage}
          <br />
          <span style={{ fontSize: '0.85em' }}>
            {error === 'cancelled' || error === 'access_denied'
              ? '로그인이 취소되었습니다. 다시 시도해주세요.'
              : '오류가 발생했습니다. 다시 시도해주세요.'}
          </span>
        </Alert>
      )}

      {/* Login Buttons */}
      <LoginButtons redirectPath={redirectPath} />

      {/* Footer */}
      <Typography
        variant="caption"
        color="text.secondary"
        sx={{ mt: 4, textAlign: 'center' }}
      >
        By signing in, you agree to our Terms of Service and Privacy Policy.
        <br />
        <span style={{ opacity: 0.8 }}>
          로그인하면 서비스 약관 및 개인정보 처리방침에 동의하는 것입니다.
        </span>
      </Typography>
    </Paper>
  );
}

function LoginFallback() {
  return (
    <Paper
      elevation={0}
      sx={{
        p: 4,
        display: 'flex',
        flexDirection: 'column',
        alignItems: 'center',
        borderRadius: 3,
        border: '1px solid',
        borderColor: 'divider',
        minHeight: 300,
        justifyContent: 'center',
      }}
    >
      <CircularProgress />
    </Paper>
  );
}

export default function LoginPage() {
  return (
    <Box
      sx={{
        minHeight: '100vh',
        display: 'flex',
        flexDirection: 'column',
        alignItems: 'center',
        justifyContent: 'center',
        backgroundColor: 'background.default',
        px: 2,
      }}
    >
      <Container maxWidth="sm">
        <Suspense fallback={<LoginFallback />}>
          <LoginContent />
        </Suspense>
      </Container>
    </Box>
  );
}
