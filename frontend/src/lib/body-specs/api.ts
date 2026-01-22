/**
 * Body Specification API client
 * @file api.ts
 * @feature F004 - Body Specification Input
 *
 * Implements:
 * - AC-018: Form with height, weight, experience level, stance
 * - AC-019: Validation: height (100-250cm), weight (30-200kg)
 * - AC-024: Body specs pre-filled for returning users
 */

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api/v1';

/** Experience level options matching backend enum */
export type ExperienceLevel = 'beginner' | 'intermediate' | 'advanced' | 'competitive';

/** Stance options matching backend enum */
export type Stance = 'orthodox' | 'southpaw';

/** Request payload for creating body specifications */
export interface BodySpecsRequest {
  height_cm: number;
  weight_kg: number;
  experience_level: ExperienceLevel;
  stance: Stance;
}

/** Response after saving body specifications */
export interface BodySpecsResponse {
  video_id: string;
  body_specs_id: string;
  saved: boolean;
  persist_to_profile: boolean;
}

/** Pre-fill response for returning users (AC-024) */
export interface PrefillResponse {
  has_saved_specs: boolean;
  height_cm: number | null;
  weight_kg: number | null;
  experience_level: string | null;
  stance: string | null;
}

/** Body specs API error */
export class BodySpecsError extends Error {
  constructor(
    message: string,
    public readonly code: string,
    public readonly statusCode?: number
  ) {
    super(message);
    this.name = 'BodySpecsError';
  }
}

/**
 * Submit body specifications for a video
 *
 * AC-018: Form with height, weight, experience level, stance
 * AC-019: Validation: height (100-250cm), weight (30-200kg)
 *
 * @param accessToken - Bearer token for authentication
 * @param videoId - UUID of the video
 * @param data - Body specifications to submit
 * @returns Response with body specs ID and save status
 */
export async function submitBodySpecs(
  accessToken: string,
  videoId: string,
  data: BodySpecsRequest
): Promise<BodySpecsResponse> {
  const response = await fetch(
    `${API_BASE_URL}/analysis/body-specs/${videoId}`,
    {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        Authorization: `Bearer ${accessToken}`,
      },
      body: JSON.stringify(data),
    }
  );

  if (response.status === 404) {
    throw new BodySpecsError('Video not found', 'VIDEO_NOT_FOUND', 404);
  }

  if (response.status === 401) {
    throw new BodySpecsError('Not authenticated', 'UNAUTHORIZED', 401);
  }

  if (response.status === 422) {
    const error = await response.json().catch(() => ({}));
    throw new BodySpecsError(
      error.detail || 'Validation error',
      'VALIDATION_ERROR',
      422
    );
  }

  if (!response.ok) {
    const error = await response.json().catch(() => ({}));
    throw new BodySpecsError(
      error.detail || 'Failed to save body specs',
      'SAVE_FAILED',
      response.status
    );
  }

  return response.json();
}

/**
 * Get pre-fill data for returning users
 *
 * AC-024: Body specs pre-filled for returning users
 *
 * @param accessToken - Bearer token for authentication
 * @returns Pre-fill data with previously saved specs (if any)
 */
export async function getPrefillSpecs(
  accessToken: string
): Promise<PrefillResponse> {
  const response = await fetch(
    `${API_BASE_URL}/analysis/body-specs/prefill`,
    {
      headers: {
        Authorization: `Bearer ${accessToken}`,
      },
    }
  );

  if (response.status === 401) {
    throw new BodySpecsError('Not authenticated', 'UNAUTHORIZED', 401);
  }

  if (!response.ok) {
    const error = await response.json().catch(() => ({}));
    throw new BodySpecsError(
      error.detail || 'Failed to get prefill data',
      'PREFILL_FAILED',
      response.status
    );
  }

  return response.json();
}

/** Response from running analysis */
export interface AnalysisResponse {
  report_id: string;
  video_id: string;
  performance_score: number;
  message: string;
}

/**
 * Run boxing analysis on a video
 *
 * Calls the synchronous analysis endpoint which:
 * 1. Extracts frames from video
 * 2. Runs MediaPipe pose estimation
 * 3. Analyzes with GPT
 * 4. Returns a report
 *
 * @param accessToken - Bearer token for authentication
 * @param videoId - UUID of the video to analyze
 * @returns Analysis result with report ID
 */
export async function runAnalysis(
  accessToken: string,
  videoId: string
): Promise<AnalysisResponse> {
  const response = await fetch(
    `${API_BASE_URL}/analysis/run/${videoId}`,
    {
      method: 'POST',
      headers: {
        Authorization: `Bearer ${accessToken}`,
      },
    }
  );

  if (response.status === 404) {
    throw new BodySpecsError('Video not found', 'VIDEO_NOT_FOUND', 404);
  }

  if (response.status === 401) {
    throw new BodySpecsError('Not authenticated', 'UNAUTHORIZED', 401);
  }

  if (!response.ok) {
    const error = await response.json().catch(() => ({}));
    throw new BodySpecsError(
      error.detail || 'Analysis failed',
      'ANALYSIS_FAILED',
      response.status
    );
  }

  return response.json();
}
