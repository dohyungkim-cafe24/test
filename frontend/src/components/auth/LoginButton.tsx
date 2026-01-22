'use client';

/**
 * OAuth login buttons component
 * @file LoginButton.tsx
 * @feature F001 - User Authentication
 * @acceptance-criteria AC-001, AC-002
 */

import React, { useState } from 'react';
import Button from '@mui/material/Button';
import CircularProgress from '@mui/material/CircularProgress';
import Stack from '@mui/material/Stack';
import { getKakaoAuthUrl, getGoogleAuthUrl, guestLogin } from '@/lib/auth/api';

/**
 * Kakao OAuth login icon
 */
function KakaoIcon() {
  return (
    <svg width="24" height="24" viewBox="0 0 24 24" fill="none">
      <path
        d="M12 3C6.48 3 2 6.58 2 11c0 2.8 1.86 5.25 4.64 6.64-.2.76-.73 2.74-.84 3.16-.13.52.19.51.4.37.17-.11 2.63-1.79 3.7-2.52.68.1 1.38.15 2.1.15 5.52 0 10-3.58 10-8s-4.48-8-10-8z"
        fill="#3C1E1E"
      />
    </svg>
  );
}

/**
 * Google OAuth login icon
 */
function GoogleIcon() {
  return (
    <svg width="24" height="24" viewBox="0 0 24 24">
      <path
        d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z"
        fill="#4285F4"
      />
      <path
        d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z"
        fill="#34A853"
      />
      <path
        d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.22.81-.62z"
        fill="#FBBC05"
      />
      <path
        d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z"
        fill="#EA4335"
      />
    </svg>
  );
}

export interface LoginButtonProps {
  /** Optional redirect path after successful login */
  redirectPath?: string;
}

/**
 * Kakao login button
 * Redirects to Kakao OAuth flow on click
 */
export function KakaoLoginButton({ redirectPath }: LoginButtonProps) {
  const handleClick = () => {
    window.location.href = getKakaoAuthUrl(redirectPath);
  };

  return (
    <Button
      variant="contained"
      fullWidth
      startIcon={<KakaoIcon />}
      onClick={handleClick}
      sx={{
        backgroundColor: '#FEE500',
        color: '#3C1E1E',
        '&:hover': {
          backgroundColor: '#FADA0A',
        },
        textTransform: 'none',
        fontWeight: 500,
        py: 1.5,
      }}
    >
      Continue with Kakao
      <span style={{ marginLeft: 8, fontSize: 12, opacity: 0.7 }}>
        카카오로 계속하기
      </span>
    </Button>
  );
}

/**
 * Google login button
 * Redirects to Google OAuth flow on click
 */
export function GoogleLoginButton({ redirectPath }: LoginButtonProps) {
  const handleClick = () => {
    window.location.href = getGoogleAuthUrl(redirectPath);
  };

  return (
    <Button
      variant="outlined"
      fullWidth
      startIcon={<GoogleIcon />}
      onClick={handleClick}
      sx={{
        borderColor: '#dadce0',
        color: '#3c4043',
        '&:hover': {
          backgroundColor: '#f8f9fa',
          borderColor: '#dadce0',
        },
        textTransform: 'none',
        fontWeight: 500,
        py: 1.5,
      }}
    >
      Continue with Google
      <span style={{ marginLeft: 8, fontSize: 12, opacity: 0.7 }}>
        Google로 계속하기
      </span>
    </Button>
  );
}

/**
 * Guest login button
 * Allows users to continue without authentication
 */
export function GuestLoginButton({ redirectPath }: LoginButtonProps) {
  const [isLoading, setIsLoading] = useState(false);

  const handleClick = async () => {
    setIsLoading(true);
    try {
      const response = await guestLogin();
      if (response?.access_token) {
        // Store the access token the same way OAuth callback does (URL fragment)
        // Navigate with the token in the URL fragment
        window.location.href = `${redirectPath || '/dashboard'}#access_token=${response.access_token}`;
      } else {
        console.error('Guest login failed: no token received');
        alert('Guest login failed. Please try again.');
      }
    } catch (error) {
      console.error('Guest login error:', error);
      alert('Guest login failed. Please try again.');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <Button
      variant="text"
      fullWidth
      onClick={handleClick}
      disabled={isLoading}
      sx={{
        color: 'text.secondary',
        textTransform: 'none',
        fontWeight: 400,
        py: 1.5,
        '&:hover': {
          backgroundColor: 'action.hover',
        },
      }}
    >
      {isLoading ? (
        <CircularProgress size={20} color="inherit" />
      ) : (
        <>
          Continue as Guest
          <span style={{ marginLeft: 8, fontSize: 12, opacity: 0.7 }}>
            비회원으로 계속하기
          </span>
        </>
      )}
    </Button>
  );
}

/**
 * Combined login buttons stack
 */
export function LoginButtons({ redirectPath }: LoginButtonProps) {
  return (
    <Stack spacing={2} sx={{ width: '100%', maxWidth: 360 }}>
      <KakaoLoginButton redirectPath={redirectPath} />
      <GoogleLoginButton redirectPath={redirectPath} />
      <GuestLoginButton redirectPath={redirectPath} />
    </Stack>
  );
}
