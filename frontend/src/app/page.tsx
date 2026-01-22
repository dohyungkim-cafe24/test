'use client';

/**
 * Landing page
 * @file page.tsx
 */

import React from 'react';
import Box from '@mui/material/Box';
import Button from '@mui/material/Button';
import Container from '@mui/material/Container';
import Typography from '@mui/material/Typography';
import { useRouter } from 'next/navigation';
import { useAuth } from '@/lib/auth/hooks';

export default function LandingPage() {
  const router = useRouter();
  const { isAuthenticated, isLoading } = useAuth();

  // Redirect to dashboard if already authenticated
  React.useEffect(() => {
    if (!isLoading && isAuthenticated) {
      router.push('/dashboard');
    }
  }, [isAuthenticated, isLoading, router]);

  return (
    <Box
      sx={{
        minHeight: '100vh',
        display: 'flex',
        flexDirection: 'column',
        alignItems: 'center',
        justifyContent: 'center',
        background: 'linear-gradient(180deg, #1565C0 0%, #0D47A1 100%)',
        color: 'white',
        textAlign: 'center',
        px: 2,
      }}
    >
      <Container maxWidth="md">
        <Typography
          variant="h2"
          component="h1"
          gutterBottom
          sx={{ fontWeight: 700 }}
        >
          PunchAnalytics
        </Typography>

        <Typography
          variant="h5"
          sx={{ mb: 4, opacity: 0.9 }}
        >
          AI-powered boxing analysis for smarter training
          <br />
          <span style={{ fontSize: '0.9em', opacity: 0.8 }}>
            AI 기반 복싱 분석으로 더 스마트한 트레이닝
          </span>
        </Typography>

        <Typography
          variant="body1"
          sx={{ mb: 6, maxWidth: 600, mx: 'auto', opacity: 0.85 }}
        >
          Upload your training videos and receive personalized feedback on your
          technique, with AI-generated insights on strengths, weaknesses, and
          recommendations.
          <br />
          <br />
          <span style={{ opacity: 0.8 }}>
            트레이닝 영상을 업로드하고 AI가 분석한 개인화된 피드백을 받아보세요.
          </span>
        </Typography>

        <Button
          variant="contained"
          size="large"
          onClick={() => router.push('/login')}
          sx={{
            backgroundColor: 'white',
            color: '#1565C0',
            '&:hover': {
              backgroundColor: '#f5f5f5',
            },
            px: 6,
            py: 1.5,
            fontSize: '1.1rem',
          }}
        >
          Get Started
          <span style={{ marginLeft: 8, opacity: 0.7 }}>시작하기</span>
        </Button>
      </Container>

      <Box
        sx={{
          position: 'absolute',
          bottom: 24,
          opacity: 0.7,
        }}
      >
        <Typography variant="caption">
          © 2026 PunchAnalytics. Training analysis for improvement, not diagnosis.
        </Typography>
      </Box>
    </Box>
  );
}
