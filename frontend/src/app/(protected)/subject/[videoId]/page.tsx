'use client';

/**
 * Subject Selection page
 * @file page.tsx
 * @feature F003 - Subject Selection
 *
 * Implements:
 * - AC-013: Thumbnail grid displays after upload completes
 * - AC-014: Tap on person highlights with selection indicator
 * - AC-015: Confirm selection stores bounding box for tracking
 * - AC-016: Selection can be changed before confirmation
 * - AC-017: Single person auto-selected with confirm option
 *
 * BDD Scenarios:
 * - Thumbnail grid displays extracted frames
 * - User selects subject from thumbnail
 * - User changes selection before confirmation
 * - User confirms subject selection
 * - Single person auto-selected
 * - No subjects detected in video
 * - Thumbnail extraction loading state
 */

import { useCallback, useEffect, useState } from 'react';
import { useParams, useRouter } from 'next/navigation';
import {
  Alert,
  Box,
  Button,
  CircularProgress,
  Container,
  Snackbar,
  Typography,
} from '@mui/material';
import CloudUploadIcon from '@mui/icons-material/CloudUpload';
import { useAuth } from '@/lib/auth/hooks';
import { ThumbnailGrid } from '@/components/subject';
import {
  getThumbnails,
  selectSubject,
  SubjectError,
  ThumbnailsResponse,
} from '@/lib/subject';

/** Polling interval for thumbnail extraction status (ms) */
const POLL_INTERVAL = 2000;

/** Maximum polling attempts before showing error */
const MAX_POLL_ATTEMPTS = 60; // 2 minutes

/** Selection state */
interface Selection {
  thumbnailId: string;
  personId: string;
}

export default function SubjectSelectionPage() {
  const params = useParams();
  const router = useRouter();
  const { accessToken, isLoading: isAuthLoading, isAuthenticated } = useAuth();

  const videoId = params.videoId as string;

  // Data state
  const [thumbnailData, setThumbnailData] = useState<ThumbnailsResponse | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [pollCount, setPollCount] = useState(0);

  // Selection state
  const [selection, setSelection] = useState<Selection | null>(null);
  const [isSubmitting, setIsSubmitting] = useState(false);

  // Error state
  const [errorMessage, setErrorMessage] = useState<string | null>(null);
  const [showError, setShowError] = useState(false);

  // Fetch thumbnails (with polling for processing status)
  useEffect(() => {
    if (!accessToken || !videoId) return;

    let isMounted = true;
    let pollTimer: NodeJS.Timeout | null = null;

    const fetchThumbnails = async () => {
      try {
        const data = await getThumbnails(accessToken, videoId);

        if (!isMounted) return;

        setThumbnailData(data);

        // If still processing, continue polling
        if (data.status === 'processing') {
          setPollCount((prev) => {
            if (prev >= MAX_POLL_ATTEMPTS) {
              setErrorMessage('Frame extraction is taking longer than expected. Please try again later.');
              setShowError(true);
              setIsLoading(false);
              return prev;
            }
            return prev + 1;
          });

          pollTimer = setTimeout(fetchThumbnails, POLL_INTERVAL);
        } else {
          setIsLoading(false);

          // AC-017: Auto-select if single person detected
          if (data.auto_select) {
            setSelection({
              thumbnailId: data.auto_select.thumbnail_id,
              personId: data.auto_select.person_id,
            });
          }
        }
      } catch (error) {
        if (!isMounted) return;

        setIsLoading(false);

        if (error instanceof SubjectError) {
          setErrorMessage(error.message);
        } else {
          setErrorMessage('Failed to load thumbnails. Please try again.');
        }
        setShowError(true);
      }
    };

    fetchThumbnails();

    return () => {
      isMounted = false;
      if (pollTimer) clearTimeout(pollTimer);
    };
  }, [accessToken, videoId]);

  // Handle person selection
  const handlePersonSelect = useCallback((thumbnailId: string, personId: string) => {
    setSelection({ thumbnailId, personId });
  }, []);

  // Handle confirm selection
  const handleConfirmSelection = useCallback(async () => {
    if (!accessToken || !selection) return;

    setIsSubmitting(true);
    setErrorMessage(null);

    try {
      await selectSubject(
        accessToken,
        videoId,
        selection.thumbnailId,
        selection.personId
      );

      // AC-015: Navigate to body specification page after selection
      router.push(`/body-specs/${videoId}`);
    } catch (error) {
      if (error instanceof SubjectError) {
        setErrorMessage(error.message);
      } else {
        setErrorMessage('Failed to confirm selection. Please try again.');
      }
      setShowError(true);
    } finally {
      setIsSubmitting(false);
    }
  }, [accessToken, videoId, selection, router]);

  // Handle upload different video
  const handleUploadDifferent = useCallback(() => {
    router.push('/upload');
  }, [router]);

  // Handle error close
  const handleErrorClose = useCallback(() => {
    setShowError(false);
  }, []);

  // Auth loading state
  if (isAuthLoading) {
    return (
      <Box
        sx={{
          display: 'flex',
          justifyContent: 'center',
          alignItems: 'center',
          minHeight: '60vh',
        }}
      >
        <CircularProgress />
      </Box>
    );
  }

  // Not authenticated - redirect will happen via middleware
  if (!isAuthenticated) {
    return (
      <Box
        sx={{
          display: 'flex',
          justifyContent: 'center',
          alignItems: 'center',
          minHeight: '60vh',
        }}
      >
        <Typography>Redirecting to login...</Typography>
      </Box>
    );
  }

  // Processing state
  if (isLoading || thumbnailData?.status === 'processing') {
    return (
      <Container maxWidth="md" sx={{ py: 4 }}>
        <Typography variant="h4" component="h1" gutterBottom textAlign="center">
          Subject Selection
        </Typography>
        <Typography
          variant="subtitle1"
          color="text.secondary"
          textAlign="center"
          gutterBottom
        >
          {/* Korean + English */}
          Extracting frames... / 프레임 추출 중...
        </Typography>

        <Box
          sx={{
            display: 'flex',
            flexDirection: 'column',
            alignItems: 'center',
            mt: 4,
            mb: 4,
          }}
        >
          <CircularProgress size={48} />
        </Box>

        {/* Skeleton grid */}
        <ThumbnailGrid
          thumbnails={[]}
          selectedPerson={null}
          onPersonSelect={() => {}}
          isLoading={true}
        />
      </Container>
    );
  }

  // No subjects detected state
  if (thumbnailData?.status === 'no_subjects') {
    return (
      <Container maxWidth="sm" sx={{ py: 4 }}>
        <Typography variant="h4" component="h1" gutterBottom textAlign="center">
          No Subjects Detected
        </Typography>
        <Typography
          variant="subtitle1"
          color="text.secondary"
          textAlign="center"
          gutterBottom
        >
          {/* Korean + English */}
          No subjects detected / 피사체를 찾지 못했습니다
        </Typography>

        <Box
          sx={{
            display: 'flex',
            flexDirection: 'column',
            alignItems: 'center',
            mt: 4,
            gap: 2,
          }}
        >
          <Typography
            variant="body1"
            color="text.secondary"
            textAlign="center"
          >
            We couldn&apos;t identify any people in your video.
          </Typography>
          <Typography
            variant="body2"
            color="text.secondary"
            textAlign="center"
          >
            Please upload a video with clear visibility of the participants.
          </Typography>

          <Button
            variant="contained"
            size="large"
            startIcon={<CloudUploadIcon />}
            onClick={handleUploadDifferent}
            sx={{ mt: 2 }}
          >
            Upload Different Video
          </Button>
        </Box>
      </Container>
    );
  }

  // Failed state
  if (thumbnailData?.status === 'failed') {
    return (
      <Container maxWidth="sm" sx={{ py: 4 }}>
        <Typography variant="h4" component="h1" gutterBottom textAlign="center">
          Processing Failed
        </Typography>

        <Box
          sx={{
            display: 'flex',
            flexDirection: 'column',
            alignItems: 'center',
            mt: 4,
            gap: 2,
          }}
        >
          <Typography
            variant="body1"
            color="text.secondary"
            textAlign="center"
          >
            {thumbnailData.message || 'An error occurred during processing.'}
          </Typography>

          <Button
            variant="contained"
            size="large"
            startIcon={<CloudUploadIcon />}
            onClick={handleUploadDifferent}
            sx={{ mt: 2 }}
          >
            Upload Different Video
          </Button>
        </Box>
      </Container>
    );
  }

  // Ready state with thumbnails
  const isSinglePerson = thumbnailData?.auto_select !== null;

  return (
    <Container maxWidth="md" sx={{ py: 4 }}>
      <Typography variant="h4" component="h1" gutterBottom textAlign="center">
        Subject Selection
      </Typography>

      <Typography
        variant="subtitle1"
        color="text.secondary"
        textAlign="center"
        gutterBottom
      >
        {isSinglePerson ? (
          // AC-017: Single person detected message (Korean + English)
          <>We detected one person. Is this you? / 한 명이 감지되었습니다. 본인이 맞나요?</>
        ) : (
          // Multi-person instruction (Korean + English)
          <>Tap on yourself in the video / 영상에서 본인을 탭하세요</>
        )}
      </Typography>

      <Box sx={{ mt: 4, mb: 4 }}>
        <ThumbnailGrid
          thumbnails={thumbnailData?.thumbnails || []}
          selectedPerson={selection}
          onPersonSelect={handlePersonSelect}
          isLoading={false}
        />
      </Box>

      <Box sx={{ display: 'flex', justifyContent: 'center', gap: 2 }}>
        <Button
          variant="outlined"
          onClick={handleUploadDifferent}
          disabled={isSubmitting}
        >
          Upload Different Video
        </Button>
        <Button
          variant="contained"
          size="large"
          onClick={handleConfirmSelection}
          disabled={!selection || isSubmitting}
        >
          {isSubmitting ? (
            <CircularProgress size={24} color="inherit" />
          ) : (
            'Confirm Selection'
          )}
        </Button>
      </Box>

      {/* Error snackbar */}
      <Snackbar
        open={showError}
        autoHideDuration={6000}
        onClose={handleErrorClose}
        anchorOrigin={{ vertical: 'bottom', horizontal: 'center' }}
      >
        <Alert
          onClose={handleErrorClose}
          severity="error"
          variant="filled"
          sx={{ width: '100%' }}
        >
          {errorMessage}
        </Alert>
      </Snackbar>
    </Container>
  );
}
