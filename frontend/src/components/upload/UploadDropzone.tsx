'use client';

/**
 * Upload dropzone component with drag & drop support
 * @file UploadDropzone.tsx
 * @feature F002 - Video Upload
 *
 * Material Design 3 implementation
 *
 * Scenarios covered:
 * - Empty state with drop zone (dashed border, cloud icon)
 * - Drag over visual feedback
 * - File validation on select/drop
 */

import { useCallback, useState } from 'react';
import { Box, Paper, Typography, alpha, useTheme } from '@mui/material';
import CloudUploadIcon from '@mui/icons-material/CloudUpload';
import {
  ALLOWED_CONTENT_TYPES,
  getVideoDuration,
  MAX_FILE_SIZE,
  validateVideoFile,
} from '@/lib/upload';

export interface UploadDropzoneProps {
  /** Called when a valid file is selected */
  onFileSelect: (file: File, durationSeconds: number) => void;
  /** Called when validation fails */
  onValidationError: (error: string) => void;
  /** Whether upload is in progress */
  disabled?: boolean;
}

export function UploadDropzone({
  onFileSelect,
  onValidationError,
  disabled = false,
}: UploadDropzoneProps) {
  const theme = useTheme();
  const [isDragOver, setIsDragOver] = useState(false);
  const [isValidating, setIsValidating] = useState(false);

  const handleFile = useCallback(
    async (file: File) => {
      if (disabled || isValidating) return;

      setIsValidating(true);
      try {
        // Get video duration
        let durationSeconds: number;
        try {
          durationSeconds = await getVideoDuration(file);
        } catch {
          onValidationError(
            'Could not read video metadata. Please ensure the file is a valid video.'
          );
          return;
        }

        // Validate file
        const error = validateVideoFile(file, durationSeconds);
        if (error) {
          onValidationError(error);
          return;
        }

        onFileSelect(file, durationSeconds);
      } finally {
        setIsValidating(false);
      }
    },
    [disabled, isValidating, onFileSelect, onValidationError]
  );

  const handleDragOver = useCallback(
    (e: React.DragEvent) => {
      e.preventDefault();
      e.stopPropagation();
      if (!disabled) {
        setIsDragOver(true);
      }
    },
    [disabled]
  );

  const handleDragLeave = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragOver(false);
  }, []);

  const handleDrop = useCallback(
    async (e: React.DragEvent) => {
      e.preventDefault();
      e.stopPropagation();
      setIsDragOver(false);

      if (disabled) return;

      const files = e.dataTransfer.files;
      if (files.length > 0) {
        await handleFile(files[0]);
      }
    },
    [disabled, handleFile]
  );

  const handleInputChange = useCallback(
    async (e: React.ChangeEvent<HTMLInputElement>) => {
      const files = e.target.files;
      if (files && files.length > 0) {
        await handleFile(files[0]);
      }
      // Reset input so same file can be selected again
      e.target.value = '';
    },
    [handleFile]
  );

  const handleClick = useCallback(() => {
    if (!disabled) {
      document.getElementById('video-upload-input')?.click();
    }
  }, [disabled]);

  const handleKeyDown = useCallback(
    (e: React.KeyboardEvent) => {
      if ((e.key === 'Enter' || e.key === ' ') && !disabled) {
        e.preventDefault();
        handleClick();
      }
    },
    [disabled, handleClick]
  );

  return (
    <Paper
      variant="outlined"
      role="button"
      tabIndex={disabled ? -1 : 0}
      aria-label="Upload video. Click or drag and drop"
      aria-disabled={disabled}
      onClick={handleClick}
      onKeyDown={handleKeyDown}
      onDragOver={handleDragOver}
      onDragLeave={handleDragLeave}
      onDrop={handleDrop}
      sx={{
        p: 4,
        minHeight: 280,
        display: 'flex',
        flexDirection: 'column',
        alignItems: 'center',
        justifyContent: 'center',
        textAlign: 'center',
        cursor: disabled ? 'default' : 'pointer',
        borderStyle: 'dashed',
        borderWidth: 2,
        borderColor: isDragOver
          ? theme.palette.primary.main
          : theme.palette.divider,
        backgroundColor: isDragOver
          ? alpha(theme.palette.primary.main, 0.04)
          : 'transparent',
        transition: theme.transitions.create(
          ['border-color', 'background-color'],
          { duration: theme.transitions.duration.short }
        ),
        opacity: disabled ? 0.5 : 1,
        '&:hover': disabled
          ? {}
          : {
              borderColor: theme.palette.primary.light,
              backgroundColor: alpha(theme.palette.primary.main, 0.02),
            },
        '&:focus-visible': {
          outline: `2px solid ${theme.palette.primary.main}`,
          outlineOffset: 2,
        },
      }}
    >
      <input
        id="video-upload-input"
        type="file"
        accept={ALLOWED_CONTENT_TYPES.join(',')}
        onChange={handleInputChange}
        hidden
        disabled={disabled}
      />

      <CloudUploadIcon
        sx={{
          fontSize: 64,
          color: isDragOver
            ? theme.palette.primary.main
            : theme.palette.action.active,
          mb: 2,
        }}
      />

      <Typography
        variant="h6"
        component="p"
        color={isDragOver ? 'primary' : 'textPrimary'}
        gutterBottom
      >
        {isValidating ? 'Validating video...' : 'Drop your video here'}
      </Typography>

      <Typography variant="body2" color="text.secondary" gutterBottom>
        or tap to browse
      </Typography>

      <Box
        component="ul"
        sx={{
          mt: 3,
          listStyle: 'none',
          p: 0,
          m: 0,
          '& li': {
            mb: 0.5,
          },
        }}
      >
        <Typography component="li" variant="caption" color="text.secondary">
          Formats: MP4, MOV, WebM
        </Typography>
        <Typography component="li" variant="caption" color="text.secondary">
          Maximum size: 500MB
        </Typography>
        <Typography component="li" variant="caption" color="text.secondary">
          Duration: 1-3 minutes
        </Typography>
      </Box>
    </Paper>
  );
}
