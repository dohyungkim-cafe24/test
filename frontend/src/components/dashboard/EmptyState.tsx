'use client';

/**
 * Empty state component for dashboard
 * @file EmptyState.tsx
 * @feature F010 - Report History Dashboard
 *
 * Implements:
 * - AC-060: Empty state shows upload CTA
 *
 * BDD Scenario:
 * - Dashboard shows empty state for new user
 * - I should see the empty state illustration
 * - I should see "No analysis reports yet"
 * - I should see "Upload your first sparring video to get AI-powered coaching feedback"
 * - I should see an "Upload Video" button
 * - When I click "Upload Video" then I should be navigated to the upload page
 */

import { useCallback } from 'react';
import { useRouter } from 'next/navigation';
import { Box, Button, Typography } from '@mui/material';
import CloudUploadIcon from '@mui/icons-material/CloudUpload';
import SportsKabaddiIcon from '@mui/icons-material/SportsKabaddi';

/**
 * Empty state display for users with no reports
 *
 * AC-060: Empty state shows upload CTA
 */
export function EmptyState() {
  const router = useRouter();

  // BDD: Navigate to upload page when clicking Upload Video
  const handleUploadClick = useCallback(() => {
    router.push('/upload');
  }, [router]);

  return (
    <Box
      sx={{
        display: 'flex',
        flexDirection: 'column',
        alignItems: 'center',
        justifyContent: 'center',
        py: 8,
        px: 3,
        textAlign: 'center',
      }}
    >
      {/* Empty state illustration */}
      <Box
        sx={{
          width: 120,
          height: 120,
          borderRadius: '50%',
          bgcolor: 'primary.light',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          mb: 3,
        }}
      >
        <SportsKabaddiIcon sx={{ fontSize: 64, color: 'primary.main' }} />
      </Box>

      {/* BDD: "No analysis reports yet" */}
      <Typography variant="h5" gutterBottom>
        No analysis reports yet
        <br />
        <span style={{ fontSize: '0.7em', opacity: 0.7 }}>
          아직 분석 보고서가 없습니다
        </span>
      </Typography>

      {/* BDD: "Upload your first sparring video..." */}
      <Typography
        variant="body1"
        color="text.secondary"
        sx={{ maxWidth: 400, mb: 4 }}
      >
        Upload your first sparring video to get AI-powered coaching feedback
        <br />
        <span style={{ fontSize: '0.9em' }}>
          첫 번째 스파링 영상을 업로드하여 AI 코칭 피드백을 받으세요
        </span>
      </Typography>

      {/* BDD: "Upload Video" button */}
      <Button
        variant="contained"
        size="large"
        startIcon={<CloudUploadIcon />}
        onClick={handleUploadClick}
        sx={{ px: 4, py: 1.5 }}
      >
        Upload Video
        <span style={{ marginLeft: 8, fontSize: '0.85em', opacity: 0.8 }}>
          영상 업로드
        </span>
      </Button>
    </Box>
  );
}
