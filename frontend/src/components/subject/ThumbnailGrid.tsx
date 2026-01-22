'use client';

/**
 * Thumbnail grid component for subject selection
 * @file ThumbnailGrid.tsx
 * @feature F003 - Subject Selection
 *
 * BDD Scenarios:
 * - Thumbnail grid displays extracted frames
 * - Skeleton placeholders in loading state
 */

import { Box, Grid, Skeleton, Typography } from '@mui/material';
import { ThumbnailResponse } from '@/lib/subject';
import { PersonSelector } from './PersonSelector';

export interface ThumbnailGridProps {
  /** Thumbnails to display */
  thumbnails: ThumbnailResponse[];
  /** Currently selected person */
  selectedPerson: {
    thumbnailId: string;
    personId: string;
  } | null;
  /** Called when a person is selected */
  onPersonSelect: (thumbnailId: string, personId: string) => void;
  /** Whether the grid is loading */
  isLoading?: boolean;
}

/**
 * Grid of thumbnail frames with person selection
 *
 * AC-013: Thumbnail grid displays after upload completes
 */
export function ThumbnailGrid({
  thumbnails,
  selectedPerson,
  onPersonSelect,
  isLoading = false,
}: ThumbnailGridProps) {
  // Show skeleton placeholders during loading
  if (isLoading) {
    return (
      <Grid container spacing={2}>
        {Array.from({ length: 6 }).map((_, index) => (
          <Grid item xs={6} sm={4} key={`skeleton-${index}`}>
            <Skeleton
              variant="rectangular"
              width="100%"
              sx={{
                aspectRatio: '16/9',
                borderRadius: 1,
              }}
            />
          </Grid>
        ))}
      </Grid>
    );
  }

  // Empty state handled by parent
  if (thumbnails.length === 0) {
    return null;
  }

  return (
    <Grid container spacing={2}>
      {thumbnails.map((thumbnail) => (
        <Grid item xs={6} sm={4} key={thumbnail.thumbnail_id}>
          <PersonSelector
            thumbnail={thumbnail}
            selectedPersonId={
              selectedPerson?.thumbnailId === thumbnail.thumbnail_id
                ? selectedPerson.personId
                : null
            }
            onPersonSelect={(personId) =>
              onPersonSelect(thumbnail.thumbnail_id, personId)
            }
          />
        </Grid>
      ))}
    </Grid>
  );
}
