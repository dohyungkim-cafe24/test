/**
 * Subject Selection API client
 * @file api.ts
 * @feature F003 - Subject Selection
 *
 * Implements:
 * - AC-013: Thumbnail grid displays after upload completes
 * - AC-014: Tap on person highlights with selection indicator
 * - AC-015: Confirm selection stores bounding box for tracking
 * - AC-016: Selection can be changed before confirmation
 * - AC-017: Single person auto-selected with confirm option
 */

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api/v1';

/** Bounding box coordinates for detected person */
export interface BoundingBox {
  x: number;
  y: number;
  width: number;
  height: number;
}

/** A person detected in a thumbnail frame */
export interface DetectedPerson {
  person_id: string;
  bounding_box: BoundingBox;
  confidence: number;
}

/** Single thumbnail with detected persons */
export interface ThumbnailResponse {
  thumbnail_id: string;
  frame_number: number;
  timestamp_seconds: number;
  image_url: string;
  detected_persons: DetectedPerson[];
}

/** Auto-selection info for single-person videos */
export interface AutoSelectInfo {
  thumbnail_id: string;
  person_id: string;
  bounding_box: BoundingBox;
}

/** Processing status for thumbnails */
export type ThumbnailStatus = 'processing' | 'ready' | 'no_subjects' | 'failed';

/** Response for thumbnails endpoint */
export interface ThumbnailsResponse {
  video_id: string;
  status: ThumbnailStatus;
  total_persons_detected: number;
  thumbnails: ThumbnailResponse[];
  auto_select: AutoSelectInfo | null;
  message: string | null;
}

/** Request to select analysis subject */
export interface SubjectSelectRequest {
  thumbnail_id: string;
  person_id: string;
}

/** Response after subject selection */
export interface SubjectSelectResponse {
  subject_id: string;
  video_id: string;
  person_id: string;
  bounding_box: BoundingBox;
  auto_selected: boolean;
}

/** Subject selection error */
export class SubjectError extends Error {
  constructor(
    message: string,
    public readonly code: string,
    public readonly statusCode?: number
  ) {
    super(message);
    this.name = 'SubjectError';
  }
}

/**
 * Get extracted thumbnails for subject selection
 *
 * AC-013: Thumbnail grid displays after upload completes
 * AC-017: Single person auto-selected with confirm option
 *
 * @param accessToken - Bearer token for authentication
 * @param videoId - UUID of the uploaded video
 * @returns Thumbnails response with detected persons
 */
export async function getThumbnails(
  accessToken: string,
  videoId: string
): Promise<ThumbnailsResponse> {
  const response = await fetch(
    `${API_BASE_URL}/analysis/thumbnails/${videoId}`,
    {
      headers: {
        Authorization: `Bearer ${accessToken}`,
      },
    }
  );

  if (response.status === 404) {
    throw new SubjectError('Video not found', 'VIDEO_NOT_FOUND', 404);
  }

  if (response.status === 401) {
    throw new SubjectError('Not authenticated', 'UNAUTHORIZED', 401);
  }

  if (!response.ok) {
    const error = await response.json().catch(() => ({}));
    throw new SubjectError(
      error.detail || 'Failed to get thumbnails',
      'THUMBNAILS_FAILED',
      response.status
    );
  }

  return response.json();
}

/**
 * Select analysis subject from thumbnail
 *
 * AC-014: Tap on person highlights with selection indicator
 * AC-015: Confirm selection stores bounding box for tracking
 * AC-016: Selection can be changed before confirmation
 *
 * @param accessToken - Bearer token for authentication
 * @param videoId - UUID of the video
 * @param thumbnailId - UUID of the thumbnail where selection was made
 * @param personId - ID of the selected person
 * @returns Subject selection response with created subject ID
 */
export async function selectSubject(
  accessToken: string,
  videoId: string,
  thumbnailId: string,
  personId: string
): Promise<SubjectSelectResponse> {
  const response = await fetch(
    `${API_BASE_URL}/analysis/subject/${videoId}`,
    {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        Authorization: `Bearer ${accessToken}`,
      },
      body: JSON.stringify({
        thumbnail_id: thumbnailId,
        person_id: personId,
      } as SubjectSelectRequest),
    }
  );

  if (response.status === 404) {
    const error = await response.json().catch(() => ({}));
    throw new SubjectError(
      error.detail || 'Resource not found',
      'NOT_FOUND',
      404
    );
  }

  if (response.status === 401) {
    throw new SubjectError('Not authenticated', 'UNAUTHORIZED', 401);
  }

  if (response.status === 409) {
    throw new SubjectError(
      'Subject already selected',
      'SUBJECT_EXISTS',
      409
    );
  }

  if (!response.ok) {
    const error = await response.json().catch(() => ({}));
    throw new SubjectError(
      error.detail || 'Failed to select subject',
      'SELECT_FAILED',
      response.status
    );
  }

  return response.json();
}
