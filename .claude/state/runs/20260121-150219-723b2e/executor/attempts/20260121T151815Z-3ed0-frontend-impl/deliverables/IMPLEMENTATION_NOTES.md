# Implementation Notes - F003 Subject Selection (Frontend)

## Summary

Implemented the frontend components for F003 Subject Selection, including API client, UI components (ThumbnailGrid, PersonSelector), and the subject selection page. All code follows existing patterns from F002 Video Upload.

## Inputs

Files consulted:
- `/projects/punch-analytics/frontend/src/lib/upload/api.ts` - API client pattern
- `/projects/punch-analytics/frontend/src/app/(protected)/upload/page.tsx` - Page pattern
- `/projects/punch-analytics/frontend/src/components/upload/UploadDropzone.tsx` - Component pattern
- `/projects/punch-analytics/frontend/src/lib/auth/hooks.ts` - Auth hooks
- `/projects/punch-analytics/backend/api/schemas/subject.py` - API contract
- `/projects/punch-analytics/backend/api/routers/subject.py` - API endpoints
- `/projects/punch-analytics/specs/bdd/subject-selection.feature` - BDD scenarios

## Approach

1. **API Client** (`lib/subject/api.ts`)
   - Matches backend schema types
   - `getThumbnails(accessToken, videoId)` - Fetches thumbnails for subject selection
   - `selectSubject(accessToken, videoId, thumbnailId, personId)` - Confirms subject selection
   - Error handling with `SubjectError` class (same pattern as `UploadError`)

2. **ThumbnailGrid Component** (`components/subject/ThumbnailGrid.tsx`)
   - Displays 6-9 thumbnail frames in a responsive grid
   - Shows skeleton placeholders during loading
   - Delegates person selection to PersonSelector

3. **PersonSelector Component** (`components/subject/PersonSelector.tsx`)
   - Renders thumbnail image with clickable bounding boxes
   - Blue selection ring + checkmark for selected person
   - Keyboard accessible (Enter/Space to select)

4. **Subject Selection Page** (`app/(protected)/subject/[videoId]/page.tsx`)
   - Polling for processing status (2s interval, max 2 minutes)
   - Auto-selects single person (AC-017)
   - Shows loading state with skeleton grid
   - Shows "No subjects detected" empty state
   - Shows "Tap on yourself" instruction for multi-person
   - Confirm button navigates to body-specs page

## Changes

### Added Files
- `frontend/src/lib/subject/api.ts` - API client
- `frontend/src/lib/subject/index.ts` - Module exports
- `frontend/src/components/subject/ThumbnailGrid.tsx` - Grid component
- `frontend/src/components/subject/PersonSelector.tsx` - Person selection component
- `frontend/src/components/subject/index.ts` - Component exports
- `frontend/src/app/(protected)/subject/[videoId]/page.tsx` - Selection page
- `frontend/src/lib/subject/__tests__/api.test.ts` - API unit tests
- `frontend/jest.config.js` - Jest configuration
- `frontend/jest.setup.js` - Jest setup

### Modified Files
- `frontend/tsconfig.json` - Added jest types
- `frontend/package.json` - @types/jest added via npm install

## Decisions

1. **Polling vs WebSocket**: Chose polling for simplicity since backend doesn't have WebSocket support yet. 2s interval balances responsiveness with server load.

2. **Bounding box coordinates**: Used percentage-based positioning to support responsive layouts. Backend may need adjustment if it returns absolute pixel coordinates.

3. **Korean + English copy**: Both languages inline following BDD scenarios (e.g., "Tap on yourself / 영상에서 본인을 탭하세요").

4. **Navigation path**: Used `/body-specs/{videoId}` as the next page (consistent with the feature flow).

## Risks / Follow-ups

1. **Bounding box coordinate system**: If backend returns absolute pixel coordinates instead of percentages, PersonSelector needs adjustment to convert coordinates based on thumbnail dimensions.

2. **No React Query**: Used direct fetch + useState/useEffect. Could migrate to React Query (useQuery) for caching and deduplication if needed.

3. **No E2E tests yet**: Unit tests added for API client. E2E tests will be needed for full BDD scenario coverage.

4. **Thumbnail URL format**: Assumes backend returns full URLs. May need adjustment if relative paths are returned.
