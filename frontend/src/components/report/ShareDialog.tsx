'use client';

/**
 * Share Dialog component for report sharing
 * @file ShareDialog.tsx
 * @feature F009 - Report Sharing
 *
 * Implements:
 * - AC-049: Share button shows on report page (default private)
 * - AC-050: Enable sharing generates unique URL
 * - AC-052: Copy Link copies to clipboard with confirmation
 * - AC-054: Disabling sharing invalidates the URL
 * - AC-055: Re-enabling generates new unique URL
 *
 * BDD Scenarios:
 * - Report shows share button in private state
 * - User enables sharing and gets unique URL
 * - User copies share link to clipboard
 * - User disables sharing
 * - User re-enables sharing gets new URL
 */

import { useCallback, useEffect, useState } from 'react';
import {
  Alert,
  Box,
  Button,
  CircularProgress,
  Dialog,
  DialogActions,
  DialogContent,
  DialogTitle,
  IconButton,
  Snackbar,
  Switch,
  TextField,
  Tooltip,
  Typography,
} from '@mui/material';
import CloseIcon from '@mui/icons-material/Close';
import ContentCopyIcon from '@mui/icons-material/ContentCopy';
import LinkIcon from '@mui/icons-material/Link';
import ShareIcon from '@mui/icons-material/Share';
import {
  copyToClipboard,
  disableSharing,
  enableSharing,
  getShareStatus,
  SharingError,
  type ShareStatusResponse,
} from '@/lib/sharing';

interface ShareDialogProps {
  reportId: string;
  accessToken: string;
  open: boolean;
  onClose: () => void;
}

/**
 * Share Dialog component
 *
 * Displays sharing controls with toggle, URL display, and copy button.
 */
export function ShareDialog({
  reportId,
  accessToken,
  open,
  onClose,
}: ShareDialogProps) {
  // State
  const [shareStatus, setShareStatus] = useState<ShareStatusResponse | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [isToggling, setIsToggling] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [showCopiedToast, setShowCopiedToast] = useState(false);

  // Fetch share status when dialog opens
  useEffect(() => {
    if (!open || !accessToken || !reportId) return;

    const fetchStatus = async () => {
      setIsLoading(true);
      setError(null);

      try {
        const status = await getShareStatus(accessToken, reportId);
        setShareStatus(status);
      } catch (err) {
        if (err instanceof SharingError) {
          setError(err.message);
        } else {
          setError('Failed to load sharing status');
        }
      } finally {
        setIsLoading(false);
      }
    };

    fetchStatus();
  }, [open, accessToken, reportId]);

  // Handle toggle sharing
  // AC-050: Enable sharing generates unique URL
  // AC-054: Disabling sharing invalidates the URL
  // AC-055: Re-enabling generates new unique URL
  const handleToggleSharing = useCallback(async () => {
    if (!accessToken || !reportId) return;

    setIsToggling(true);
    setError(null);

    try {
      if (shareStatus?.share_enabled) {
        // Disable sharing
        const result = await disableSharing(accessToken, reportId);
        setShareStatus({
          share_enabled: result.share_enabled,
          share_token: null,
          share_url: null,
        });
      } else {
        // Enable sharing - generates new URL each time
        const result = await enableSharing(accessToken, reportId);
        setShareStatus({
          share_enabled: result.share_enabled,
          share_token: result.share_token,
          share_url: result.share_url,
        });
      }
    } catch (err) {
      if (err instanceof SharingError) {
        setError(err.message);
      } else {
        setError('Failed to update sharing settings');
      }
    } finally {
      setIsToggling(false);
    }
  }, [accessToken, reportId, shareStatus?.share_enabled]);

  // Handle copy link
  // AC-052: Copy Link copies to clipboard with confirmation
  const handleCopyLink = useCallback(async () => {
    if (!shareStatus?.share_url) return;

    try {
      await copyToClipboard(shareStatus.share_url);
      setShowCopiedToast(true);
    } catch {
      setError('Failed to copy link');
    }
  }, [shareStatus?.share_url]);

  // Handle close toast
  // BDD: Toast disappears after 4 seconds
  const handleCloseToast = useCallback(() => {
    setShowCopiedToast(false);
  }, []);

  return (
    <>
      <Dialog open={open} onClose={onClose} maxWidth="sm" fullWidth>
        <DialogTitle>
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
            <ShareIcon />
            <Typography variant="h6" component="span">
              Share Report
              <Typography
                component="span"
                variant="body2"
                color="text.secondary"
                sx={{ ml: 1 }}
              >
                / 보고서 공유
              </Typography>
            </Typography>
          </Box>
          <IconButton
            aria-label="close"
            onClick={onClose}
            sx={{
              position: 'absolute',
              right: 8,
              top: 8,
              color: (theme) => theme.palette.grey[500],
            }}
          >
            <CloseIcon />
          </IconButton>
        </DialogTitle>

        <DialogContent>
          {/* Loading state */}
          {isLoading && (
            <Box sx={{ display: 'flex', justifyContent: 'center', py: 4 }}>
              <CircularProgress />
            </Box>
          )}

          {/* Error state */}
          {error && (
            <Alert severity="error" sx={{ mb: 2 }}>
              {error}
            </Alert>
          )}

          {/* Share controls */}
          {!isLoading && shareStatus && (
            <>
              {/* Enable sharing toggle */}
              <Box
                sx={{
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'space-between',
                  mb: 3,
                }}
              >
                <Box>
                  <Typography variant="subtitle1">
                    Enable sharing
                    <Typography
                      component="span"
                      variant="body2"
                      color="text.secondary"
                      sx={{ ml: 1 }}
                    >
                      / 공유 활성화
                    </Typography>
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    {shareStatus.share_enabled
                      ? 'Anyone with the link can view this report'
                      : 'Only you can view this report'}
                  </Typography>
                </Box>
                <Switch
                  checked={shareStatus.share_enabled}
                  onChange={handleToggleSharing}
                  disabled={isToggling}
                  inputProps={{ 'aria-label': 'Enable sharing toggle' }}
                />
              </Box>

              {/* Share URL display */}
              {shareStatus.share_enabled && shareStatus.share_url && (
                <Box sx={{ mb: 2 }}>
                  <Typography variant="body2" color="text.secondary" sx={{ mb: 1 }}>
                    Share link / 공유 링크
                  </Typography>
                  <Box sx={{ display: 'flex', gap: 1 }}>
                    <TextField
                      fullWidth
                      size="small"
                      value={shareStatus.share_url}
                      InputProps={{
                        readOnly: true,
                        startAdornment: (
                          <LinkIcon sx={{ color: 'action.active', mr: 1 }} />
                        ),
                      }}
                    />
                    <Tooltip title="Copy link / 링크 복사">
                      <Button
                        variant="contained"
                        onClick={handleCopyLink}
                        startIcon={<ContentCopyIcon />}
                        sx={{ minWidth: 120 }}
                      >
                        Copy
                      </Button>
                    </Tooltip>
                  </Box>
                </Box>
              )}

              {/* Disabled state message */}
              {!shareStatus.share_enabled && (
                <Alert severity="info" icon={<ShareIcon />}>
                  <Typography variant="body2">
                    Turn on sharing to generate a public link that anyone can access.
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    공유를 활성화하면 누구나 접근할 수 있는 공개 링크가 생성됩니다.
                  </Typography>
                </Alert>
              )}
            </>
          )}
        </DialogContent>

        <DialogActions>
          <Button onClick={onClose}>Close / 닫기</Button>
        </DialogActions>
      </Dialog>

      {/* Copy confirmation toast - AC-052 */}
      <Snackbar
        open={showCopiedToast}
        autoHideDuration={4000}
        onClose={handleCloseToast}
        message="Link copied to clipboard / 링크가 클립보드에 복사되었습니다"
        anchorOrigin={{ vertical: 'bottom', horizontal: 'center' }}
      />
    </>
  );
}
