/**
 * Dashboard module exports
 * @file index.ts
 * @feature F010 - Report History Dashboard
 */

export {
  DashboardError,
  deleteReport,
  formatAnalyzedDate,
  getReportList,
  restoreReport,
  type DeleteReportResponse,
  type ReportListItem,
  type ReportListResponse,
  type RestoreReportResponse,
} from './api';
