/**
 * Next.js middleware for route protection
 * @file middleware.ts
 * @feature F001 - User Authentication
 * @acceptance-criteria AC-005
 */

import { NextResponse } from 'next/server';
import type { NextRequest } from 'next/server';

/**
 * Protected route patterns
 * Routes matching these patterns require authentication
 */
const PROTECTED_ROUTES = [
  '/dashboard',
  '/upload',
  '/analysis',
  '/report',
  '/settings',
];

/**
 * Public routes that authenticated users can access
 * But should redirect to dashboard if already logged in
 */
const AUTH_ROUTES = ['/login', '/'];

/**
 * Check if a path matches any protected route pattern
 */
function isProtectedRoute(pathname: string): boolean {
  return PROTECTED_ROUTES.some(
    (route) => pathname === route || pathname.startsWith(`${route}/`)
  );
}

/**
 * Check if a path is an auth route
 */
function isAuthRoute(pathname: string): boolean {
  return AUTH_ROUTES.includes(pathname);
}

/**
 * Middleware to handle route protection
 *
 * Note: This middleware performs client-side redirect hints.
 * The actual authentication check is done by AuthGuard on the client
 * because tokens are stored in localStorage (not accessible from middleware).
 *
 * For enhanced security, consider:
 * 1. Using HttpOnly cookies for the access token
 * 2. Implementing server-side session validation
 */
export function middleware(request: NextRequest) {
  const { pathname } = request.nextUrl;

  // Skip static files and API routes
  if (
    pathname.startsWith('/_next') ||
    pathname.startsWith('/api') ||
    pathname.includes('.')
  ) {
    return NextResponse.next();
  }

  // For protected routes, add a header to signal client-side auth check is needed
  if (isProtectedRoute(pathname)) {
    const response = NextResponse.next();
    response.headers.set('x-require-auth', 'true');
    return response;
  }

  return NextResponse.next();
}

/**
 * Matcher configuration
 * Exclude static files and Next.js internals
 */
export const config = {
  matcher: [
    /*
     * Match all request paths except:
     * - _next/static (static files)
     * - _next/image (image optimization files)
     * - favicon.ico (favicon file)
     * - public folder files
     */
    '/((?!_next/static|_next/image|favicon.ico|.*\\..*|api).*)',
  ],
};
