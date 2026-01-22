/**
 * Shared Report layout with Open Graph metadata
 * @file layout.tsx
 * @feature F009 - Report Sharing
 *
 * Implements:
 * - AC-053: Shared report shows social preview cards
 *
 * BDD Scenario:
 * - Shared report displays social preview (Open Graph meta tags)
 */

import type { Metadata } from 'next';
import type { ReactNode } from 'react';

/**
 * Generate metadata for social preview
 * AC-053: Open Graph meta tags for social sharing
 */
export const metadata: Metadata = {
  title: 'PunchAnalytics - Shared Boxing Analysis Report',
  description: 'View this AI-powered boxing training analysis report. Get insights on technique, strengths, weaknesses, and personalized recommendations.',
  openGraph: {
    title: 'Boxing Analysis Report - PunchAnalytics',
    description: 'AI-powered boxing training analysis with technique feedback, performance metrics, and personalized coaching recommendations.',
    type: 'article',
    siteName: 'PunchAnalytics',
    locale: 'en_US',
    images: [
      {
        url: '/og-share-report.png',
        width: 1200,
        height: 630,
        alt: 'PunchAnalytics Boxing Analysis Report',
      },
    ],
  },
  twitter: {
    card: 'summary_large_image',
    title: 'Boxing Analysis Report - PunchAnalytics',
    description: 'AI-powered boxing training analysis with technique feedback and personalized recommendations.',
    images: ['/og-share-report.png'],
  },
  robots: {
    index: true,
    follow: true,
  },
};

export default function SharedReportLayout({
  children,
}: {
  children: ReactNode;
}) {
  return children;
}
