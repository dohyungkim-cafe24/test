'use client';

/**
 * Delete confirmation dialog component
 * @file DeleteConfirmDialog.tsx
 * @feature F010 - Report History Dashboard
 *
 * Implements:
 * - AC-059: Delete report shows confirmation dialog
 *
 * BDD Scenarios:
 * - User deletes report with confirmation dialog
 * - The dialog should say "Delete this report?"
 * - The dialog should warn "This action cannot be undone."
 */

import {
  Button,
  Dialog,
  DialogActions,
  DialogContent,
  DialogContentText,
  DialogTitle,
  CircularProgress,
} from '@mui/material';
import WarningAmberIcon from '@mui/icons-material/WarningAmber';

interface DeleteConfirmDialogProps {
  open: boolean;
  onClose: () => void;
  onConfirm: () => Promise<void>;
  isDeleting: boolean;
}

/**
 * Confirmation dialog for report deletion
 *
 * AC-059: Delete report shows confirmation dialog
 * BDD: Dialog shows "Delete this report?" and warning message
 */
export function DeleteConfirmDialog({
  open,
  onClose,
  onConfirm,
  isDeleting,
}: DeleteConfirmDialogProps) {
  return (
    <Dialog
      open={open}
      onClose={onClose}
      aria-labelledby="delete-dialog-title"
      aria-describedby="delete-dialog-description"
    >
      <DialogTitle
        id="delete-dialog-title"
        sx={{ display: 'flex', alignItems: 'center', gap: 1 }}
      >
        <WarningAmberIcon color="warning" />
        Delete this report?
        <span style={{ marginLeft: 8, fontSize: '0.7em', opacity: 0.7 }}>
          이 보고서를 삭제하시겠습니까?
        </span>
      </DialogTitle>
      <DialogContent>
        <DialogContentText id="delete-dialog-description">
          This action cannot be undone.
          <br />
          <span style={{ fontSize: '0.9em' }}>
            이 작업은 취소할 수 없습니다.
          </span>
        </DialogContentText>
      </DialogContent>
      <DialogActions>
        <Button onClick={onClose} disabled={isDeleting}>
          Cancel
          <span style={{ marginLeft: 4, fontSize: '0.85em', opacity: 0.7 }}>
            취소
          </span>
        </Button>
        <Button
          onClick={onConfirm}
          color="error"
          variant="contained"
          disabled={isDeleting}
          startIcon={isDeleting ? <CircularProgress size={16} color="inherit" /> : undefined}
        >
          {isDeleting ? 'Deleting...' : 'Delete'}
          {!isDeleting && (
            <span style={{ marginLeft: 4, fontSize: '0.85em', opacity: 0.7 }}>
              삭제
            </span>
          )}
        </Button>
      </DialogActions>
    </Dialog>
  );
}
