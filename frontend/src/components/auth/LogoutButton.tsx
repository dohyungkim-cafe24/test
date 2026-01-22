'use client';

/**
 * Logout button component
 * @file LogoutButton.tsx
 * @feature F001 - User Authentication
 * @acceptance-criteria AC-004
 */

import React from 'react';
import Button from '@mui/material/Button';
import LogoutIcon from '@mui/icons-material/Logout';
import { useAuth } from '@/lib/auth/hooks';
import { useRouter } from 'next/navigation';

export interface LogoutButtonProps {
  /** Button variant */
  variant?: 'text' | 'outlined' | 'contained';
  /** Button size */
  size?: 'small' | 'medium' | 'large';
  /** Show icon */
  showIcon?: boolean;
  /** Custom class name */
  className?: string;
}

/**
 * Logout button
 * Terminates session and redirects to landing page
 */
export function LogoutButton({
  variant = 'text',
  size = 'medium',
  showIcon = true,
  className,
}: LogoutButtonProps) {
  const { logout } = useAuth();
  const router = useRouter();

  const handleLogout = async () => {
    await logout();
    router.push('/');
  };

  return (
    <Button
      variant={variant}
      size={size}
      onClick={handleLogout}
      startIcon={showIcon ? <LogoutIcon /> : undefined}
      className={className}
      sx={{
        textTransform: 'none',
      }}
    >
      Log out
      <span style={{ marginLeft: 4, fontSize: 12, opacity: 0.7 }}>
        로그아웃
      </span>
    </Button>
  );
}
