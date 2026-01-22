/**
 * Report API client
 * @file api.ts
 * @feature F008 - Report Display
 *
 * Implements:
 * - AC-041: Summary section displays overall assessment
 * - AC-042: Strengths section shows 3-5 observations
 * - AC-043: Weaknesses section shows 3-5 improvement areas
 * - AC-044: Recommendations section shows 3-5 actionable items
 * - AC-045: Key moments section with timestamp links
 * - AC-046: Metrics displayed with visual indicators
 */

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api/v1';

/** Strength item from analysis */
export interface StrengthItem {
  title: string;
  description: string;
  metric_reference: string | null;
}

/** Weakness item from analysis */
export interface WeaknessItem {
  title: string;
  description: string;
  metric_reference: string | null;
}

/** Recommendation item from analysis */
export interface RecommendationItem {
  title: string;
  description: string;
  priority: 'high' | 'medium' | 'low';
  drill_type: string | null;
}

/** Metric value with benchmark data for visualization (AC-046) */
export interface MetricValue {
  value: number;
  unit: string;
  benchmark_min: number | null;
  benchmark_max: number | null;
  percentile: number | null;
}

/** Stamp (key moment) data (AC-045) */
export interface StampItem {
  stamp_id: string;
  timestamp_seconds: number;
  frame_number: number;
  action_type: string;
  side: string;
  confidence: number;
  thumbnail_key: string | null;
}

/** Full report response */
export interface ReportResponse {
  id: string;
  analysis_id: string;
  video_id: string;
  user_id: string;
  performance_score: number | null;
  overall_assessment: string;
  strengths: StrengthItem[];
  weaknesses: WeaknessItem[];
  recommendations: RecommendationItem[];
  metrics: Record<string, MetricValue>;
  stamps: StampItem[];
  llm_model: string | null;
  disclaimer: string;
  created_at: string;
  updated_at: string | null;
}

/** Report API error */
export class ReportError extends Error {
  constructor(
    message: string,
    public readonly code: string,
    public readonly statusCode?: number
  ) {
    super(message);
    this.name = 'ReportError';
  }
}

/**
 * Get report by ID
 *
 * AC-041 through AC-046: Full report with all sections
 *
 * @param accessToken - Bearer token for authentication
 * @param reportId - UUID of the report
 * @returns Full report data with all sections
 */
export async function getReport(
  accessToken: string,
  reportId: string
): Promise<ReportResponse> {
  const response = await fetch(
    `${API_BASE_URL}/reports/${reportId}`,
    {
      headers: {
        Authorization: `Bearer ${accessToken}`,
      },
    }
  );

  if (response.status === 404) {
    throw new ReportError('Report not found', 'REPORT_NOT_FOUND', 404);
  }

  if (response.status === 401) {
    throw new ReportError('Not authenticated', 'UNAUTHORIZED', 401);
  }

  if (response.status === 403) {
    throw new ReportError('Not authorized to view this report', 'FORBIDDEN', 403);
  }

  if (!response.ok) {
    const error = await response.json().catch(() => ({}));
    throw new ReportError(
      error.detail || 'Failed to fetch report',
      'FETCH_FAILED',
      response.status
    );
  }

  return response.json();
}

/**
 * Get report by analysis ID
 *
 * Useful for navigating to report after processing completes.
 *
 * @param accessToken - Bearer token for authentication
 * @param analysisId - UUID of the analysis
 * @returns Full report data
 */
export async function getReportByAnalysisId(
  accessToken: string,
  analysisId: string
): Promise<ReportResponse> {
  const response = await fetch(
    `${API_BASE_URL}/reports/by-analysis/${analysisId}`,
    {
      headers: {
        Authorization: `Bearer ${accessToken}`,
      },
    }
  );

  if (response.status === 404) {
    throw new ReportError('Report not found', 'REPORT_NOT_FOUND', 404);
  }

  if (response.status === 401) {
    throw new ReportError('Not authenticated', 'UNAUTHORIZED', 401);
  }

  if (response.status === 403) {
    throw new ReportError('Not authorized to view this report', 'FORBIDDEN', 403);
  }

  if (!response.ok) {
    const error = await response.json().catch(() => ({}));
    throw new ReportError(
      error.detail || 'Failed to fetch report',
      'FETCH_FAILED',
      response.status
    );
  }

  return response.json();
}

/**
 * Format timestamp seconds to display format (e.g., "1:23")
 *
 * AC-045: Timestamps should be in format "0:34"
 *
 * @param seconds - Timestamp in seconds
 * @returns Formatted string like "1:23"
 */
export function formatTimestamp(seconds: number): string {
  const mins = Math.floor(seconds / 60);
  const secs = Math.floor(seconds % 60);
  return `${mins}:${secs.toString().padStart(2, '0')}`;
}
