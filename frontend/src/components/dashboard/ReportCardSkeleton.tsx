'use client';

/**
 * Report card skeleton component for loading state
 * @file ReportCardSkeleton.tsx
 * @feature F010 - Report History Dashboard
 *
 * BDD Scenario:
 * - Dashboard loading state shows skeleton cards with pulse animation
 * - I should see 3 skeleton list items
 * - The skeletons should have pulse animation
 */

import { Box, Card, CardContent, Skeleton } from '@mui/material';

/**
 * Skeleton loading card for report list
 *
 * BDD: Skeletons should have pulse animation (default Skeleton behavior)
 */
export function ReportCardSkeleton() {
  return (
    <Card
      sx={{
        display: 'flex',
        flexDirection: { xs: 'column', sm: 'row' },
        height: { xs: 'auto', sm: 140 },
      }}
    >
      {/* Thumbnail skeleton */}
      <Skeleton
        variant="rectangular"
        animation="pulse"
        sx={{
          width: { xs: '100%', sm: 180 },
          height: { xs: 120, sm: 140 },
          flexShrink: 0,
        }}
      />

      <CardContent sx={{ flex: 1, py: 2 }}>
        {/* Date skeleton */}
        <Skeleton
          variant="text"
          animation="pulse"
          width="40%"
          height={24}
          sx={{ mb: 1 }}
        />
        <Skeleton
          variant="text"
          animation="pulse"
          width="30%"
          height={20}
          sx={{ mb: 2 }}
        />

        {/* Summary skeleton */}
        <Skeleton
          variant="text"
          animation="pulse"
          width="60%"
          height={28}
        />
        <Skeleton
          variant="text"
          animation="pulse"
          width="50%"
          height={24}
        />
      </CardContent>
    </Card>
  );
}

/**
 * Multiple skeleton cards for loading state
 *
 * BDD: I should see 3 skeleton list items
 */
export function ReportListSkeleton() {
  return (
    <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2 }}>
      <ReportCardSkeleton />
      <ReportCardSkeleton />
      <ReportCardSkeleton />
    </Box>
  );
}
