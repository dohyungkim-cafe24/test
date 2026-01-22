/**
 * Upload API client with chunked/resumable upload support
 * @file api.ts
 * @feature F002 - Video Upload
 *
 * Implements:
 * - AC-006: Valid video file upload with progress indicator
 * - AC-011: Network interruption resumes upload automatically
 * - AC-012: Cancel upload discards partial upload
 */

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api/v1';

/** Chunk size: 5MB */
export const CHUNK_SIZE = 5 * 1024 * 1024;

/** Maximum file size: 500MB */
export const MAX_FILE_SIZE = 500 * 1024 * 1024;

/** Minimum duration: 60 seconds */
export const MIN_DURATION = 60;

/** Maximum duration: 180 seconds */
export const MAX_DURATION = 180;

/** Allowed content types */
export const ALLOWED_CONTENT_TYPES = [
  'video/mp4',
  'video/quicktime',
  'video/webm',
] as const;

/** Upload initiation response */
export interface UploadInitiateResponse {
  upload_id: string;
  chunk_size: number;
  total_chunks: number;
  expires_at: string;
}

/** Chunk upload response */
export interface UploadChunkResponse {
  chunk_number: number;
  received_bytes: number;
  total_received: number;
  progress_percent: number;
}

/** Upload complete response */
export interface UploadCompleteResponse {
  video_id: string;
  status: 'processing_thumbnails' | 'ready' | 'failed';
  duration_seconds: number;
  file_size: number;
}

/** Upload status response */
export interface UploadStatusResponse {
  upload_id: string;
  status: 'active' | 'completed' | 'cancelled' | 'expired';
  chunks_received: number;
  total_chunks: number;
  progress_percent: number;
  expires_at: string | null;
}

/** Upload cancel response */
export interface UploadCancelResponse {
  message: string;
  upload_id: string;
}

/** Upload progress callback */
export type ProgressCallback = (progress: {
  percent: number;
  bytesUploaded: number;
  totalBytes: number;
  chunksUploaded: number;
  totalChunks: number;
  estimatedTimeRemaining?: number;
}) => void;

/** Upload error */
export class UploadError extends Error {
  constructor(
    message: string,
    public readonly code: string,
    public readonly statusCode?: number
  ) {
    super(message);
    this.name = 'UploadError';
  }
}

/**
 * Validate video file before upload
 * @returns null if valid, error message if invalid
 */
export function validateVideoFile(
  file: File,
  durationSeconds: number
): string | null {
  // Check file size (AC-008)
  if (file.size > MAX_FILE_SIZE) {
    const sizeMB = Math.round(file.size / 1024 / 1024);
    return `Video file too large. Please upload a file under 500MB. Current file: ${sizeMB}MB`;
  }

  // Check content type (AC-010)
  if (!ALLOWED_CONTENT_TYPES.includes(file.type as typeof ALLOWED_CONTENT_TYPES[number])) {
    return `Unsupported format. Please upload MP4, MOV, or WebM. Detected format: ${file.type || 'unknown'}`;
  }

  // Check duration (AC-009)
  if (durationSeconds < MIN_DURATION) {
    return `Video must be between 1 and 3 minutes. Current duration: ${durationSeconds} seconds`;
  }
  if (durationSeconds > MAX_DURATION) {
    const minutes = Math.round(durationSeconds / 60);
    return `Video must be between 1 and 3 minutes. Current duration: ${minutes} minutes`;
  }

  return null;
}

/**
 * Get video duration from file
 */
export function getVideoDuration(file: File): Promise<number> {
  return new Promise((resolve, reject) => {
    const video = document.createElement('video');
    video.preload = 'metadata';

    video.onloadedmetadata = () => {
      URL.revokeObjectURL(video.src);
      resolve(Math.round(video.duration));
    };

    video.onerror = () => {
      URL.revokeObjectURL(video.src);
      reject(new Error('Failed to load video metadata'));
    };

    video.src = URL.createObjectURL(file);
  });
}

/**
 * Initiate a chunked upload session
 */
export async function initiateUpload(
  accessToken: string,
  filename: string,
  fileSize: number,
  contentType: string,
  durationSeconds: number
): Promise<UploadInitiateResponse> {
  const response = await fetch(`${API_BASE_URL}/upload/initiate`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      Authorization: `Bearer ${accessToken}`,
    },
    body: JSON.stringify({
      filename,
      file_size: fileSize,
      content_type: contentType,
      duration_seconds: durationSeconds,
    }),
  });

  if (!response.ok) {
    const error = await response.json().catch(() => ({}));
    throw new UploadError(
      error.detail || 'Failed to initiate upload',
      'INITIATE_FAILED',
      response.status
    );
  }

  return response.json();
}

/**
 * Upload a single chunk
 */
export async function uploadChunk(
  accessToken: string,
  uploadId: string,
  chunkNumber: number,
  chunkData: ArrayBuffer
): Promise<UploadChunkResponse> {
  const response = await fetch(
    `${API_BASE_URL}/upload/chunk/${uploadId}/${chunkNumber}`,
    {
      method: 'PUT',
      headers: {
        'Content-Type': 'application/octet-stream',
        Authorization: `Bearer ${accessToken}`,
      },
      body: chunkData,
    }
  );

  if (response.status === 409) {
    // Chunk already exists, skip it
    const error = await response.json();
    throw new UploadError(
      error.detail?.error_description || 'Chunk already uploaded',
      'CHUNK_EXISTS',
      409
    );
  }

  if (!response.ok) {
    const error = await response.json().catch(() => ({}));
    throw new UploadError(
      error.detail || 'Failed to upload chunk',
      'CHUNK_FAILED',
      response.status
    );
  }

  return response.json();
}

/**
 * Complete the upload
 */
export async function completeUpload(
  accessToken: string,
  uploadId: string
): Promise<UploadCompleteResponse> {
  const response = await fetch(`${API_BASE_URL}/upload/complete/${uploadId}`, {
    method: 'POST',
    headers: {
      Authorization: `Bearer ${accessToken}`,
    },
  });

  if (!response.ok) {
    const error = await response.json().catch(() => ({}));
    throw new UploadError(
      error.detail || 'Failed to complete upload',
      'COMPLETE_FAILED',
      response.status
    );
  }

  return response.json();
}

/**
 * Cancel an upload
 */
export async function cancelUpload(
  accessToken: string,
  uploadId: string
): Promise<UploadCancelResponse> {
  const response = await fetch(`${API_BASE_URL}/upload/${uploadId}`, {
    method: 'DELETE',
    headers: {
      Authorization: `Bearer ${accessToken}`,
    },
  });

  if (!response.ok) {
    const error = await response.json().catch(() => ({}));
    throw new UploadError(
      error.detail || 'Failed to cancel upload',
      'CANCEL_FAILED',
      response.status
    );
  }

  return response.json();
}

/**
 * Get upload status for resumption
 */
export async function getUploadStatus(
  accessToken: string,
  uploadId: string
): Promise<UploadStatusResponse> {
  const response = await fetch(`${API_BASE_URL}/upload/status/${uploadId}`, {
    headers: {
      Authorization: `Bearer ${accessToken}`,
    },
  });

  if (!response.ok) {
    const error = await response.json().catch(() => ({}));
    throw new UploadError(
      error.detail || 'Failed to get upload status',
      'STATUS_FAILED',
      response.status
    );
  }

  return response.json();
}

/**
 * Get list of received chunks for resumption
 */
export async function getReceivedChunks(
  accessToken: string,
  uploadId: string
): Promise<number[]> {
  const response = await fetch(`${API_BASE_URL}/upload/chunks/${uploadId}`, {
    headers: {
      Authorization: `Bearer ${accessToken}`,
    },
  });

  if (!response.ok) {
    const error = await response.json().catch(() => ({}));
    throw new UploadError(
      error.detail || 'Failed to get received chunks',
      'CHUNKS_FAILED',
      response.status
    );
  }

  return response.json();
}

/**
 * Upload state for resumable uploads
 */
export interface UploadState {
  uploadId: string;
  file: File;
  totalChunks: number;
  chunkSize: number;
  uploadedChunks: Set<number>;
  startTime: number;
  bytesUploaded: number;
}

/**
 * Perform a full chunked upload with progress and resumability
 *
 * AC-006: Upload with progress indicator
 * AC-011: Resumes automatically after network interruption
 * AC-012: Cancel discards partial upload
 */
export async function uploadVideo(
  accessToken: string,
  file: File,
  durationSeconds: number,
  onProgress: ProgressCallback,
  abortSignal?: AbortSignal,
  existingUploadId?: string
): Promise<UploadCompleteResponse> {
  let state: UploadState;

  // Check for resume
  if (existingUploadId) {
    const status = await getUploadStatus(accessToken, existingUploadId);
    if (status.status !== 'active') {
      throw new UploadError(
        `Upload session is ${status.status}`,
        'SESSION_INVALID'
      );
    }

    const receivedChunks = await getReceivedChunks(accessToken, existingUploadId);

    state = {
      uploadId: existingUploadId,
      file,
      totalChunks: status.total_chunks,
      chunkSize: CHUNK_SIZE,
      uploadedChunks: new Set(receivedChunks),
      startTime: Date.now(),
      bytesUploaded: receivedChunks.length * CHUNK_SIZE,
    };
  } else {
    // Initiate new upload
    const initResponse = await initiateUpload(
      accessToken,
      file.name,
      file.size,
      file.type,
      durationSeconds
    );

    state = {
      uploadId: initResponse.upload_id,
      file,
      totalChunks: initResponse.total_chunks,
      chunkSize: initResponse.chunk_size,
      uploadedChunks: new Set(),
      startTime: Date.now(),
      bytesUploaded: 0,
    };
  }

  // Upload chunks
  for (let chunkNumber = 0; chunkNumber < state.totalChunks; chunkNumber++) {
    // Check for abort
    if (abortSignal?.aborted) {
      await cancelUpload(accessToken, state.uploadId);
      throw new UploadError('Upload cancelled', 'CANCELLED');
    }

    // Skip already uploaded chunks
    if (state.uploadedChunks.has(chunkNumber)) {
      continue;
    }

    // Read chunk from file
    const start = chunkNumber * state.chunkSize;
    const end = Math.min(start + state.chunkSize, file.size);
    const chunk = await file.slice(start, end).arrayBuffer();

    // Upload chunk with retry
    let retries = 3;
    while (retries > 0) {
      try {
        await uploadChunk(accessToken, state.uploadId, chunkNumber, chunk);
        state.uploadedChunks.add(chunkNumber);
        state.bytesUploaded += chunk.byteLength;
        break;
      } catch (error) {
        if (error instanceof UploadError && error.code === 'CHUNK_EXISTS') {
          // Chunk already uploaded, skip
          state.uploadedChunks.add(chunkNumber);
          break;
        }

        retries--;
        if (retries === 0) {
          throw error;
        }

        // Wait before retry (exponential backoff)
        await new Promise((resolve) =>
          setTimeout(resolve, (4 - retries) * 1000)
        );
      }
    }

    // Calculate progress
    const percent = Math.round(
      (state.uploadedChunks.size / state.totalChunks) * 100
    );
    const elapsed = (Date.now() - state.startTime) / 1000;
    const bytesPerSecond = state.bytesUploaded / elapsed;
    const remainingBytes = file.size - state.bytesUploaded;
    const estimatedTimeRemaining =
      bytesPerSecond > 0 ? Math.round(remainingBytes / bytesPerSecond) : undefined;

    onProgress({
      percent,
      bytesUploaded: state.bytesUploaded,
      totalBytes: file.size,
      chunksUploaded: state.uploadedChunks.size,
      totalChunks: state.totalChunks,
      estimatedTimeRemaining,
    });
  }

  // Complete upload
  return completeUpload(accessToken, state.uploadId);
}
