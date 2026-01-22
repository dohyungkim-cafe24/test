'use client';

/**
 * Upload progress component with cancel functionality
 * @file UploadProgress.tsx
 * @feature F002 - Video Upload
 *
 * Material Design 3 implementation
 *
 * Scenarios covered:
 * - Progress bar with percentage
 * - Bytes transferred and total
 * - Estimated time remaining
 * - Cancel button with confirmation dialog
 * - Connection lost message (AC-011)
 */

import { useCallback, useState } from 'react';
import {
  Box,
  Button,
  Card,
  CardContent,
  CircularProgress,
  Dialog,
  DialogActions,
  DialogContent,
  DialogContentText,
  DialogTitle,
  LinearProgress,
  Typography,
  useTheme,
} from '@mui/material';
import CancelIcon from '@mui/icons-material/Cancel';
import CloudOffIcon from '@mui/icons-material/CloudOff';

export interface UploadProgressProps {
  /** Upload progress percentage (0-100) */
  percent: number;
  /** Bytes uploaded so far */
  bytesUploaded: number;
  /** Total file size in bytes */
  totalBytes: number;
  /** Chunks uploaded so far */
  chunksUploaded: number;
  /** Total number of chunks */
  totalChunks: number;
  /** Estimated time remaining in seconds */
  estimatedTimeRemaining?: number;
  /** Whether connection is lost */
  isConnectionLost?: boolean;
  /** Filename being uploaded */
  filename?: string;
  /** Called when user confirms cancellation */
  onCancel: () => void;
}

/** Format bytes to human-readable string */
function formatBytes(bytes: number): string {
  if (bytes === 0) return '0 B';
  const k = 1024;
  const sizes = ['B', 'KB', 'MB', 'GB'];
  const i = Math.floor(Math.log(bytes) / Math.log(k));
  return `${(bytes / Math.pow(k, i)).toFixed(1)} ${sizes[i]}`;
}

/** Format seconds to human-readable string */
function formatTime(seconds: number): string {
  if (seconds < 60) {
    return `${seconds}s`;
  }
  const minutes = Math.floor(seconds / 60);
  const remainingSeconds = seconds % 60;
  if (minutes < 60) {
    return remainingSeconds > 0
      ? `${minutes}m ${remainingSeconds}s`
      : `${minutes}m`;
  }
  const hours = Math.floor(minutes / 60);
  const remainingMinutes = minutes % 60;
  return `${hours}h ${remainingMinutes}m`;
}

export function UploadProgress({
  percent,
  bytesUploaded,
  totalBytes,
  chunksUploaded,
  totalChunks,
  estimatedTimeRemaining,
  isConnectionLost = false,
  filename,
  onCancel,
}: UploadProgressProps) {
  const theme = useTheme();
  const [showCancelDialog, setShowCancelDialog] = useState(false);

  const handleCancelClick = useCallback(() => {
    setShowCancelDialog(true);
  }, []);

  const handleCancelConfirm = useCallback(() => {
    setShowCancelDialog(false);
    onCancel();
  }, [onCancel]);

  const handleCancelDismiss = useCallback(() => {
    setShowCancelDialog(false);
  }, []);

  return (
    <>
      <Card variant="outlined">
        <CardContent>
          {/* Header */}
          <Box
            sx={{
              display: 'flex',
              justifyContent: 'space-between',
              alignItems: 'flex-start',
              mb: 2,
            }}
          >
            <Box>
              <Typography variant="h6" component="p" gutterBottom>
                Uploading video
              </Typography>
              {filename && (
                <Typography
                  variant="body2"
                  color="text.secondary"
                  sx={{
                    maxWidth: 250,
                    overflow: 'hidden',
                    textOverflow: 'ellipsis',
                    whiteSpace: 'nowrap',
                  }}
                >
                  {filename}
                </Typography>
              )}
            </Box>
            <Button
              variant="outlined"
              color="error"
              size="small"
              startIcon={<CancelIcon />}
              onClick={handleCancelClick}
              aria-label="Cancel upload"
            >
              Cancel
            </Button>
          </Box>

          {/* Connection lost warning */}
          {isConnectionLost && (
            <Box
              sx={{
                display: 'flex',
                alignItems: 'center',
                gap: 1,
                mb: 2,
                p: 1.5,
                borderRadius: 1,
                backgroundColor: theme.palette.warning.light,
                color: theme.palette.warning.contrastText,
              }}
              role="alert"
            >
              <CloudOffIcon />
              <Typography variant="body2">
                Connection lost. Waiting to resume...
              </Typography>
            </Box>
          )}

          {/* Progress bar */}
          <Box sx={{ mb: 2 }}>
            <Box
              sx={{
                display: 'flex',
                justifyContent: 'space-between',
                alignItems: 'center',
                mb: 1,
              }}
            >
              <Typography variant="body2" color="text.secondary">
                {percent}% uploaded
              </Typography>
              {estimatedTimeRemaining !== undefined && !isConnectionLost && (
                <Typography variant="body2" color="text.secondary">
                  ~{formatTime(estimatedTimeRemaining)} remaining
                </Typography>
              )}
            </Box>
            <LinearProgress
              variant="determinate"
              value={percent}
              sx={{
                height: 8,
                borderRadius: 1,
                backgroundColor: theme.palette.grey[200],
                '& .MuiLinearProgress-bar': {
                  borderRadius: 1,
                },
              }}
              aria-label={`Upload progress: ${percent}%`}
            />
          </Box>

          {/* Stats */}
          <Box
            sx={{
              display: 'flex',
              justifyContent: 'space-between',
              flexWrap: 'wrap',
              gap: 1,
            }}
          >
            <Typography variant="caption" color="text.secondary">
              {formatBytes(bytesUploaded)} / {formatBytes(totalBytes)}
            </Typography>
            <Typography variant="caption" color="text.secondary">
              Chunk {chunksUploaded} of {totalChunks}
            </Typography>
          </Box>
        </CardContent>
      </Card>

      {/* Cancel confirmation dialog */}
      <Dialog
        open={showCancelDialog}
        onClose={handleCancelDismiss}
        aria-labelledby="cancel-dialog-title"
        aria-describedby="cancel-dialog-description"
      >
        <DialogTitle id="cancel-dialog-title">Cancel upload?</DialogTitle>
        <DialogContent>
          <DialogContentText id="cancel-dialog-description">
            Your upload progress will be lost and you will need to start over.
            Are you sure you want to cancel?
          </DialogContentText>
        </DialogContent>
        <DialogActions>
          <Button onClick={handleCancelDismiss}>Continue uploading</Button>
          <Button onClick={handleCancelConfirm} color="error" autoFocus>
            Yes, cancel
          </Button>
        </DialogActions>
      </Dialog>
    </>
  );
}
