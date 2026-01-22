'use client';

/**
 * Material UI theme configuration
 * Based on design_tokens.json - Material Design 3
 * @file theme.ts
 */

import { createTheme } from '@mui/material/styles';

/**
 * PunchAnalytics theme
 * Implements design tokens from docs/ux/design_tokens.json
 */
const theme = createTheme({
  palette: {
    mode: 'light',
    primary: {
      main: '#1565C0',
      light: '#D1E4FF',
      dark: '#062E6F',
      contrastText: '#FFFFFF',
    },
    secondary: {
      main: '#625B71',
      light: '#E8DEF8',
      dark: '#1D192B',
      contrastText: '#FFFFFF',
    },
    error: {
      main: '#B3261E',
      light: '#F9DEDC',
      dark: '#410E0B',
      contrastText: '#FFFFFF',
    },
    success: {
      main: '#2E7D32',
      light: '#C8E6C9',
      dark: '#1B5E20',
      contrastText: '#FFFFFF',
    },
    warning: {
      main: '#ED6C02',
      light: '#FFE0B2',
      dark: '#E65100',
      contrastText: '#FFFFFF',
    },
    info: {
      main: '#0288D1',
      light: '#B3E5FC',
      dark: '#01579B',
      contrastText: '#FFFFFF',
    },
    background: {
      default: '#FEFBFF',
      paper: '#FFFFFF',
    },
    text: {
      primary: '#1C1B1F',
      secondary: '#49454F',
    },
  },
  typography: {
    fontFamily:
      "'Roboto', 'Noto Sans KR', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif",
    h1: {
      fontSize: '57px',
      fontWeight: 400,
      lineHeight: '64px',
      letterSpacing: '-0.25px',
    },
    h2: {
      fontSize: '45px',
      fontWeight: 400,
      lineHeight: '52px',
    },
    h3: {
      fontSize: '36px',
      fontWeight: 400,
      lineHeight: '44px',
    },
    h4: {
      fontSize: '32px',
      fontWeight: 400,
      lineHeight: '40px',
    },
    h5: {
      fontSize: '28px',
      fontWeight: 400,
      lineHeight: '36px',
    },
    h6: {
      fontSize: '24px',
      fontWeight: 400,
      lineHeight: '32px',
    },
    subtitle1: {
      fontSize: '22px',
      fontWeight: 400,
      lineHeight: '28px',
    },
    subtitle2: {
      fontSize: '16px',
      fontWeight: 500,
      lineHeight: '24px',
      letterSpacing: '0.15px',
    },
    body1: {
      fontSize: '16px',
      fontWeight: 400,
      lineHeight: '24px',
      letterSpacing: '0.5px',
    },
    body2: {
      fontSize: '14px',
      fontWeight: 400,
      lineHeight: '20px',
      letterSpacing: '0.25px',
    },
    button: {
      fontSize: '14px',
      fontWeight: 500,
      lineHeight: '20px',
      letterSpacing: '0.1px',
      textTransform: 'none',
    },
    caption: {
      fontSize: '12px',
      fontWeight: 400,
      lineHeight: '16px',
      letterSpacing: '0.4px',
    },
    overline: {
      fontSize: '11px',
      fontWeight: 500,
      lineHeight: '16px',
      letterSpacing: '0.5px',
    },
  },
  shape: {
    borderRadius: 12, // medium radius
  },
  components: {
    MuiButton: {
      styleOverrides: {
        root: {
          borderRadius: '20px',
          minWidth: '64px',
        },
        sizeLarge: {
          height: '48px',
          padding: '0 32px',
        },
        sizeMedium: {
          height: '40px',
          padding: '0 24px',
        },
        sizeSmall: {
          height: '32px',
          padding: '0 16px',
        },
      },
    },
    MuiCard: {
      styleOverrides: {
        root: {
          borderRadius: '12px',
          padding: '16px',
        },
      },
    },
    MuiDialog: {
      styleOverrides: {
        paper: {
          borderRadius: '28px',
          padding: '24px',
          minWidth: '280px',
          maxWidth: '560px',
        },
      },
    },
    MuiAppBar: {
      styleOverrides: {
        root: {
          height: '64px',
        },
      },
    },
  },
});

export default theme;
