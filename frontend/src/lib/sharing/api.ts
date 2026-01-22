/**
 * Sharing API client
 * @file api.ts
 * @feature F009 - Report Sharing
 *
 * Implements:
 * - AC-049: Share button shows on report page (default private)
 * - AC-050: Enable sharing generates unique URL
 * - AC-051: Shared URL accessible without authentication
 * - AC-052: Copy Link copies to clipboard with confirmation
 * - AC-054: Disabling sharing invalidates the URL
 * - AC-055: Re-enabling generates new unique URL
 */

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api/v1';

/** Share status response */
export interface ShareStatusResponse {
  share_enabled: boolean;
  share_token: string | null;
  share_url: string | null;
}

/** Share enabled response */
export interface ShareEnabledResponse {
  share_enabled: boolean;
  share_token: string;
  share_url: string;
  created_at: string;
}

/** Share disabled response */
export interface ShareDisabledResponse {
  share_enabled: boolean;
  message: string;
}

/** Shared report response (public access) */
export interface SharedReportResponse {
  id: string;
  performance_score: number | null;
  overall_assessment: string;
  strengths: Array<{
    title: string;
    description: string;
    metric_reference: string | null;
  }>;
  weaknesses: Array<{
    title: string;
    description: string;
    metric_reference: string | null;
  }>;
  recommendations: Array<{
    title: string;
    description: string;
    priority: 'high' | 'medium' | 'low';
    drill_type: string | null;
  }>;
  metrics: Record<string, {
    value: number;
    unit: string;
    benchmark_min: number | null;
    benchmark_max: number | null;
    percentile: number | null;
  }>;
  stamps: Array<{
    stamp_id: string;
    timestamp_seconds: number;
    frame_number: number;
    action_type: string;
    side: string;
    confidence: number;
    thumbnail_key: string | null;
  }>;
  disclaimer: string;
  created_at: string | null;
}

/** Sharing API error */
export class SharingError extends Error {
  constructor(
    message: string,
    public readonly code: string,
    public readonly statusCode?: number
  ) {
    super(message);
    this.name = 'SharingError';
  }
}

/**
 * Get share status for a report
 *
 * AC-049: Share button shows on report page (default private)
 *
 * @param accessToken - Bearer token for authentication
 * @param reportId - UUID of the report
 * @returns Share status with token and URL if enabled
 */
export async function getShareStatus(
  accessToken: string,
  reportId: string
): Promise<ShareStatusResponse> {
  const response = await fetch(
    `${API_BASE_URL}/reports/${reportId}/share`,
    {
      headers: {
        Authorization: `Bearer ${accessToken}`,
      },
    }
  );

  if (response.status === 404) {
    throw new SharingError('Report not found', 'REPORT_NOT_FOUND', 404);
  }

  if (response.status === 401) {
    throw new SharingError('Not authenticated', 'UNAUTHORIZED', 401);
  }

  if (response.status === 403) {
    throw new SharingError('Not authorized', 'FORBIDDEN', 403);
  }

  if (!response.ok) {
    const error = await response.json().catch(() => ({}));
    throw new SharingError(
      error.detail || 'Failed to get share status',
      'FETCH_FAILED',
      response.status
    );
  }

  return response.json();
}

/**
 * Enable sharing for a report
 *
 * AC-050: Enable sharing generates unique URL
 * AC-055: Re-enabling generates new unique URL
 *
 * @param accessToken - Bearer token for authentication
 * @param reportId - UUID of the report
 * @returns Share enabled response with token and URL
 */
export async function enableSharing(
  accessToken: string,
  reportId: string
): Promise<ShareEnabledResponse> {
  const response = await fetch(
    `${API_BASE_URL}/reports/${reportId}/share`,
    {
      method: 'POST',
      headers: {
        Authorization: `Bearer ${accessToken}`,
      },
    }
  );

  if (response.status === 404) {
    throw new SharingError('Report not found', 'REPORT_NOT_FOUND', 404);
  }

  if (response.status === 401) {
    throw new SharingError('Not authenticated', 'UNAUTHORIZED', 401);
  }

  if (response.status === 403) {
    throw new SharingError('Not authorized', 'FORBIDDEN', 403);
  }

  if (!response.ok) {
    const error = await response.json().catch(() => ({}));
    throw new SharingError(
      error.detail || 'Failed to enable sharing',
      'ENABLE_FAILED',
      response.status
    );
  }

  return response.json();
}

/**
 * Disable sharing for a report
 *
 * AC-054: Disabling sharing invalidates the URL
 *
 * @param accessToken - Bearer token for authentication
 * @param reportId - UUID of the report
 * @returns Share disabled response
 */
export async function disableSharing(
  accessToken: string,
  reportId: string
): Promise<ShareDisabledResponse> {
  const response = await fetch(
    `${API_BASE_URL}/reports/${reportId}/share`,
    {
      method: 'DELETE',
      headers: {
        Authorization: `Bearer ${accessToken}`,
      },
    }
  );

  if (response.status === 404) {
    throw new SharingError('Report not found', 'REPORT_NOT_FOUND', 404);
  }

  if (response.status === 401) {
    throw new SharingError('Not authenticated', 'UNAUTHORIZED', 401);
  }

  if (response.status === 403) {
    throw new SharingError('Not authorized', 'FORBIDDEN', 403);
  }

  if (!response.ok) {
    const error = await response.json().catch(() => ({}));
    throw new SharingError(
      error.detail || 'Failed to disable sharing',
      'DISABLE_FAILED',
      response.status
    );
  }

  return response.json();
}

/**
 * Get a shared report via public token
 *
 * AC-051: Shared URL accessible without authentication
 *
 * @param shareToken - 8-character share token
 * @returns Shared report data
 */
export async function getSharedReport(
  shareToken: string
): Promise<SharedReportResponse> {
  const response = await fetch(
    `${API_BASE_URL}/shared/${shareToken}`
  );

  if (response.status === 404) {
    throw new SharingError('Share link not found', 'SHARE_NOT_FOUND', 404);
  }

  if (response.status === 403) {
    throw new SharingError(
      'Sharing disabled for this report',
      'SHARE_DISABLED',
      403
    );
  }

  if (!response.ok) {
    const error = await response.json().catch(() => ({}));
    throw new SharingError(
      error.detail || 'Failed to fetch shared report',
      'FETCH_FAILED',
      response.status
    );
  }

  return response.json();
}

/**
 * Copy text to clipboard
 *
 * AC-052: Copy Link copies to clipboard with confirmation
 *
 * @param text - Text to copy
 * @returns Promise that resolves when copied
 */
export async function copyToClipboard(text: string): Promise<void> {
  if (navigator.clipboard && navigator.clipboard.writeText) {
    return navigator.clipboard.writeText(text);
  }

  // Fallback for older browsers
  const textArea = document.createElement('textarea');
  textArea.value = text;
  textArea.style.position = 'fixed';
  textArea.style.left = '-999999px';
  textArea.style.top = '-999999px';
  document.body.appendChild(textArea);
  textArea.focus();
  textArea.select();

  return new Promise((resolve, reject) => {
    const result = document.execCommand('copy');
    document.body.removeChild(textArea);
    if (result) {
      resolve();
    } else {
      reject(new Error('Failed to copy'));
    }
  });
}
