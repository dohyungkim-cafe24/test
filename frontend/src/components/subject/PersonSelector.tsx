'use client';

/**
 * Person selector component for thumbnail
 * @file PersonSelector.tsx
 * @feature F003 - Subject Selection
 *
 * BDD Scenarios:
 * - User selects subject from thumbnail (blue selection ring + checkmark)
 * - User changes selection before confirmation
 */

import { useCallback } from 'react';
import { Box, alpha, useTheme } from '@mui/material';
import CheckCircleIcon from '@mui/icons-material/CheckCircle';
import { ThumbnailResponse, DetectedPerson, BoundingBox } from '@/lib/subject';

export interface PersonSelectorProps {
  /** Thumbnail with detected persons */
  thumbnail: ThumbnailResponse;
  /** Currently selected person ID (null if none) */
  selectedPersonId: string | null;
  /** Called when a person is selected */
  onPersonSelect: (personId: string) => void;
}

/**
 * Displays a thumbnail with clickable person bounding boxes
 *
 * AC-014: Tap on person highlights with selection indicator
 * AC-016: Selection can be changed before confirmation
 */
export function PersonSelector({
  thumbnail,
  selectedPersonId,
  onPersonSelect,
}: PersonSelectorProps) {
  const theme = useTheme();

  const handlePersonClick = useCallback(
    (e: React.MouseEvent, personId: string) => {
      e.stopPropagation();
      onPersonSelect(personId);
    },
    [onPersonSelect]
  );

  const handleKeyDown = useCallback(
    (e: React.KeyboardEvent, personId: string) => {
      if (e.key === 'Enter' || e.key === ' ') {
        e.preventDefault();
        onPersonSelect(personId);
      }
    },
    [onPersonSelect]
  );

  return (
    <Box
      sx={{
        position: 'relative',
        width: '100%',
        aspectRatio: '16/9',
        borderRadius: 1,
        overflow: 'hidden',
        bgcolor: 'grey.900',
      }}
    >
      {/* Thumbnail image */}
      <Box
        component="img"
        src={thumbnail.image_url}
        alt={`Frame at ${thumbnail.timestamp_seconds.toFixed(1)}s`}
        sx={{
          width: '100%',
          height: '100%',
          objectFit: 'cover',
        }}
      />

      {/* Person bounding boxes */}
      {thumbnail.detected_persons.map((person) => {
        const isSelected = person.person_id === selectedPersonId;

        return (
          <PersonBoundingBox
            key={person.person_id}
            person={person}
            isSelected={isSelected}
            onClick={(e) => handlePersonClick(e, person.person_id)}
            onKeyDown={(e) => handleKeyDown(e, person.person_id)}
          />
        );
      })}
    </Box>
  );
}

interface PersonBoundingBoxProps {
  person: DetectedPerson;
  isSelected: boolean;
  onClick: (e: React.MouseEvent) => void;
  onKeyDown: (e: React.KeyboardEvent) => void;
}

/**
 * Clickable bounding box overlay for a detected person
 */
function PersonBoundingBox({
  person,
  isSelected,
  onClick,
  onKeyDown,
}: PersonBoundingBoxProps) {
  const theme = useTheme();
  const { bounding_box } = person;

  // Convert pixel coordinates to percentages for responsive positioning
  // Assuming the thumbnail aspect ratio and coordinates match
  // The backend provides normalized or absolute coordinates - adjust as needed

  return (
    <Box
      role="button"
      tabIndex={0}
      aria-label={`Select person ${person.person_id}`}
      aria-pressed={isSelected}
      onClick={onClick}
      onKeyDown={onKeyDown}
      sx={{
        position: 'absolute',
        left: `${bounding_box.x}%`,
        top: `${bounding_box.y}%`,
        width: `${bounding_box.width}%`,
        height: `${bounding_box.height}%`,
        border: isSelected
          ? `3px solid ${theme.palette.primary.main}`
          : `2px solid ${alpha(theme.palette.common.white, 0.6)}`,
        borderRadius: 1,
        cursor: 'pointer',
        transition: theme.transitions.create(['border-color', 'border-width'], {
          duration: theme.transitions.duration.short,
        }),
        '&:hover': {
          borderColor: isSelected
            ? theme.palette.primary.main
            : theme.palette.primary.light,
          borderWidth: isSelected ? 3 : 2,
        },
        '&:focus-visible': {
          outline: `2px solid ${theme.palette.primary.main}`,
          outlineOffset: 2,
        },
      }}
    >
      {/* Selection checkmark indicator */}
      {isSelected && (
        <CheckCircleIcon
          sx={{
            position: 'absolute',
            top: -12,
            right: -12,
            fontSize: 24,
            color: theme.palette.primary.main,
            bgcolor: 'white',
            borderRadius: '50%',
          }}
        />
      )}
    </Box>
  );
}
