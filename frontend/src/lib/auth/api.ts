/**
 * Authentication API client
 * @file api.ts
 * @feature F001 - User Authentication
 */

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api/v1';

/**
 * Token response from refresh endpoint
 */
export interface TokenResponse {
  access_token: string;
  token_type: string;
  expires_in: number;
}

/**
 * User profile from /auth/me endpoint
 */
export interface UserProfile {
  id: string;
  email: string;
  name: string | null;
  provider: 'kakao' | 'google';
  avatar_url: string | null;
  created_at: string;
  body_specs?: {
    height_cm: number | null;
    weight_kg: number | null;
    experience_level: string | null;
    stance: string | null;
  } | null;
}

/**
 * Get Kakao OAuth redirect URL
 * @param redirectPath - Path to redirect after successful auth
 */
export function getKakaoAuthUrl(redirectPath?: string): string {
  const params = new URLSearchParams();
  if (redirectPath) {
    params.set('redirect_uri', redirectPath);
  }
  const queryString = params.toString();
  return `${API_BASE_URL}/auth/kakao${queryString ? `?${queryString}` : ''}`;
}

/**
 * Get Google OAuth redirect URL
 * @param redirectPath - Path to redirect after successful auth
 */
export function getGoogleAuthUrl(redirectPath?: string): string {
  const params = new URLSearchParams();
  if (redirectPath) {
    params.set('redirect_uri', redirectPath);
  }
  const queryString = params.toString();
  return `${API_BASE_URL}/auth/google${queryString ? `?${queryString}` : ''}`;
}

/**
 * Refresh access token using refresh token cookie
 * @returns New token response or null if refresh failed
 */
export async function refreshToken(): Promise<TokenResponse | null> {
  try {
    const response = await fetch(`${API_BASE_URL}/auth/refresh`, {
      method: 'POST',
      credentials: 'include', // Include cookies
    });

    if (!response.ok) {
      return null;
    }

    return response.json();
  } catch (error) {
    console.error('Token refresh failed:', error);
    return null;
  }
}

/**
 * Get current user profile
 * @param accessToken - JWT access token
 * @returns User profile or null if not authenticated
 */
export async function getCurrentUser(accessToken: string): Promise<UserProfile | null> {
  try {
    const response = await fetch(`${API_BASE_URL}/auth/me`, {
      headers: {
        Authorization: `Bearer ${accessToken}`,
      },
    });

    if (!response.ok) {
      return null;
    }

    return response.json();
  } catch (error) {
    console.error('Get user failed:', error);
    return null;
  }
}

/**
 * Logout user and clear session
 * @returns True if logout successful
 */
export async function logout(): Promise<boolean> {
  try {
    const response = await fetch(`${API_BASE_URL}/auth/logout`, {
      method: 'POST',
      credentials: 'include',
    });

    return response.ok;
  } catch (error) {
    console.error('Logout failed:', error);
    return false;
  }
}
