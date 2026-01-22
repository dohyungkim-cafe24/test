/**
 * Root layout component
 * @file layout.tsx
 */

import type { Metadata } from 'next';
import { AppRouterCacheProvider } from '@mui/material-nextjs/v14-appRouter';
import { ThemeProvider } from '@mui/material/styles';
import CssBaseline from '@mui/material/CssBaseline';
import { AuthProvider } from '@/lib/auth/context';
import theme from './theme';

export const metadata: Metadata = {
  title: 'PunchAnalytics - AI Boxing Analysis',
  description:
    'Analyze your boxing technique with AI-powered feedback. Upload your training videos and get personalized coaching insights.',
  keywords: ['boxing', 'training', 'AI', 'analysis', 'coaching', 'sports'],
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body>
        <AppRouterCacheProvider>
          <ThemeProvider theme={theme}>
            <CssBaseline />
            <AuthProvider>{children}</AuthProvider>
          </ThemeProvider>
        </AppRouterCacheProvider>
      </body>
    </html>
  );
}
