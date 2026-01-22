# PunchAnalytics Design System

## Inputs
- docs/product/PRD.md
- docs/product/REQUIREMENTS_BASELINE.md
- docs/product/MARKET_BENCHMARK.md
- docs/product/STORY_MAP.md

---

## Material

PunchAnalytics adopts **Material Design 3 (M3)** as the baseline design system. All components, tokens, and patterns follow M3 specifications unless explicitly documented otherwise.

### Design Principles
1. **Form follows function**: Every element serves the analysis workflow
2. **Progressive disclosure**: Complex data revealed through clear hierarchy
3. **Mobile-first**: Touch-optimized interactions with responsive scaling
4. **Performance-oriented**: Lightweight visuals that load quickly

### M3 Adoption
- Use M3 color system with dynamic color support
- Use M3 typography scale with Roboto (Latin) and Noto Sans KR (Korean)
- Use M3 elevation and state layer system
- Use M3 shape scale (small/medium/large radius tokens)

---

## Design tokens

All tokens are defined in the companion `design_tokens.json` file. This section explains the semantic mapping.

### Token Categories
| Category | Purpose | JSON Path |
|----------|---------|-----------|
| Colors | Brand and functional colors | `colors.*` |
| Typography | Font families, sizes, weights | `typography.*` |
| Spacing | Layout and component spacing | `spacing.*` |
| Radius | Border radius values | `radius.*` |
| Elevation | Shadow definitions | `elevation.*` |
| Motion | Animation timing | `motion.*` |

### Referencing Tokens
- Engineers should import `design_tokens.json` directly
- CSS custom properties follow pattern: `--pa-{category}-{name}`
- Example: `--pa-color-primary` maps to `colors.primary`

---

## Theme

### Light Theme (Default)
PunchAnalytics uses a light theme by default, optimized for readability of analysis data.

| Role | Token | Hex Value |
|------|-------|-----------|
| Primary | `colors.primary` | #1565C0 |
| On Primary | `colors.onPrimary` | #FFFFFF |
| Primary Container | `colors.primaryContainer` | #D1E4FF |
| Secondary | `colors.secondary` | #625B71 |
| Surface | `colors.surface` | #FEFBFF |
| On Surface | `colors.onSurface` | #1C1B1F |
| Error | `colors.error` | #B3261E |
| Success | `colors.success` | #2E7D32 |

### Dark Theme (System Preference)
Dark theme is supported via media query detection. Tokens automatically switch when `prefers-color-scheme: dark`.

| Role | Token | Hex Value |
|------|-------|-----------|
| Primary | `colors.primaryDark` | #A8C7FA |
| On Primary | `colors.onPrimaryDark` | #062E6F |
| Surface | `colors.surfaceDark` | #1C1B1F |
| On Surface | `colors.onSurfaceDark` | #E6E1E5 |

### Theme Application
```css
:root {
  --pa-color-primary: #1565C0;
  --pa-color-surface: #FEFBFF;
}

@media (prefers-color-scheme: dark) {
  :root {
    --pa-color-primary: #A8C7FA;
    --pa-color-surface: #1C1B1F;
  }
}
```

---

## Color roles

### Primary Palette
| Role | Usage | Light | Dark |
|------|-------|-------|------|
| Primary | CTAs, key actions, active states | #1565C0 | #A8C7FA |
| On Primary | Text/icons on primary | #FFFFFF | #062E6F |
| Primary Container | Selected states, chips | #D1E4FF | #1A4175 |

### Secondary Palette
| Role | Usage | Light | Dark |
|------|-------|-------|------|
| Secondary | Less prominent actions | #625B71 | #CCC2DC |
| Secondary Container | Supporting UI elements | #E8DEF8 | #4A4458 |

### Surface Palette
| Role | Usage | Light | Dark |
|------|-------|-------|------|
| Surface | Page backgrounds | #FEFBFF | #1C1B1F |
| Surface Variant | Card backgrounds | #E7E0EC | #49454F |
| On Surface | Primary text | #1C1B1F | #E6E1E5 |
| On Surface Variant | Secondary text | #49454F | #CAC4D0 |

### Feedback Colors
| Role | Usage | Light | Dark |
|------|-------|-------|------|
| Error | Validation errors | #B3261E | #F2B8B5 |
| Error Container | Error backgrounds | #F9DEDC | #8C1D18 |
| Success | Completion states | #2E7D32 | #81C784 |
| Warning | Caution states | #ED6C02 | #FFB74D |
| Info | Informational | #0288D1 | #4FC3F7 |

### Boxing-Specific Colors
| Role | Usage | Hex |
|------|-------|-----|
| Strike | Punch visualization | #E53935 |
| Defense | Guard visualization | #1976D2 |
| Movement | Footwork visualization | #7B1FA2 |
| Strength | Positive metrics | #2E7D32 |
| Weakness | Improvement areas | #ED6C02 |

---

## Typography

### Font Stack
```css
--pa-font-primary: 'Roboto', 'Noto Sans KR', -apple-system, sans-serif;
--pa-font-mono: 'Roboto Mono', monospace;
```

### Type Scale (M3 Baseline)

| Style | Size | Weight | Line Height | Letter Spacing | Usage |
|-------|------|--------|-------------|----------------|-------|
| Display Large | 57px | 400 | 64px | -0.25px | Hero sections |
| Display Medium | 45px | 400 | 52px | 0 | Section headers |
| Display Small | 36px | 400 | 44px | 0 | Page titles |
| Headline Large | 32px | 400 | 40px | 0 | Card titles |
| Headline Medium | 28px | 400 | 36px | 0 | Section titles |
| Headline Small | 24px | 400 | 32px | 0 | Subsection titles |
| Title Large | 22px | 400 | 28px | 0 | List headers |
| Title Medium | 16px | 500 | 24px | 0.15px | Card headers |
| Title Small | 14px | 500 | 20px | 0.1px | Small headers |
| Body Large | 16px | 400 | 24px | 0.5px | Primary body text |
| Body Medium | 14px | 400 | 20px | 0.25px | Secondary body text |
| Body Small | 12px | 400 | 16px | 0.4px | Captions |
| Label Large | 14px | 500 | 20px | 0.1px | Button labels |
| Label Medium | 12px | 500 | 16px | 0.5px | Form labels |
| Label Small | 11px | 500 | 16px | 0.5px | Helper text |

### Korean Typography Notes
- Noto Sans KR for Korean text rendering
- Minimum font size: 14px for Korean body text (legibility)
- Line height increased by 4px for Korean text blocks

---

## Components

### Buttons

#### Primary Button (Filled)
| Property | Value |
|----------|-------|
| Background | `colors.primary` |
| Text | `colors.onPrimary` |
| Height | 40px |
| Padding | 24px horizontal |
| Border Radius | `radius.full` (20px) |
| Font | Label Large |
| States | Hover: +8% tint, Pressed: +12% tint, Disabled: 38% opacity |

#### Secondary Button (Outlined)
| Property | Value |
|----------|-------|
| Background | Transparent |
| Border | 1px `colors.outline` |
| Text | `colors.primary` |
| Height | 40px |
| States | Hover: 8% primary overlay |

#### Text Button
| Property | Value |
|----------|-------|
| Background | Transparent |
| Text | `colors.primary` |
| Padding | 12px horizontal |
| States | Hover: 8% primary overlay |

### Cards

#### Elevated Card
| Property | Value |
|----------|-------|
| Background | `colors.surface` |
| Elevation | Level 1 (1dp shadow) |
| Border Radius | `radius.medium` (12px) |
| Padding | 16px |

#### Filled Card
| Property | Value |
|----------|-------|
| Background | `colors.surfaceVariant` |
| Elevation | None |
| Border Radius | `radius.medium` (12px) |
| Padding | 16px |

### Form Fields

#### Text Input
| Property | Value |
|----------|-------|
| Height | 56px |
| Background | `colors.surfaceVariant` |
| Border Radius | `radius.small` (4px) top only |
| Border Bottom | 1px `colors.outline` |
| Label | Label Small, positioned above |
| Focus | 2px bottom border `colors.primary` |
| Error | Border `colors.error`, helper text red |

#### Dropdown/Select
| Property | Value |
|----------|-------|
| Height | 56px |
| Background | `colors.surfaceVariant` |
| Icon | Trailing chevron |
| Menu | Elevated surface, max 5 visible items |

### Navigation

#### Top App Bar
| Property | Value |
|----------|-------|
| Height | 64px |
| Background | `colors.surface` |
| Elevation | Level 2 on scroll |
| Title | Title Large |

#### Bottom Navigation (Mobile)
| Property | Value |
|----------|-------|
| Height | 80px |
| Background | `colors.surface` |
| Items | 3-5 icons with labels |
| Active | `colors.primary` icon + label |
| Inactive | `colors.onSurfaceVariant` |

### Progress Indicators

#### Linear Progress (Upload)
| Property | Value |
|----------|-------|
| Height | 4px |
| Track | `colors.surfaceVariant` |
| Indicator | `colors.primary` |
| Border Radius | `radius.full` |

#### Circular Progress (Processing)
| Property | Value |
|----------|-------|
| Size | 48px (default), 24px (small) |
| Track | `colors.surfaceVariant` |
| Indicator | `colors.primary` |
| Stroke Width | 4px |

### Chips

#### Filter Chip
| Property | Value |
|----------|-------|
| Height | 32px |
| Background | Transparent (unselected), `colors.secondaryContainer` (selected) |
| Border | 1px `colors.outline` (unselected) |
| Border Radius | `radius.small` (8px) |

### Dialogs

#### Alert Dialog
| Property | Value |
|----------|-------|
| Background | `colors.surface` |
| Border Radius | `radius.extraLarge` (28px) |
| Title | Headline Small |
| Body | Body Medium |
| Actions | Text buttons, right-aligned |
| Scrim | 32% black overlay |

### Snackbar / Toast
| Property | Value |
|----------|-------|
| Background | `colors.inverseSurface` |
| Text | `colors.inverseOnSurface` |
| Border Radius | `radius.small` (4px) |
| Position | Bottom center, 16px margin |
| Duration | 4 seconds default |

### Report-Specific Components

#### Metric Card
| Property | Value |
|----------|-------|
| Background | `colors.surface` |
| Border Radius | `radius.medium` (12px) |
| Padding | 16px |
| Title | Title Medium |
| Value | Display Small |
| Indicator | 4px left border (strength/weakness color) |

#### Stamp Timeline Item
| Property | Value |
|----------|-------|
| Height | 64px |
| Thumbnail | 48x48px, `radius.small` |
| Label | Title Small |
| Timestamp | Body Small, `colors.onSurfaceVariant` |
| Icon | 24px action type indicator |

#### Analysis Section Card
| Property | Value |
|----------|-------|
| Background | `colors.surfaceVariant` |
| Border Radius | `radius.medium` (12px) |
| Header | Icon + Title Medium |
| Content | Body Medium list items |
| Divider | 1px `colors.outlineVariant` between items |
