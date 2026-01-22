'use client';

/**
 * Report card component for dashboard list
 * @file ReportCard.tsx
 * @feature F010 - Report History Dashboard
 *
 * Implements:
 * - AC-057: List items show thumbnail, date, summary indicator
 * - AC-058: Clicking report navigates to full view
 * - AC-059: Delete report shows confirmation dialog
 *
 * BDD Scenarios:
 * - Report list item shows thumbnail, date, summary (key moments count)
 * - User navigates to report from list (/dashboard/report/{id})
 * - User deletes report with confirmation dialog
 */

import { useCallback, useState } from 'react';
import { useRouter } from 'next/navigation';
import {
  Box,
  Card,
  CardActionArea,
  CardContent,
  CardMedia,
  IconButton,
  Typography,
} from '@mui/material';
import DeleteOutlineIcon from '@mui/icons-material/DeleteOutline';
import SportsIcon from '@mui/icons-material/Sports';
import { formatAnalyzedDate, type ReportListItem } from '@/lib/dashboard';
import { DeleteConfirmDialog } from './DeleteConfirmDialog';

interface ReportCardProps {
  report: ReportListItem;
  onDelete: (reportId: string) => Promise<void>;
}

/**
 * Report card for dashboard list display
 *
 * AC-057: Shows thumbnail, date, summary indicator (key moments count)
 * AC-058: Clicking navigates to /dashboard/report/{id}
 */
export function ReportCard({ report, onDelete }: ReportCardProps) {
  const router = useRouter();
  const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
  const [isDeleting, setIsDeleting] = useState(false);

  // AC-058: Navigate to full report view
  const handleClick = useCallback(() => {
    router.push(`/dashboard/report/${report.id}`);
  }, [router, report.id]);

  // AC-059: Open delete confirmation dialog
  const handleDeleteClick = useCallback((e: React.MouseEvent) => {
    e.stopPropagation(); // Prevent card click navigation
    setDeleteDialogOpen(true);
  }, []);

  const handleDeleteCancel = useCallback(() => {
    setDeleteDialogOpen(false);
  }, []);

  const handleDeleteConfirm = useCallback(async () => {
    setIsDeleting(true);
    try {
      await onDelete(report.id);
      setDeleteDialogOpen(false);
    } finally {
      setIsDeleting(false);
    }
  }, [onDelete, report.id]);

  // Format display values
  const analyzedDate = formatAnalyzedDate(report.analyzed_at);
  const keyMomentsText = `${report.key_moments_count} key moments detected`;
  const keyMomentsKo = `${report.key_moments_count}개의 핵심 순간 감지`;

  return (
    <>
      <Card
        sx={{
          display: 'flex',
          flexDirection: { xs: 'column', sm: 'row' },
          height: { xs: 'auto', sm: 140 },
          position: 'relative',
          '&:hover .delete-button': {
            opacity: 1,
          },
        }}
      >
        <CardActionArea
          onClick={handleClick}
          sx={{
            display: 'flex',
            flexDirection: { xs: 'column', sm: 'row' },
            alignItems: 'stretch',
          }}
        >
          {/* Thumbnail - AC-057 */}
          {report.thumbnail_url ? (
            <CardMedia
              component="img"
              sx={{
                width: { xs: '100%', sm: 180 },
                height: { xs: 120, sm: 140 },
                objectFit: 'cover',
              }}
              image={report.thumbnail_url}
              alt="Video thumbnail"
            />
          ) : (
            <Box
              sx={{
                width: { xs: '100%', sm: 180 },
                height: { xs: 120, sm: 140 },
                bgcolor: 'grey.200',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                flexShrink: 0,
              }}
            >
              <SportsIcon sx={{ fontSize: 48, color: 'grey.400' }} />
            </Box>
          )}

          <CardContent sx={{ flex: 1, py: 2 }}>
            {/* Date - AC-057 */}
            <Typography variant="body2" color="text.secondary" gutterBottom>
              Analyzed on {analyzedDate}
              <br />
              <span style={{ fontSize: '0.85em' }}>
                {new Date(report.analyzed_at).toLocaleDateString('ko-KR')} 분석됨
              </span>
            </Typography>

            {/* Summary indicator - AC-057 */}
            <Typography variant="body1" fontWeight="medium">
              {keyMomentsText}
              <br />
              <span style={{ fontSize: '0.85em', opacity: 0.8 }}>
                {keyMomentsKo}
              </span>
            </Typography>

            {/* Performance score if available */}
            {report.performance_score !== null && (
              <Typography
                variant="h6"
                color={
                  report.performance_score >= 70
                    ? 'success.main'
                    : report.performance_score >= 40
                      ? 'warning.main'
                      : 'error.main'
                }
                sx={{ mt: 1 }}
              >
                Score: {report.performance_score}
              </Typography>
            )}
          </CardContent>
        </CardActionArea>

        {/* Delete button - AC-059 */}
        <IconButton
          className="delete-button"
          onClick={handleDeleteClick}
          sx={{
            position: 'absolute',
            top: 8,
            right: 8,
            bgcolor: 'background.paper',
            opacity: { xs: 1, sm: 0 },
            transition: 'opacity 0.2s',
            '&:hover': {
              bgcolor: 'error.light',
              color: 'error.contrastText',
            },
          }}
          aria-label="Delete report"
        >
          <DeleteOutlineIcon />
        </IconButton>
      </Card>

      {/* Delete confirmation dialog - AC-059 */}
      <DeleteConfirmDialog
        open={deleteDialogOpen}
        onClose={handleDeleteCancel}
        onConfirm={handleDeleteConfirm}
        isDeleting={isDeleting}
      />
    </>
  );
}
