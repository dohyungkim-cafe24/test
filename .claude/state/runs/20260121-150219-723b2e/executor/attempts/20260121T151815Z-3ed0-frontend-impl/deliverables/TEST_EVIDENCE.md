# Test Evidence - F003 Subject Selection (Frontend)

## Inputs

Tested against:
- Backend API schemas: `backend/api/schemas/subject.py`
- BDD scenarios: `specs/bdd/subject-selection.feature`

## Commands

### TypeScript Type Check
```bash
cd /Users/briankim/Desktop/ai/agi-dev/projects/punch-analytics/frontend
./node_modules/.bin/tsc --noEmit
```

**Result:** PASS (no output = no errors)

### Unit Tests - Subject API Client
```bash
cd /Users/briankim/Desktop/ai/agi-dev/projects/punch-analytics/frontend
./node_modules/.bin/jest src/lib/subject/__tests__/api.test.ts
```

**Result:** PASS

```
PASS src/lib/subject/__tests__/api.test.ts
  Subject Selection API
    getThumbnails
      ✓ should fetch thumbnails successfully (2 ms)
      ✓ should return processing status when thumbnails not ready
      ✓ should return auto_select info for single person (1 ms)
      ✓ should throw SubjectError on 404 (1 ms)
      ✓ should throw SubjectError on 401
    selectSubject
      ✓ should select subject successfully
      ✓ should throw SubjectError on 404 (1 ms)
      ✓ should throw SubjectError on 409 conflict

Test Suites: 1 passed, 1 total
Tests:       8 passed, 8 total
Snapshots:   0 total
Time:        0.513 s
```

## Test Coverage by BDD Scenario

| Scenario | Test Coverage |
|----------|---------------|
| Thumbnail grid displays extracted frames | API: getThumbnails success test |
| User selects subject from thumbnail | API: selectSubject success test |
| User changes selection before confirmation | Component: selection state management (no test yet) |
| User confirms subject selection | API: selectSubject success test |
| Single person auto-selected | API: auto_select info test |
| No subjects detected in video | API: status handling (implicit) |
| Thumbnail extraction loading state | API: processing status test |

## Notes

- Unit tests cover the API client layer
- Component tests (React Testing Library) not yet implemented
- E2E tests (Playwright) to be added in `/agi-e2e` phase
- Runtime verification requires starting the full system (backend + frontend)
