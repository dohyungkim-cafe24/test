# PunchAnalytics 무료 배포 계획

## 목표
PunchAnalytics를 **100% 무료**로 배포하기 위한 최적의 조합을 구성합니다.

---

## 현재 아키텍처 vs 무료 배포 아키텍처

| 구성요소 | 현재 (Docker) | 무료 배포 |
|----------|---------------|-----------|
| Frontend | Next.js :3000 | **Vercel** (무료) |
| Backend | FastAPI :8000 | **Render** (무료) |
| PostgreSQL | :5432 | **Neon** (무료) |
| Redis | :6379 | **Upstash** (무료) |

---

## 무료 서비스별 제한사항

### 1. Vercel (Frontend)
- ✅ Next.js 최적화 배포
- ✅ 월 100GB 대역폭
- ✅ 자동 HTTPS
- ✅ 커스텀 도메인 지원
- ⚠️ Serverless 함수 10초 제한

### 2. Render (Backend)
- ✅ Python/FastAPI 지원
- ✅ 자동 HTTPS
- ⚠️ 무료 tier: 15분 비활성시 sleep
- ⚠️ 월 750시간 (1개 서비스)
- ⚠️ 512MB RAM

### 3. Neon (PostgreSQL)
- ✅ 서버리스 PostgreSQL
- ✅ 0.5GB 스토리지
- ✅ 자동 스케일링
- ⚠️ 비활성시 5분 후 suspend

### 4. Upstash (Redis)
- ✅ 서버리스 Redis
- ✅ 일 10,000 명령어
- ✅ 256MB 스토리지
- ⚠️ 글로벌 리전 1개

---

## 배포 단계

### Phase 1: 데이터베이스 설정 (Neon)
1. [ ] Neon 계정 생성 (https://neon.tech)
2. [ ] PostgreSQL 인스턴스 생성
3. [ ] 데이터베이스 연결 URL 획득
4. [ ] 스키마 마이그레이션

### Phase 2: Redis 설정 (Upstash)
1. [ ] Upstash 계정 생성 (https://upstash.com)
2. [ ] Redis 인스턴스 생성
3. [ ] 연결 URL 획득

### Phase 3: Backend 배포 (Render)
1. [ ] GitHub 리포지토리에 프로젝트 푸시
2. [ ] Render 계정 생성 (https://render.com)
3. [ ] Web Service 생성 (Python)
4. [ ] 환경 변수 설정
5. [ ] 배포 확인

### Phase 4: Frontend 배포 (Vercel)
1. [ ] Vercel 계정 생성 (https://vercel.com)
2. [ ] GitHub 연결
3. [ ] 환경 변수 설정 (API URL)
4. [ ] 배포 확인

### Phase 5: OAuth 설정
1. [ ] Kakao Developers에서 Redirect URI 업데이트
2. [ ] Google Cloud Console에서 Redirect URI 업데이트

---

## 필요한 코드 수정

### 1. Backend 수정 사항

**파일: `backend/api/core/config.py`**
- Neon PostgreSQL SSL 연결 설정 추가
- 환경 변수 기반 설정 강화

### 2. Frontend 수정 사항

**파일: `frontend/next.config.js`**
- Vercel 배포 최적화 설정
- 환경 변수 설정

### 3. 새로 생성할 파일

**`render.yaml`** - Render 배포 설정
**`.env.example`** - 환경 변수 템플릿

---

## 환경 변수 목록

### Backend (Render)
```
DATABASE_URL=postgresql://...@neon.tech/punch_analytics?sslmode=require
REDIS_URL=redis://default:...@upstash.com:6379
SECRET_KEY=your-production-secret-key
KAKAO_CLIENT_ID=...
KAKAO_CLIENT_SECRET=...
GOOGLE_CLIENT_ID=...
GOOGLE_CLIENT_SECRET=...
OPENAI_API_KEY=...
ENVIRONMENT=production
```

### Frontend (Vercel)
```
NEXT_PUBLIC_API_URL=https://your-backend.onrender.com
```

---

## 제한사항 및 대안

### 영상 처리 제한
- Render 무료 512MB RAM → MediaPipe 실행 제한적
- **권장 대안**: 영상 크기 제한 (30초 이하, 720p 이하)

### Cold Start 문제
- Render 무료: 15분 비활성시 sleep → 첫 요청 30초 대기
- **대안**: UptimeRobot으로 5분마다 ping (무료)

---

## 예상 비용

| 서비스 | 비용 | 비고 |
|--------|------|------|
| Vercel | $0 | Hobby plan |
| Render | $0 | Free tier |
| Neon | $0 | Free tier |
| Upstash | $0 | Free tier |
| **총 합계** | **$0/월** | |

---

## 검증 방법

1. Frontend 접속: `https://your-app.vercel.app`
2. Backend health: `https://your-backend.onrender.com/health`
3. OAuth 로그인 테스트
4. 영상 업로드 테스트 (작은 파일)
