'use client';

/**
 * Dashboard page (protected)
 * @file page.tsx
 * @feature F001 - User Authentication
 * @feature F010 - Report History Dashboard
 *
 * Implements:
 * - AC-056: Dashboard lists reports sorted by date descending
 * - AC-057: List items show thumbnail, date, summary indicator
 * - AC-058: Clicking report navigates to full view
 * - AC-059: Delete report shows confirmation dialog
 * - AC-060: Empty state shows upload CTA
 *
 * BDD Scenarios:
 * - Dashboard displays report list sorted by date (newest first)
 * - Report list item shows thumbnail, date, summary (key moments count)
 * - User navigates to report from list (/dashboard/report/{id})
 * - User deletes report with confirmation dialog and undo toast (10 seconds)
 * - Dashboard shows empty state for new user (illustration, Upload Video CTA)
 * - Dashboard loading state shows skeleton cards with pulse animation
 */

import React, { useCallback, useEffect, useState } from 'react';
import Box from '@mui/material/Box';
import AppBar from '@mui/material/AppBar';
import Toolbar from '@mui/material/Toolbar';
import Typography from '@mui/material/Typography';
import Container from '@mui/material/Container';
import Avatar from '@mui/material/Avatar';
import Menu from '@mui/material/Menu';
import MenuItem from '@mui/material/MenuItem';
import IconButton from '@mui/material/IconButton';
import Button from '@mui/material/Button';
import Alert from '@mui/material/Alert';
import Snackbar from '@mui/material/Snackbar';
import AddIcon from '@mui/icons-material/Add';
import { AuthGuard } from '@/components/auth/AuthGuard';
import {
  EmptyState,
  ReportCard,
  ReportListSkeleton,
} from '@/components/dashboard';
import { useAuth } from '@/lib/auth/hooks';
import {
  DashboardError,
  deleteReport,
  getReportList,
  restoreReport,
  type ReportListItem,
} from '@/lib/dashboard';
import { useRouter } from 'next/navigation';

/**
 * Dashboard content (shown after auth)
 */
function DashboardContent() {
  const { user, logout, accessToken } = useAuth();
  const router = useRouter();
  const [anchorEl, setAnchorEl] = React.useState<null | HTMLElement>(null);

  // Report list state
  const [reports, setReports] = useState<ReportListItem[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // Undo toast state - BDD: Undo toast for 10 seconds
  const [deletedReport, setDeletedReport] = useState<{
    id: string;
    canRestoreUntil: string;
  } | null>(null);
  const [showUndoToast, setShowUndoToast] = useState(false);

  // Fetch reports on mount
  useEffect(() => {
    if (!accessToken) return;

    const fetchReports = async () => {
      setIsLoading(true);
      setError(null);

      try {
        const data = await getReportList(accessToken);
        setReports(data.items);
      } catch (err) {
        if (err instanceof DashboardError) {
          setError(err.message);
        } else {
          setError('Failed to load reports. Please try again.');
        }
      } finally {
        setIsLoading(false);
      }
    };

    fetchReports();
  }, [accessToken]);

  const handleMenuOpen = (event: React.MouseEvent<HTMLElement>) => {
    setAnchorEl(event.currentTarget);
  };

  const handleMenuClose = () => {
    setAnchorEl(null);
  };

  const handleLogout = async () => {
    handleMenuClose();
    await logout();
    router.push('/');
  };

  const handleUploadClick = () => {
    router.push('/upload');
  };

  // AC-059: Delete report with confirmation
  // BDD: Undo toast for 10 seconds
  const handleDeleteReport = useCallback(async (reportId: string) => {
    if (!accessToken) return;

    try {
      const result = await deleteReport(accessToken, reportId);

      // Remove from list optimistically
      setReports((prev) => prev.filter((r) => r.id !== reportId));

      // Show undo toast
      setDeletedReport({
        id: reportId,
        canRestoreUntil: result.can_restore_until,
      });
      setShowUndoToast(true);
    } catch (err) {
      if (err instanceof DashboardError) {
        setError(err.message);
      } else {
        setError('Failed to delete report. Please try again.');
      }
    }
  }, [accessToken]);

  // BDD: Undo delete within 10 seconds
  const handleUndo = useCallback(async () => {
    if (!accessToken || !deletedReport) return;

    try {
      await restoreReport(accessToken, deletedReport.id);

      // Refetch reports to get the restored one back
      const data = await getReportList(accessToken);
      setReports(data.items);

      setShowUndoToast(false);
      setDeletedReport(null);
    } catch (err) {
      if (err instanceof DashboardError) {
        setError(err.message);
      } else {
        setError('Failed to restore report. Please try again.');
      }
    }
  }, [accessToken, deletedReport]);

  const handleUndoToastClose = useCallback(() => {
    setShowUndoToast(false);
    setDeletedReport(null);
  }, []);

  return (
    <Box sx={{ flexGrow: 1 }}>
      {/* App Bar */}
      <AppBar position="static" color="default" elevation={0}>
        <Toolbar>
          <Typography
            variant="h6"
            component="div"
            sx={{ flexGrow: 1, color: 'primary.main', fontWeight: 700 }}
          >
            PunchAnalytics
          </Typography>

          {/* User Profile Menu */}
          <IconButton onClick={handleMenuOpen} size="small">
            <Avatar
              src={user?.avatar_url || undefined}
              alt={user?.name || user?.email}
              sx={{ width: 36, height: 36 }}
            >
              {user?.name?.[0] || user?.email?.[0]?.toUpperCase()}
            </Avatar>
          </IconButton>

          <Menu
            anchorEl={anchorEl}
            open={Boolean(anchorEl)}
            onClose={handleMenuClose}
            anchorOrigin={{
              vertical: 'bottom',
              horizontal: 'right',
            }}
            transformOrigin={{
              vertical: 'top',
              horizontal: 'right',
            }}
          >
            <MenuItem disabled>
              <Typography variant="body2" color="text.secondary">
                {user?.email}
              </Typography>
            </MenuItem>
            <MenuItem onClick={handleLogout}>
              Log out
              <span style={{ marginLeft: 8, fontSize: '0.85em', opacity: 0.7 }}>
                로그아웃
              </span>
            </MenuItem>
          </Menu>
        </Toolbar>
      </AppBar>

      {/* Main Content */}
      <Container maxWidth="lg" sx={{ py: 4 }}>
        {/* Page Title - BDD: "My Reports" as the page title */}
        <Box
          sx={{
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'space-between',
            mb: 4,
          }}
        >
          <Typography variant="h4">
            My Reports
            <span
              style={{
                display: 'block',
                fontSize: '0.5em',
                opacity: 0.7,
                marginTop: 4,
              }}
            >
              내 분석 보고서
            </span>
          </Typography>

          {/* Upload button */}
          <Button
            variant="contained"
            startIcon={<AddIcon />}
            onClick={handleUploadClick}
          >
            Upload Video
            <span style={{ marginLeft: 8, fontSize: '0.85em', opacity: 0.8 }}>
              업로드
            </span>
          </Button>
        </Box>

        {/* Error state */}
        {error && (
          <Alert severity="error" sx={{ mb: 3 }}>
            {error}
            <br />
            <span style={{ fontSize: '0.9em' }}>
              오류가 발생했습니다. 다시 시도해 주세요.
            </span>
          </Alert>
        )}

        {/* Loading state - BDD: 3 skeleton cards with pulse animation */}
        {isLoading && <ReportListSkeleton />}

        {/* Empty state - AC-060 */}
        {!isLoading && !error && reports.length === 0 && <EmptyState />}

        {/* Report list - AC-056: Sorted by date descending */}
        {!isLoading && !error && reports.length > 0 && (
          <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2 }}>
            {reports.map((report) => (
              <ReportCard
                key={report.id}
                report={report}
                onDelete={handleDeleteReport}
              />
            ))}
          </Box>
        )}
      </Container>

      {/* Undo toast - BDD: toast shows "Undo" option for 10 seconds */}
      <Snackbar
        open={showUndoToast}
        autoHideDuration={10000}
        onClose={handleUndoToastClose}
        message="Report deleted"
        action={
          <Button color="primary" size="small" onClick={handleUndo}>
            Undo
            <span style={{ marginLeft: 4, fontSize: '0.85em', opacity: 0.8 }}>
              취소
            </span>
          </Button>
        }
        anchorOrigin={{ vertical: 'bottom', horizontal: 'center' }}
      />
    </Box>
  );
}

/**
 * Dashboard page with auth guard
 */
export default function DashboardPage() {
  return (
    <AuthGuard>
      <DashboardContent />
    </AuthGuard>
  );
}
