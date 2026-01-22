# Implementation Notes: F004 Body Specification Frontend

## Summary
Implemented the frontend components for F004 Body Specification Input feature, including API client and form page with real-time validation, prefill support, and bilingual UI.

## Inputs
- `specs/bdd/body-specs.feature` - BDD scenarios for body specs
- `docs/ux/COPY.md` - UI copy for Korean + English text
- `docs/ux/UX_CONTRACT.md` - UX requirements (mobile-first, M3, validation)
- `backend/api/schemas/body_specs.py` - API schemas
- `backend/api/routers/body_specs.py` - API endpoint definitions
- `frontend/src/lib/subject/api.ts` - Reference pattern for API client
- `frontend/src/app/(protected)/subject/[videoId]/page.tsx` - Reference pattern for form page

## Approach
1. **API Client** (`lib/body-specs/api.ts`)
   - Created `submitBodySpecs()` for POST /analysis/body-specs/{video_id}
   - Created `getPrefillSpecs()` for GET /analysis/body-specs/prefill
   - Custom `BodySpecsError` class with error codes matching backend
   - TypeScript types matching backend Pydantic schemas

2. **Form Page** (`app/(protected)/body-specs/[videoId]/page.tsx`)
   - Material UI components following M3 design system
   - Real-time field validation with red border on errors
   - Height validation: 100-250cm (AC-019)
   - Weight validation: 30-200kg (AC-019)
   - Decimal rounding on blur (BDD scenario)
   - Non-numeric character stripping
   - Pre-fill from API on mount (AC-024)
   - All fields required for submission
   - Submit button disabled until form valid
   - Loading states during prefill and submission
   - Error snackbar for API failures
   - Korean + English bilingual copy

3. **Unit Tests** (`lib/body-specs/__tests__/api.test.ts`)
   - 9 test cases covering happy paths and error scenarios
   - Mock fetch for external boundary testing

## Changes

### New Files
- `frontend/src/lib/body-specs/api.ts` - API client with submitBodySpecs and getPrefillSpecs
- `frontend/src/lib/body-specs/index.ts` - Module exports
- `frontend/src/lib/body-specs/__tests__/api.test.ts` - API client unit tests
- `frontend/src/app/(protected)/body-specs/[videoId]/page.tsx` - Body specs form page

## Decisions

### Validation Strategy
- **Client-side validation** mirrors backend constraints (100-250cm, 30-200kg)
- **Real-time validation** on blur (not on every keystroke) to avoid UX friction
- **Decimal rounding** to integers on blur to match backend integer fields
- **Non-numeric stripping** allows paste of "175cm" -> "175"

### State Management
- React useState for form state (simple form, no need for form libraries)
- Separate `touched` state to show errors only after interaction
- `fieldErrors` object for per-field error messages

### UX Patterns
- Matches existing subject selection page pattern
- Uses MUI TextField, Select, Button, Snackbar
- Disabled submit until all validations pass
- Loading spinner during prefill fetch and submission

### Error Handling
- API errors display via Snackbar (non-blocking)
- Pre-fill failures are non-fatal (silent console.error)
- Validation errors show inline with red border

## Risks / Follow-ups
1. **Processing page not yet implemented** - Navigation to `/processing/${videoId}` after submit will 404 until F005 is built
2. **No integration test** - Would need backend running for full E2E test
3. **Accessibility** - Should verify with screen reader (focus management, aria labels present)
4. **Responsive testing** - Should verify 375px viewport in runtime
