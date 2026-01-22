/**
 * Dashboard API client
 * @file api.ts
 * @feature F010 - Report History Dashboard
 *
 * Implements:
 * - AC-056: Dashboard lists reports sorted by date descending
 * - AC-057: List items show thumbnail, date, summary indicator
 * - AC-059: Delete report shows confirmation dialog
 * - AC-060: Empty state shows upload CTA
 */

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api/v1';

/**
 * Report list item for dashboard display
 *
 * AC-057: List items show thumbnail, date, summary indicator
 */
export interface ReportListItem {
  id: string;
  video_id: string;
  thumbnail_url: string | null;
  analyzed_at: string;
  key_moments_count: number;
  performance_score: number | null;
}

/**
 * Paginated report list response
 *
 * AC-056: Dashboard lists reports sorted by date descending
 */
export interface ReportListResponse {
  items: ReportListItem[];
  total: number;
  page: number;
  has_more: boolean;
}

/**
 * Delete report response with undo window info
 *
 * AC-059: Delete report shows confirmation dialog
 * BDD: Undo toast for 10 seconds
 */
export interface DeleteReportResponse {
  deleted: boolean;
  can_restore_until: string;
}

/**
 * Restore report response
 */
export interface RestoreReportResponse {
  restored: boolean;
}

/** Dashboard API error */
export class DashboardError extends Error {
  constructor(
    message: string,
    public readonly code: string,
    public readonly statusCode?: number
  ) {
    super(message);
    this.name = 'DashboardError';
  }
}

/**
 * Get paginated list of user's reports for dashboard
 *
 * AC-056: Reports sorted by date descending (newest first)
 * AC-057: Each item includes thumbnail, date, and key moments count
 *
 * @param accessToken - Bearer token for authentication
 * @param page - Page number (1-indexed)
 * @param limit - Number of items per page
 * @returns Paginated report list
 */
export async function getReportList(
  accessToken: string,
  page: number = 1,
  limit: number = 10
): Promise<ReportListResponse> {
  const response = await fetch(
    `${API_BASE_URL}/dashboard/reports?page=${page}&limit=${limit}`,
    {
      headers: {
        Authorization: `Bearer ${accessToken}`,
      },
    }
  );

  if (response.status === 401) {
    throw new DashboardError('Not authenticated', 'UNAUTHORIZED', 401);
  }

  if (!response.ok) {
    const error = await response.json().catch(() => ({}));
    throw new DashboardError(
      error.detail || 'Failed to fetch reports',
      'FETCH_FAILED',
      response.status
    );
  }

  return response.json();
}

/**
 * Delete a report (soft delete with undo support)
 *
 * AC-059: Delete report shows confirmation dialog
 * BDD: Undo toast for 10 seconds
 *
 * @param accessToken - Bearer token for authentication
 * @param reportId - UUID of the report to delete
 * @returns Deletion confirmation with restore window
 */
export async function deleteReport(
  accessToken: string,
  reportId: string
): Promise<DeleteReportResponse> {
  const response = await fetch(
    `${API_BASE_URL}/reports/${reportId}`,
    {
      method: 'DELETE',
      headers: {
        Authorization: `Bearer ${accessToken}`,
      },
    }
  );

  if (response.status === 404) {
    throw new DashboardError('Report not found', 'REPORT_NOT_FOUND', 404);
  }

  if (response.status === 401) {
    throw new DashboardError('Not authenticated', 'UNAUTHORIZED', 401);
  }

  if (response.status === 403) {
    throw new DashboardError('Not authorized to delete this report', 'FORBIDDEN', 403);
  }

  if (!response.ok) {
    const error = await response.json().catch(() => ({}));
    throw new DashboardError(
      error.detail || 'Failed to delete report',
      'DELETE_FAILED',
      response.status
    );
  }

  return response.json();
}

/**
 * Restore a deleted report (undo delete)
 *
 * BDD: User deletes report with undo toast (10 seconds)
 *
 * @param accessToken - Bearer token for authentication
 * @param reportId - UUID of the report to restore
 * @returns Restoration confirmation
 */
export async function restoreReport(
  accessToken: string,
  reportId: string
): Promise<RestoreReportResponse> {
  const response = await fetch(
    `${API_BASE_URL}/reports/${reportId}/restore`,
    {
      method: 'POST',
      headers: {
        Authorization: `Bearer ${accessToken}`,
      },
    }
  );

  if (response.status === 404) {
    throw new DashboardError('Report not found', 'REPORT_NOT_FOUND', 404);
  }

  if (response.status === 401) {
    throw new DashboardError('Not authenticated', 'UNAUTHORIZED', 401);
  }

  if (response.status === 403) {
    throw new DashboardError('Not authorized to restore this report', 'FORBIDDEN', 403);
  }

  if (response.status === 400) {
    throw new DashboardError('Restore window has expired', 'RESTORE_EXPIRED', 400);
  }

  if (!response.ok) {
    const error = await response.json().catch(() => ({}));
    throw new DashboardError(
      error.detail || 'Failed to restore report',
      'RESTORE_FAILED',
      response.status
    );
  }

  return response.json();
}

/**
 * Format date for display as "Analyzed on {date}"
 *
 * BDD: The date should be formatted as "Analyzed on {date}"
 *
 * @param isoDate - ISO date string
 * @returns Formatted date string
 */
export function formatAnalyzedDate(isoDate: string): string {
  const date = new Date(isoDate);
  return date.toLocaleDateString('en-US', {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
  });
}
