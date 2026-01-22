'use client';

/**
 * Shared Report page (public access)
 * @file page.tsx
 * @feature F009 - Report Sharing
 *
 * Implements:
 * - AC-051: Shared URL accessible without authentication
 * - AC-053: Shared report shows social preview cards (via metadata)
 *
 * BDD Scenarios:
 * - Shared report accessible without login
 * - Read-only view with AI disclaimer visible
 * - "Try PunchAnalytics" CTA displayed
 * - Disabled share link returns error
 */

import { useEffect, useState } from 'react';
import { useParams } from 'next/navigation';
import type { Metadata } from 'next';
import {
  Accordion,
  AccordionDetails,
  AccordionSummary,
  Alert,
  Box,
  Button,
  Card,
  CardContent,
  Chip,
  CircularProgress,
  Container,
  Grid,
  LinearProgress,
  Paper,
  Typography,
} from '@mui/material';
import CheckCircleIcon from '@mui/icons-material/CheckCircle';
import ExpandMoreIcon from '@mui/icons-material/ExpandMore';
import InfoOutlinedIcon from '@mui/icons-material/InfoOutlined';
import LockIcon from '@mui/icons-material/Lock';
import ReportProblemIcon from '@mui/icons-material/ReportProblem';
import SportsIcon from '@mui/icons-material/Sports';
import TipsAndUpdatesIcon from '@mui/icons-material/TipsAndUpdates';
import {
  getSharedReport,
  SharingError,
  type SharedReportResponse,
} from '@/lib/sharing';

/**
 * Get color for metric based on percentile
 */
function getMetricColor(percentile: number | null): 'success' | 'warning' | 'error' | 'info' {
  if (percentile === null) return 'info';
  if (percentile >= 70) return 'success';
  if (percentile >= 40) return 'warning';
  return 'error';
}

/**
 * Format timestamp seconds to display format
 */
function formatTimestamp(seconds: number): string {
  const mins = Math.floor(seconds / 60);
  const secs = Math.floor(seconds % 60);
  return `${mins}:${secs.toString().padStart(2, '0')}`;
}

/**
 * Format action type for display
 */
function formatActionType(actionType: string): string {
  const labels: Record<string, string> = {
    jab: 'Jab / 잽',
    straight: 'Straight / 스트레이트',
    hook: 'Hook / 훅',
    uppercut: 'Uppercut / 어퍼컷',
    guard_up: 'Guard Up / 가드 올림',
    guard_down: 'Guard Down / 가드 내림',
    slip: 'Slip / 슬립',
    duck: 'Duck / 덕',
    bob_weave: 'Bob & Weave / 밥앤위브',
  };
  return labels[actionType] || actionType;
}

/**
 * Format metric name for display
 */
function formatMetricName(name: string): { en: string; ko: string } {
  const labels: Record<string, { en: string; ko: string }> = {
    punch_frequency: { en: 'Punch Frequency', ko: '펀치 빈도' },
    guard_recovery_speed: { en: 'Guard Recovery', ko: '가드 회복' },
    reach_ratio: { en: 'Reach Ratio', ko: '리치 비율' },
    upper_body_tilt: { en: 'Body Tilt', ko: '상체 기울기' },
    combination_frequency: { en: 'Combo Frequency', ko: '콤비네이션 빈도' },
    defense_ratio: { en: 'Defense Ratio', ko: '방어 비율' },
  };
  return labels[name] || { en: name, ko: name };
}

/**
 * Metric Card component (read-only)
 */
function MetricCard({ name, metric }: { name: string; metric: SharedReportResponse['metrics'][string] }) {
  const labels = formatMetricName(name);
  const color = getMetricColor(metric.percentile);
  const percentValue = metric.percentile ?? 50;

  return (
    <Card
      sx={{
        height: '100%',
        borderLeft: 4,
        borderColor: `${color}.main`,
      }}
    >
      <CardContent>
        <Typography variant="caption" color="text.secondary" gutterBottom>
          {labels.en}
          <br />
          <span style={{ fontSize: '0.85em' }}>{labels.ko}</span>
        </Typography>
        <Typography variant="h5" component="div" sx={{ mt: 1, mb: 0.5 }}>
          {metric.value}
          <Typography
            component="span"
            variant="body2"
            color="text.secondary"
            sx={{ ml: 0.5 }}
          >
            {metric.unit === 'punches_per_10s' ? '/10s' : metric.unit}
          </Typography>
        </Typography>
        <LinearProgress
          variant="determinate"
          value={percentValue}
          color={color}
          sx={{ mt: 1, height: 6, borderRadius: 3 }}
        />
        {metric.percentile !== null && (
          <Typography variant="caption" color="text.secondary" sx={{ mt: 0.5, display: 'block' }}>
            {metric.percentile}th percentile
          </Typography>
        )}
      </CardContent>
    </Card>
  );
}

/**
 * Key Moment Card component (read-only)
 */
function KeyMomentCard({ stamp }: { stamp: SharedReportResponse['stamps'][number] }) {
  return (
    <Card
      sx={{
        minWidth: 140,
        maxWidth: 160,
        flexShrink: 0,
      }}
    >
      <Box
        sx={{
          height: 80,
          bgcolor: 'grey.200',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
        }}
      >
        <SportsIcon sx={{ fontSize: 32, color: 'grey.500' }} />
      </Box>
      <CardContent sx={{ p: 1.5, '&:last-child': { pb: 1.5 } }}>
        <Typography variant="caption" fontWeight="medium" noWrap>
          {formatActionType(stamp.action_type)}
        </Typography>
        <Typography variant="body2" color="primary.main" fontWeight="medium">
          {formatTimestamp(stamp.timestamp_seconds)}
        </Typography>
      </CardContent>
    </Card>
  );
}

/**
 * Get priority color for recommendation chips
 */
function getPriorityColor(priority: string): 'error' | 'warning' | 'info' {
  switch (priority) {
    case 'high':
      return 'error';
    case 'medium':
      return 'warning';
    default:
      return 'info';
  }
}

/**
 * Error display for disabled or not found shares
 */
function ShareErrorDisplay({ code, message }: { code: string; message: string }) {
  const isDisabled = code === 'SHARE_DISABLED';

  return (
    <Container maxWidth="sm" sx={{ py: 8, textAlign: 'center' }}>
      <Paper sx={{ p: 4 }}>
        <LockIcon sx={{ fontSize: 64, color: 'action.disabled', mb: 2 }} />
        <Typography variant="h5" gutterBottom>
          {isDisabled ? 'Sharing Disabled' : 'Report Not Found'}
        </Typography>
        <Typography variant="h6" color="text.secondary" gutterBottom>
          {isDisabled ? '공유 비활성화됨' : '보고서를 찾을 수 없습니다'}
        </Typography>
        <Typography variant="body1" color="text.secondary" sx={{ mb: 3 }}>
          {isDisabled
            ? 'The owner has disabled sharing for this report.'
            : 'This share link may have expired or been removed.'}
        </Typography>
        <Typography variant="body2" color="text.secondary" sx={{ mb: 3 }}>
          {isDisabled
            ? '보고서 소유자가 공유를 비활성화했습니다.'
            : '이 공유 링크가 만료되었거나 삭제되었을 수 있습니다.'}
        </Typography>
        <Button
          variant="contained"
          color="primary"
          href="/"
          size="large"
        >
          Try PunchAnalytics
        </Button>
      </Paper>
    </Container>
  );
}

/**
 * Shared Report Page (public)
 * AC-051: Shared URL accessible without authentication
 */
export default function SharedReportPage() {
  const params = useParams();
  const shareToken = params.token as string;

  // State
  const [report, setReport] = useState<SharedReportResponse | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<{ code: string; message: string } | null>(null);

  // Expanded sections state
  const [expandedSections, setExpandedSections] = useState({
    strengths: true,
    weaknesses: true,
    recommendations: true,
  });

  // Fetch shared report
  useEffect(() => {
    if (!shareToken) return;

    const fetchReport = async () => {
      setIsLoading(true);
      setError(null);

      try {
        const data = await getSharedReport(shareToken);
        setReport(data);
      } catch (err) {
        if (err instanceof SharingError) {
          setError({ code: err.code, message: err.message });
        } else {
          setError({ code: 'UNKNOWN', message: 'Failed to load report' });
        }
      } finally {
        setIsLoading(false);
      }
    };

    fetchReport();
  }, [shareToken]);

  // Handle section toggle
  const handleSectionToggle = (section: keyof typeof expandedSections) => () => {
    setExpandedSections((prev) => ({
      ...prev,
      [section]: !prev[section],
    }));
  };

  // Loading state
  if (isLoading) {
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

  // Error state
  if (error) {
    return <ShareErrorDisplay code={error.code} message={error.message} />;
  }

  // No report
  if (!report) {
    return (
      <ShareErrorDisplay
        code="SHARE_NOT_FOUND"
        message="Report not found"
      />
    );
  }

  return (
    <Container
      maxWidth="lg"
      sx={{
        py: { xs: 2, md: 4 },
        px: { xs: 2, md: 3 },
      }}
    >
      {/* Header - Read-only indicator */}
      <Box sx={{ display: 'flex', alignItems: 'center', mb: 3 }}>
        <Typography variant="h5" component="h1" sx={{ flex: 1 }}>
          Analysis Report
          <Typography
            component="span"
            variant="body2"
            color="text.secondary"
            sx={{ ml: 1 }}
          >
            / 분석 보고서
          </Typography>
        </Typography>
        <Chip
          label="Shared View / 공유 보기"
          color="primary"
          variant="outlined"
          size="small"
        />
      </Box>

      {/* Summary Section */}
      <Paper sx={{ p: 3, mb: 3, textAlign: 'center' }}>
        {/* Performance Score */}
        <Box
          sx={{
            position: 'relative',
            display: 'inline-flex',
            mb: 2,
          }}
        >
          <CircularProgress
            variant="determinate"
            value={report.performance_score ?? 0}
            size={100}
            thickness={4}
            color={
              (report.performance_score ?? 0) >= 70
                ? 'success'
                : (report.performance_score ?? 0) >= 40
                  ? 'warning'
                  : 'error'
            }
          />
          <Box
            sx={{
              top: 0,
              left: 0,
              bottom: 0,
              right: 0,
              position: 'absolute',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
            }}
          >
            <Typography variant="h4" component="div">
              {report.performance_score ?? '-'}
            </Typography>
          </Box>
        </Box>

        <Typography variant="h6" gutterBottom>
          Performance Score / 수행 점수
        </Typography>

        {/* Overall Assessment */}
        <Typography
          variant="body1"
          color="text.secondary"
          sx={{ maxWidth: 600, mx: 'auto' }}
        >
          {report.overall_assessment}
        </Typography>

        {/* Report date */}
        {report.created_at && (
          <Typography variant="caption" color="text.secondary" sx={{ mt: 2, display: 'block' }}>
            {new Date(report.created_at).toLocaleDateString('ko-KR', {
              year: 'numeric',
              month: 'long',
              day: 'numeric',
            })}
          </Typography>
        )}
      </Paper>

      {/* Metrics Grid */}
      <Typography variant="h6" gutterBottom sx={{ mb: 2 }}>
        Key Metrics / 주요 지표
      </Typography>
      <Grid container spacing={2} sx={{ mb: 4 }}>
        {Object.entries(report.metrics).map(([name, metric]) => (
          <Grid item xs={6} md={3} key={name}>
            <MetricCard name={name} metric={metric} />
          </Grid>
        ))}
      </Grid>

      {/* Key Moments */}
      {report.stamps.length > 0 && (
        <Box sx={{ mb: 4 }}>
          <Typography variant="h6" gutterBottom sx={{ mb: 2 }}>
            Key Moments / 주요 순간
          </Typography>
          <Box
            sx={{
              display: 'flex',
              gap: 2,
              overflowX: 'auto',
              pb: 1,
              '&::-webkit-scrollbar': { height: 6 },
              '&::-webkit-scrollbar-track': { bgcolor: 'grey.200', borderRadius: 3 },
              '&::-webkit-scrollbar-thumb': { bgcolor: 'grey.400', borderRadius: 3 },
            }}
          >
            {report.stamps.map((stamp) => (
              <KeyMomentCard key={stamp.stamp_id} stamp={stamp} />
            ))}
          </Box>
        </Box>
      )}

      {/* Strengths Section */}
      <Accordion
        expanded={expandedSections.strengths}
        onChange={handleSectionToggle('strengths')}
        sx={{ mb: 1 }}
      >
        <AccordionSummary expandIcon={<ExpandMoreIcon />}>
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
            <CheckCircleIcon color="success" />
            <Typography variant="h6">
              Strengths / 강점
              <Chip
                label={report.strengths.length}
                size="small"
                sx={{ ml: 1, height: 20 }}
              />
            </Typography>
          </Box>
        </AccordionSummary>
        <AccordionDetails>
          {report.strengths.map((strength, index) => (
            <Box key={index} sx={{ display: 'flex', gap: 1.5, mb: 2 }}>
              <CheckCircleIcon color="success" sx={{ mt: 0.3, flexShrink: 0 }} />
              <Box>
                <Typography variant="subtitle2">{strength.title}</Typography>
                <Typography variant="body2" color="text.secondary">
                  {strength.description}
                </Typography>
              </Box>
            </Box>
          ))}
        </AccordionDetails>
      </Accordion>

      {/* Weaknesses Section */}
      <Accordion
        expanded={expandedSections.weaknesses}
        onChange={handleSectionToggle('weaknesses')}
        sx={{ mb: 1 }}
      >
        <AccordionSummary expandIcon={<ExpandMoreIcon />}>
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
            <ReportProblemIcon color="warning" />
            <Typography variant="h6">
              Areas for Improvement / 개선점
              <Chip
                label={report.weaknesses.length}
                size="small"
                sx={{ ml: 1, height: 20 }}
              />
            </Typography>
          </Box>
        </AccordionSummary>
        <AccordionDetails>
          {report.weaknesses.map((weakness, index) => (
            <Box key={index} sx={{ display: 'flex', gap: 1.5, mb: 2 }}>
              <ReportProblemIcon color="warning" sx={{ mt: 0.3, flexShrink: 0 }} />
              <Box>
                <Typography variant="subtitle2">{weakness.title}</Typography>
                <Typography variant="body2" color="text.secondary">
                  {weakness.description}
                </Typography>
              </Box>
            </Box>
          ))}
        </AccordionDetails>
      </Accordion>

      {/* Recommendations Section */}
      <Accordion
        expanded={expandedSections.recommendations}
        onChange={handleSectionToggle('recommendations')}
        sx={{ mb: 3 }}
      >
        <AccordionSummary expandIcon={<ExpandMoreIcon />}>
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
            <TipsAndUpdatesIcon color="primary" />
            <Typography variant="h6">
              Recommendations / 권장 사항
              <Chip
                label={report.recommendations.length}
                size="small"
                sx={{ ml: 1, height: 20 }}
              />
            </Typography>
          </Box>
        </AccordionSummary>
        <AccordionDetails>
          {report.recommendations.map((rec, index) => (
            <Box key={index} sx={{ display: 'flex', gap: 1.5, mb: 2 }}>
              <TipsAndUpdatesIcon color="primary" sx={{ mt: 0.3, flexShrink: 0 }} />
              <Box sx={{ flex: 1 }}>
                <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 0.5 }}>
                  <Typography variant="subtitle2">{rec.title}</Typography>
                  <Chip
                    label={rec.priority}
                    size="small"
                    color={getPriorityColor(rec.priority)}
                    sx={{ height: 20, fontSize: '0.7rem' }}
                  />
                </Box>
                <Typography variant="body2" color="text.secondary">
                  {rec.description}
                </Typography>
                {rec.drill_type && (
                  <Chip
                    label={rec.drill_type}
                    size="small"
                    variant="outlined"
                    sx={{ mt: 1, height: 20, fontSize: '0.7rem' }}
                  />
                )}
              </Box>
            </Box>
          ))}
        </AccordionDetails>
      </Accordion>

      {/* AI Disclaimer - Required */}
      <Paper
        sx={{
          p: 2,
          bgcolor: 'grey.100',
          display: 'flex',
          alignItems: 'flex-start',
          gap: 1.5,
          mb: 3,
        }}
      >
        <InfoOutlinedIcon color="action" sx={{ mt: 0.3, flexShrink: 0 }} />
        <Typography variant="body2" color="text.secondary">
          {report.disclaimer}
          <br />
          <span style={{ fontSize: '0.9em' }}>
            이 AI 분석은 훈련 목적으로만 제공되며, 전문 코칭을 대체하지 않습니다.
            항상 적절한 감독 하에 훈련하세요.
          </span>
        </Typography>
      </Paper>

      {/* Try PunchAnalytics CTA - BDD requirement */}
      <Paper
        sx={{
          p: 3,
          textAlign: 'center',
          bgcolor: 'primary.main',
          color: 'primary.contrastText',
        }}
      >
        <Typography variant="h6" gutterBottom>
          Get your own boxing analysis
        </Typography>
        <Typography variant="body2" sx={{ mb: 2, opacity: 0.9 }}>
          Upload your training video and get AI-powered feedback
          <br />
          훈련 영상을 업로드하고 AI 기반 피드백을 받아보세요
        </Typography>
        <Button
          variant="contained"
          color="secondary"
          size="large"
          href="/"
          sx={{ fontWeight: 600 }}
        >
          Try PunchAnalytics
        </Button>
      </Paper>
    </Container>
  );
}
