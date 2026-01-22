# PunchAnalytics Information Architecture Map

## Inputs
- docs/product/PRD.md
- docs/product/REQUIREMENTS_BASELINE.md
- docs/product/MARKET_BENCHMARK.md
- docs/product/STORY_MAP.md

---

## Sitemap

```
PunchAnalytics
│
├── Public Area
│   ├── Landing Page (/)
│   ├── Login (/login)
│   ├── OAuth Callbacks (/auth/callback/*)
│   ├── Shared Report View (/report/{hash})
│   ├── Not Found (/404)
│   └── Error (/error)
│
└── Authenticated Area (requires login)
    ├── Dashboard (/dashboard)
    │   ├── Report List
    │   └── Report Detail (/dashboard/report/{id})
    │
    └── Upload Flow (/upload)
        ├── File Upload (/upload)
        ├── Subject Selection (/upload/{id}/select)
        ├── Body Specification (/upload/{id}/specs)
        └── Processing Status (/upload/{id}/processing)
```

### Hierarchy Rationale

| Section | Purpose | Access Control |
|---------|---------|----------------|
| Public Area | Marketing, auth, shared content | No auth required |
| Authenticated Area | Core product functionality | Session required |
| Dashboard | Home base for authenticated users | Owner sees own reports |
| Upload Flow | Linear wizard for new analysis | Session + upload context |

---

## Routes

### Public Routes

| Route | Component | Purpose | SEO | Cache |
|-------|-----------|---------|-----|-------|
| `/` | LandingPage | Product introduction, conversion | Yes | Static, 1 hour |
| `/login` | LoginPage | Authentication options | No | No cache |
| `/auth/callback/kakao` | OAuthCallback | Process Kakao OAuth | No | No cache |
| `/auth/callback/google` | OAuthCallback | Process Google OAuth | No | No cache |
| `/report/{hash}` | SharedReportView | Public report viewing | Yes | Dynamic, 5 min |
| `/404` | NotFoundPage | 404 error handling | No | Static |
| `/error` | ErrorPage | Generic error display | No | No cache |

### Authenticated Routes

| Route | Component | Purpose | Guard |
|-------|-----------|---------|-------|
| `/dashboard` | DashboardPage | Report history, upload CTA | AuthGuard |
| `/dashboard/report/{id}` | ReportDetailPage | Full report with owner actions | AuthGuard + OwnerGuard |
| `/upload` | UploadPage | Video file selection | AuthGuard |
| `/upload/{id}/select` | SubjectSelectPage | Subject identification | AuthGuard + UploadGuard |
| `/upload/{id}/specs` | BodySpecPage | User attributes form | AuthGuard + UploadGuard |
| `/upload/{id}/processing` | ProcessingPage | Analysis status tracking | AuthGuard + UploadGuard |

### Route Parameters

| Parameter | Type | Validation | Example |
|-----------|------|------------|---------|
| `{hash}` | String | 8-character alphanumeric | `abc12def` |
| `{id}` | UUID | UUID v4 format | `550e8400-e29b-41d4-a716-446655440000` |

### Route Guards

| Guard | Behavior | Redirect |
|-------|----------|----------|
| AuthGuard | Check valid session | `/login?redirect={current}` |
| OwnerGuard | Check report ownership | `/dashboard` with error toast |
| UploadGuard | Check upload exists and belongs to user | `/upload` |

---

## Key flows

### Flow 1: New User Onboarding

```
/                       Landing Page
│                       ├── Hero section with value prop
│                       ├── "Get Started" CTA
│                       └── Features overview
│
└──[Get Started]──────► /login
                        ├── Kakao OAuth button
                        └── Google OAuth button
                        │
                        └──[Kakao]────► Kakao OAuth
                                        │
                                        └──[Approve]──► /auth/callback/kakao
                                                        │
                                                        └──[Success]──► /dashboard
                                                                        (empty state)
```

### Flow 2: First Upload Journey

```
/dashboard              Dashboard (empty)
│                       ├── "No reports yet" illustration
│                       └── "Upload Video" CTA
│
└──[Upload Video]─────► /upload
                        ├── Drop zone
                        ├── File guidelines
                        └── Browse button
                        │
                        └──[Select File]──► [Validation]
                                            │
                                            ├──[Pass]──► [Upload Progress]
                                            │            │
                                            │            └──[Complete]──► /upload/{id}/select
                                            │                             │
                                            │                             └──[Confirm]──► /upload/{id}/specs
                                            │                                             │
                                            │                                             └──[Submit]──► /upload/{id}/processing
                                            │                                                            │
                                            │                                                            └──[Complete]──► /dashboard/report/{id}
                                            │
                                            └──[Fail]──► [Error Message]
                                                         └──[Retry]──► /upload
```

### Flow 3: Report Sharing

```
/dashboard/report/{id}  Report Detail (Owner)
│                       ├── Report content
│                       ├── Share button (off state)
│                       └── Delete button
│
└──[Share]────────────► Share Dialog
                        ├── Toggle: Enable sharing
                        └── Copy link button (disabled)
                        │
                        └──[Enable]──► [Generate URL]
                                       │
                                       └──[Copy Link]──► Clipboard
                                                         │
                                                         └──► Toast: "Link copied"
```

### Flow 4: Shared Report Access

```
/report/{hash}          External Access
│
├──[Valid Hash]───────► Shared Report View
│                       ├── Read-only report content
│                       ├── AI disclaimer
│                       └── "Try PunchAnalytics" CTA
│
├──[Invalid Hash]─────► /404
│                       └── "Report not found"
│
└──[Disabled Share]───► /error
                        └── "Sharing disabled"
```

### Flow 5: Dashboard Navigation

```
/dashboard              Dashboard (with reports)
│                       ├── Report list (cards)
│                       ├── Upload FAB/button
│                       └── Profile menu
│
├──[Tap Report]───────► /dashboard/report/{id}
│
├──[Delete Report]────► Confirmation Dialog
│                       │
│                       ├──[Confirm]──► Delete + Toast + Refresh list
│                       └──[Cancel]──► Close dialog
│
├──[Upload]───────────► /upload
│
└──[Profile > Logout]─► Logout + Redirect to /
```

---

## Notes

### Navigation Patterns

#### Mobile Navigation
- **Bottom Navigation**: Not used (linear flow, not tab-based)
- **Top App Bar**: Logo (left), profile avatar (right)
- **Back Navigation**: System back button, explicit back arrows on wizard steps
- **FAB**: "Upload Video" floating action button on dashboard

#### Desktop Navigation
- **Top App Bar**: Full width, logo (left), primary CTA (center-right), profile (right)
- **No Sidebar**: Simple app structure doesn't require persistent navigation
- **Breadcrumbs**: Not needed (shallow hierarchy)

### State Persistence

| State | Storage | Expiration |
|-------|---------|------------|
| Auth session | HttpOnly cookie | 7 days |
| Upload progress | Server-side (upload ID) | 24 hours |
| Body specs (draft) | localStorage | Until submitted |
| Last body specs | Server (user profile) | Permanent |

### Deep Linking

| Scenario | Behavior |
|----------|----------|
| Unauthenticated user accesses `/dashboard` | Redirect to `/login?redirect=/dashboard` |
| Unauthenticated user accesses `/dashboard/report/{id}` | Redirect to `/login?redirect=/dashboard/report/{id}` |
| Authenticated user accesses `/login` | Redirect to `/dashboard` |
| User accesses invalid `/upload/{id}/*` | Redirect to `/upload` with error toast |

### Error Handling

| Error Type | Route Behavior |
|------------|----------------|
| 401 Unauthorized | Redirect to `/login` |
| 403 Forbidden | Redirect to `/dashboard` with error toast |
| 404 Not Found | Show `/404` page |
| 500 Server Error | Show `/error` page with retry option |
| Network Error | Show inline error with retry button |

### URL Structure Rationale

1. **`/dashboard` as authenticated home**: Clear separation from marketing landing
2. **`/dashboard/report/{id}` vs `/report/{id}`**: Distinguishes owner view from public share
3. **`/upload/{id}/*` wizard pattern**: Maintains context across multi-step flow
4. **Short share hashes**: 8 characters for clean sharing URLs (e.g., `punchanalytics.com/report/abc12def`)

### Accessibility Navigation

| Feature | Implementation |
|---------|----------------|
| Skip to main content | Hidden link, visible on focus |
| Landmark regions | `<main>`, `<nav>`, `<header>` |
| Focus management | Focus first interactive element on route change |
| Page titles | Dynamic `<title>` per route for screen readers |

### Analytics Navigation Events

| Event | Trigger | Data |
|-------|---------|------|
| `page_view` | Route change | `page_name`, `previous_page`, `route` |
| `navigation_click` | Navigation element clicked | `element_type`, `destination` |
| `back_navigation` | Back button/gesture | `from_page`, `to_page` |
| `deep_link_access` | Direct URL access | `route`, `referrer`, `is_authenticated` |
