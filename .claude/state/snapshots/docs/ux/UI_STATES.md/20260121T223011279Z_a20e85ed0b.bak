# PunchAnalytics UI States

## Inputs
- docs/product/PRD.md
- docs/product/REQUIREMENTS_BASELINE.md
- docs/product/MARKET_BENCHMARK.md
- docs/product/STORY_MAP.md

---

## Loading

### Global Loading States

#### Page Load Skeleton
| Property | Specification |
|----------|---------------|
| Background | `colors.surfaceVariant` with 50% opacity pulse animation |
| Animation | Pulse: 0.5s ease-in-out infinite alternate (opacity 0.5 to 1.0) |
| Duration | Display until content ready, minimum 200ms to prevent flash |
| Shape | Match content block shapes (rectangles for text, squares for images) |

#### Inline Spinner
| Property | Specification |
|----------|---------------|
| Component | Circular progress indicator |
| Size | 24px (inline), 48px (centered) |
| Color | `colors.primary` |
| Usage | Button loading states, small async operations |

### Upload Loading States

#### US-002: Video Upload Progress
| State | Visual | Behavior |
|-------|--------|----------|
| Preparing | "Preparing upload..." with spinner | Show immediately on file selection |
| Uploading | Linear progress bar with percentage | Update every 500ms; show bytes transferred |
| Paused | Progress bar paused state, "Upload paused" text | Amber indicator; show resume button |
| Resuming | "Resuming upload..." with spinner | Transition to uploading state |
| Finalizing | "Finalizing..." with indeterminate progress | Show after 100% while server processes |

```
Upload Progress Card:
+------------------------------------------+
|  [video-icon] video_filename.mp4         |
|  [=========>--------------------] 45%    |
|  225 MB / 500 MB • 2 min remaining       |
|  [Cancel]                                |
+------------------------------------------+
```

#### US-003: Thumbnail Generation
| State | Visual | Behavior |
|-------|--------|----------|
| Extracting | "Extracting frames..." with spinner | Show during frame extraction |
| Processing | Grid with skeleton items, progressive reveal | Replace skeletons as thumbnails ready |

### Processing Loading States

#### US-005/US-006/US-007: Analysis Processing
| State | Visual | Behavior |
|-------|--------|----------|
| Queued | "Your video is queued for analysis" | Show position in queue if available |
| Pose Estimation | "Analyzing movements..." (step 1/3) | Circular progress, indeterminate |
| Stamp Generation | "Identifying key moments..." (step 2/3) | Circular progress, indeterminate |
| LLM Analysis | "Generating insights..." (step 3/3) | Circular progress, indeterminate |

```
Processing Status Card:
+------------------------------------------+
|  [video-thumbnail]                       |
|                                          |
|  [===] Analyzing movements...            |
|  Step 2 of 3                             |
|                                          |
|  Estimated time: 3 minutes               |
|  Started: 2 minutes ago                  |
+------------------------------------------+
```

### Report Loading States

#### US-008: Report View Loading
| Section | Loading State |
|---------|---------------|
| Header | Skeleton: 60% width title, 40% width subtitle |
| Summary Card | Skeleton: full width paragraph block |
| Metrics Grid | Skeleton: 4 square cards with pulse |
| Analysis Sections | Skeleton: header + 3 list item lines |
| Timestamps | Skeleton: horizontal scroll of thumbnail boxes |

### Dashboard Loading States

#### US-010: Report History Loading
| State | Visual |
|-------|--------|
| Initial Load | 3 skeleton list items |
| Loading More | Skeleton item at bottom + spinner |
| Refreshing | Pull-to-refresh spinner at top |

---

## Empty

### Dashboard Empty State (US-010)
| Element | Content |
|---------|---------|
| Illustration | Boxing gloves illustration (Material style, outlined) |
| Headline | "No analysis reports yet" |
| Korean | "아직 분석 리포트가 없습니다" |
| Body | "Upload your first sparring video to get AI-powered coaching feedback" |
| Korean Body | "첫 번째 스파링 영상을 업로드하고 AI 코칭 피드백을 받아보세요" |
| CTA Button | "Upload Video" / "영상 업로드" |

```
+------------------------------------------+
|          [boxing-gloves-icon]            |
|                                          |
|     No analysis reports yet              |
|                                          |
|  Upload your first sparring video to     |
|  get AI-powered coaching feedback        |
|                                          |
|         [Upload Video]                   |
+------------------------------------------+
```

### Subject Selection Empty State (US-003)
| Element | Content |
|---------|---------|
| Scenario | No people detected in video frames |
| Headline | "No subjects detected" |
| Korean | "분석 대상을 찾을 수 없습니다" |
| Body | "We couldn't identify any people in your video. Please upload a video with clear visibility of the subjects." |
| Korean Body | "영상에서 사람을 식별할 수 없습니다. 대상이 잘 보이는 영상을 다시 업로드해 주세요." |
| CTA Button | "Upload Different Video" / "다른 영상 업로드" |

### Search Results Empty State (Future: Report Search)
| Element | Content |
|---------|---------|
| Headline | "No reports found" |
| Korean | "검색 결과가 없습니다" |
| Body | "Try adjusting your search or filters" |
| Korean Body | "검색어나 필터를 조정해 보세요" |

---

## Error

### Network Errors

#### Connection Lost
| Element | Content |
|---------|---------|
| Icon | `cloud_off` (Material Symbol) |
| Headline | "Connection lost" |
| Korean | "연결이 끊어졌습니다" |
| Body | "Check your internet connection and try again" |
| Korean Body | "인터넷 연결을 확인하고 다시 시도해 주세요" |
| Primary Action | "Retry" / "다시 시도" |
| Secondary Action | "Go Offline" (if applicable) |

#### Server Error (5xx)
| Element | Content |
|---------|---------|
| Icon | `error_outline` (Material Symbol) |
| Headline | "Something went wrong" |
| Korean | "문제가 발생했습니다" |
| Body | "Our servers are having trouble. Please try again in a few minutes." |
| Korean Body | "서버에 문제가 발생했습니다. 잠시 후 다시 시도해 주세요." |
| Primary Action | "Retry" / "다시 시도" |
| Secondary Action | "Contact Support" / "문의하기" |

#### Timeout Error
| Element | Content |
|---------|---------|
| Icon | `schedule` (Material Symbol) |
| Headline | "Request timed out" |
| Korean | "요청 시간이 초과되었습니다" |
| Body | "The server is taking too long to respond. Please try again." |
| Korean Body | "서버 응답이 너무 오래 걸립니다. 다시 시도해 주세요." |
| Primary Action | "Retry" / "다시 시도" |

### Upload Errors (US-002)

#### File Too Large
| Element | Content |
|---------|---------|
| Inline Error | Icon + text below file picker |
| Message | "Video file too large. Please upload a file under 500MB." |
| Korean | "영상 파일이 너무 큽니다. 500MB 이하의 파일을 업로드해 주세요." |
| Guidance | "Current file: 650MB" |

#### Invalid Duration
| Element | Content |
|---------|---------|
| Message | "Video must be between 1 and 3 minutes." |
| Korean | "영상 길이는 1분에서 3분 사이여야 합니다." |
| Guidance | "Current duration: 5 minutes 30 seconds" |

#### Unsupported Format
| Element | Content |
|---------|---------|
| Message | "Unsupported format. Please upload MP4, MOV, or WebM." |
| Korean | "지원하지 않는 형식입니다. MP4, MOV 또는 WebM 파일을 업로드해 주세요." |
| Guidance | "Detected format: AVI" |

#### Upload Failed
| Element | Content |
|---------|---------|
| Message | "Upload failed. Please try again." |
| Korean | "업로드에 실패했습니다. 다시 시도해 주세요." |
| Primary Action | "Retry Upload" / "다시 업로드" |
| Secondary Action | "Choose Different File" / "다른 파일 선택" |

### Processing Errors (US-005/US-006/US-007)

#### Pose Estimation Failed
| Element | Content |
|---------|---------|
| Icon | `visibility_off` (Material Symbol) |
| Headline | "Unable to analyze video" |
| Korean | "영상을 분석할 수 없습니다" |
| Body | "Unable to track subject clearly. Please upload video with better lighting or camera angle." |
| Korean Body | "대상을 명확하게 추적할 수 없습니다. 조명이나 카메라 각도가 더 좋은 영상을 업로드해 주세요." |
| Guidance | "Tips: Ensure good lighting, keep camera steady, avoid obstructions" |
| Primary Action | "Upload New Video" / "새 영상 업로드" |

#### LLM Analysis Failed
| Element | Content |
|---------|---------|
| Icon | `psychology_off` (Material Symbol) |
| Headline | "Analysis incomplete" |
| Korean | "분석을 완료할 수 없습니다" |
| Body | "We couldn't generate the analysis. Please try again." |
| Korean Body | "분석을 생성할 수 없습니다. 다시 시도해 주세요." |
| Primary Action | "Retry Analysis" / "분석 다시 시도" |
| Note | Retry available up to 3 times |

### Authentication Errors (US-001)

#### OAuth Failed
| Element | Content |
|---------|---------|
| Icon | `login` (Material Symbol) |
| Headline | "Login failed" |
| Korean | "로그인에 실패했습니다" |
| Body | "We couldn't sign you in. Please try again or use a different login method." |
| Korean Body | "로그인할 수 없습니다. 다시 시도하거나 다른 로그인 방법을 사용해 주세요." |
| Actions | "Try Again" + alternative OAuth button |

#### Session Expired
| Element | Content |
|---------|---------|
| Dialog | Modal dialog over current screen |
| Headline | "Session expired" |
| Korean | "세션이 만료되었습니다" |
| Body | "Please log in again to continue." |
| Korean Body | "계속하려면 다시 로그인해 주세요." |
| Action | "Log In" / "로그인" |

### Report Errors (US-008/US-009)

#### Report Not Found
| Element | Content |
|---------|---------|
| HTTP Status | 404 |
| Headline | "Report not found" |
| Korean | "리포트를 찾을 수 없습니다" |
| Body | "This report may have been deleted or the link is invalid." |
| Korean Body | "이 리포트가 삭제되었거나 링크가 유효하지 않습니다." |
| Primary Action | "Go to Dashboard" / "대시보드로 이동" |

#### Share Link Disabled
| Element | Content |
|---------|---------|
| HTTP Status | 403 |
| Headline | "Sharing disabled" |
| Korean | "공유가 비활성화되었습니다" |
| Body | "The owner has disabled sharing for this report." |
| Korean Body | "소유자가 이 리포트의 공유를 비활성화했습니다." |

---

## Validation

### Form Field Validation (US-004)

#### Height Input
| State | Visual | Message |
|-------|--------|---------|
| Empty (required) | Red border, error icon | "Height is required" / "키를 입력해 주세요" |
| Below minimum | Red border, error icon | "Height must be at least 100cm" / "키는 100cm 이상이어야 합니다" |
| Above maximum | Red border, error icon | "Height must be under 250cm" / "키는 250cm 이하여야 합니다" |
| Invalid format | Red border, error icon | "Please enter a valid number" / "올바른 숫자를 입력해 주세요" |
| Valid | Green checkmark (optional) | Helper text or none |

#### Weight Input
| State | Visual | Message |
|-------|--------|---------|
| Empty (required) | Red border, error icon | "Weight is required" / "체중을 입력해 주세요" |
| Below minimum | Red border, error icon | "Weight must be at least 30kg" / "체중은 30kg 이상이어야 합니다" |
| Above maximum | Red border, error icon | "Weight must be under 200kg" / "체중은 200kg 이하여야 합니다" |
| Invalid format | Red border, error icon | "Please enter a valid number" / "올바른 숫자를 입력해 주세요" |
| Valid | Green checkmark (optional) | Helper text or none |

#### Experience Level Selection
| State | Visual | Message |
|-------|--------|---------|
| Not selected (required) | Red outline on selection group | "Please select your experience level" / "경력을 선택해 주세요" |
| Selected | Primary color highlight | None |

#### Stance Selection
| State | Visual | Message |
|-------|--------|---------|
| Not selected (required) | Red outline on selection group | "Please select your stance" / "스탠스를 선택해 주세요" |
| Selected | Primary color highlight | None |

### Validation Behavior
| Trigger | Behavior |
|---------|----------|
| On blur | Validate field when user leaves it |
| On change | Clear error when user starts correcting |
| On submit | Validate all fields; focus first error |
| Real-time | Show character count for limited fields |

### Form Validation Visual Pattern
```
+------------------------------------------+
| Height (cm)                              |
| +--------------------------------------+ |
| | 280                                  | |
| +--------------------------------------+ |
| [error-icon] Height must be under 250cm  |
+------------------------------------------+
```

### Submit Button States
| Form State | Button State |
|------------|--------------|
| Empty required fields | Disabled, 38% opacity |
| Validation errors | Disabled, 38% opacity |
| All fields valid | Enabled, full opacity |
| Submitting | Loading spinner, disabled |

---

## Success

### Upload Success (US-002)
| Element | Content |
|---------|---------|
| Indicator | Green checkmark animation |
| Message | "Video uploaded successfully" |
| Korean | "영상이 업로드되었습니다" |
| Duration | Display for 2 seconds, then auto-navigate |
| Navigation | Automatically proceed to subject selection |

### Subject Selection Success (US-003)
| Element | Content |
|---------|---------|
| Indicator | Selected thumbnail with checkmark overlay |
| Visual | Blue selection ring around chosen subject |
| Confirmation | Enlarged preview of selected subject |
| Action | "Confirm Selection" button enabled |

### Body Spec Submission Success (US-004)
| Element | Content |
|---------|---------|
| Indicator | Form fields lock with subtle animation |
| Message | "Starting analysis..." |
| Korean | "분석을 시작합니다..." |
| Navigation | Proceed to processing status screen |

### Processing Complete Success (US-005/US-006/US-007)
| Element | Content |
|---------|---------|
| Indicator | Green checkmark with confetti animation (subtle) |
| Headline | "Analysis complete!" |
| Korean | "분석이 완료되었습니다!" |
| Body | "Your coaching report is ready to view" |
| Korean Body | "코칭 리포트가 준비되었습니다" |
| Primary Action | "View Report" / "리포트 보기" |
| Duration | Display until user action |

```
+------------------------------------------+
|            [checkmark-icon]              |
|                                          |
|        Analysis complete!                |
|                                          |
|  Your coaching report is ready to view   |
|                                          |
|         [View Report]                    |
+------------------------------------------+
```

### Share Link Created Success (US-009)
| Element | Content |
|---------|---------|
| Component | Snackbar / Toast |
| Icon | `link` (Material Symbol) |
| Message | "Link copied to clipboard" |
| Korean | "링크가 클립보드에 복사되었습니다" |
| Duration | 4 seconds |
| Position | Bottom center |

### Report Deleted Success (US-010)
| Element | Content |
|---------|---------|
| Component | Snackbar / Toast |
| Icon | `delete` (Material Symbol) |
| Message | "Report deleted" |
| Korean | "리포트가 삭제되었습니다" |
| Action | "Undo" / "실행 취소" (available for 10 seconds) |
| Duration | 6 seconds |

### Login Success (US-001)
| Element | Content |
|---------|---------|
| Behavior | Silent redirect to dashboard or previous page |
| Fallback Message | "Welcome back!" (if redirect delayed) |
| Korean | "환영합니다!" |

### Logout Success (US-001)
| Element | Content |
|---------|---------|
| Component | Snackbar / Toast |
| Message | "You've been logged out" |
| Korean | "로그아웃되었습니다" |
| Navigation | Redirect to landing page |

### Success Animation Specifications
| Animation | Duration | Easing |
|-----------|----------|--------|
| Checkmark draw | 300ms | emphasized decelerate |
| Confetti burst | 500ms | standard |
| Card highlight | 200ms | standard |
| Toast entrance | 200ms | emphasized decelerate |
| Toast exit | 150ms | standard accelerate |
