---
name: Aetheric Pastel Enterprise
colors:
  surface: '#f9f9ff'
  surface-dim: '#cfdaf1'
  surface-bright: '#f9f9ff'
  surface-container-lowest: '#ffffff'
  surface-container-low: '#f0f3ff'
  surface-container: '#e7eeff'
  surface-container-high: '#dee9ff'
  surface-container-highest: '#d8e3f9'
  on-surface: '#111c2c'
  on-surface-variant: '#3f4949'
  inverse-surface: '#263142'
  inverse-on-surface: '#ebf1ff'
  outline: '#6f797a'
  outline-variant: '#bec8c9'
  surface-tint: '#12686e'
  primary: '#12686e'
  on-primary: '#ffffff'
  primary-container: '#83ccd2'
  on-primary-container: '#00575c'
  inverse-primary: '#89d3d9'
  secondary: '#5e5a7e'
  on-secondary: '#ffffff'
  secondary-container: '#dbd5ff'
  on-secondary-container: '#5e5b7f'
  tertiary: '#994157'
  on-tertiary: '#ffffff'
  tertiary-container: '#ffa8b9'
  on-tertiary-container: '#853147'
  error: '#ba1a1a'
  on-error: '#ffffff'
  error-container: '#ffdad6'
  on-error-container: '#93000a'
  primary-fixed: '#a5eff5'
  primary-fixed-dim: '#89d3d9'
  on-primary-fixed: '#002022'
  on-primary-fixed-variant: '#004f54'
  secondary-fixed: '#e4dfff'
  secondary-fixed-dim: '#c7c2eb'
  on-secondary-fixed: '#1a1737'
  on-secondary-fixed-variant: '#464365'
  tertiary-fixed: '#ffd9df'
  tertiary-fixed-dim: '#ffb1c0'
  on-tertiary-fixed: '#3f0016'
  on-tertiary-fixed-variant: '#7c2940'
  background: '#f9f9ff'
  on-background: '#111c2c'
  surface-variant: '#d8e3f9'
typography:
  display-lg:
    fontFamily: Hanken Grotesk
    fontSize: 40px
    fontWeight: '700'
    lineHeight: 48px
    letterSpacing: -0.02em
  display-lg-mobile:
    fontFamily: Hanken Grotesk
    fontSize: 30px
    fontWeight: '700'
    lineHeight: 38px
    letterSpacing: -0.015em
  headline-lg:
    fontFamily: Hanken Grotesk
    fontSize: 28px
    fontWeight: '600'
    lineHeight: 36px
    letterSpacing: -0.01em
  headline-md:
    fontFamily: Hanken Grotesk
    fontSize: 22px
    fontWeight: '600'
    lineHeight: 28px
    letterSpacing: -0.005em
  headline-sm:
    fontFamily: Hanken Grotesk
    fontSize: 18px
    fontWeight: '600'
    lineHeight: 24px
  title-md:
    fontFamily: Hanken Grotesk
    fontSize: 16px
    fontWeight: '600'
    lineHeight: 22px
  body-lg:
    fontFamily: Hanken Grotesk
    fontSize: 15px
    fontWeight: '400'
    lineHeight: 22px
  body-md:
    fontFamily: Hanken Grotesk
    fontSize: 13px
    fontWeight: '400'
    lineHeight: 18px
  body-sm:
    fontFamily: Hanken Grotesk
    fontSize: 12px
    fontWeight: '400'
    lineHeight: 16px
  label-md:
    fontFamily: Hanken Grotesk
    fontSize: 12px
    fontWeight: '600'
    lineHeight: 16px
    letterSpacing: 0.02em
  label-sm:
    fontFamily: Hanken Grotesk
    fontSize: 11px
    fontWeight: '600'
    lineHeight: 14px
    letterSpacing: 0.04em
  code-num:
    fontFamily: Hanken Grotesk
    fontSize: 13px
    fontWeight: '500'
    lineHeight: 16px
    letterSpacing: -0.01em
rounded:
  sm: 0.125rem
  DEFAULT: 0.25rem
  md: 0.375rem
  lg: 0.5rem
  xl: 0.75rem
  full: 9999px
spacing:
  gutter: 1rem
  gutter-compact: 0.75rem
  margin: 1.5rem
  margin-mobile: 1rem
  space-xs: 0.25rem
  space-sm: 0.5rem
  space-md: 0.75rem
  space-lg: 1.25rem
  space-xl: 2rem
---

## Brand & Style

This design system translates a luminous, gentle pastel palette into an executive-grade, high-density digital workspace. By pairing soft ethereal tones with strict typographic discipline and crisp architectural lines, the aesthetic avoids frivolous whimsy, landing instead on serene focus, modern elegance, and cognitive clarity. 

The aesthetic marries **Corporate / Modern** precision with soft **Minimalism** and subtle tonal depth. The primary persona comprises analysts, operations leads, and knowledge workers who operate within complex data structures for prolonged hours. The system evokes a sense of tranquil competence, replacing the visual fatigue of harsh dark modes and cold monochromatic grays with soothing hues of cyan, wisteria, and mint, accented by an assertive rose-coral for decisive actions.

## Colors

The color palette directly extracts and synthesizes the luminous swatches provided:
- **Primary (`#83CCD2`)**: Anchors primary focus, active navigation states, interactive toggles, and key metric progress bars. Supported by atmospheric surface tints (`#A9E8E8`, `#B1E8ED`, `#C0F3EA`) for table row highlights, active chips, and sub-surface fills.
- **Secondary (`#BEB9E2`)**: Provides structural secondary categorization, grouping metadata, badges, and secondary analytical dimensions. Supported by softer tint variants (`#D2CCF2`, `#DFCFF3`).
- **Tertiary (`#F68BA2`)**: Used intentionally and sparingly as an energetic accent for high-priority calls-to-action, active alert flags, real-time indicators, and critical conversion triggers.
- **Success & Status Complement (`#B2EAD3`)**: Serves as a soothing positive state identifier, operational health flag, and growth vector within data grids.
- **Neutrals & Surfaces**: Clean white (`#FFFFFF`) surfaces sit upon an ultra-soft cool off-white canvas (`#F7FAFA`). Typography and high-contrast structural dividers rely on deep slate tones (`#1E2638` for primary text, `#5A6578` for secondary labels, `#E3E8EC` for crisp 1px structural borders). Text rendered atop light pastel fills must use high-contrast dark neutrals to ensure strict accessibility compliance.

## Typography

The typographic hierarchy is powered by **Hanken Grotesk**, chosen for its sharp modern geometric structure, crisp legibility at small sizes, and functional neutral cadence. 

Key implementation rules:
- **Tabular Figures**: All numerical metrics, status counters, and financial tables must enforce `font-feature-settings: "tnum"` to maintain vertical tabular alignment across dense rows.
- **Case and Tracking**: Section headers and overline labels use uppercase styling paired with expanded tracking (`0.04em`) to establish visual separation against dense body content.
- **Hierarchy Contrast**: Because the color palette is light and delicate, typography assumes structural authority via deep charcoal tones (`#1E2638`) and precise font weight differentials (`600` for hierarchy versus `400` for reading density).

## Layout & Spacing

This design system uses a 12-column fluid grid system engineered for analytical density and multi-pane productivity:
- **Desktop (>= 1280px)**: 12 columns with `1rem` (16px) gutters and `1.5rem` (24px) outer margins. Side panels dock rigidly to 260px or 320px fixed bounds, with remaining content area calculating fluidly.
- **Compact / Tablet (768px - 1279px)**: 8 columns with `0.75rem` (12px) gutters, outer margin of `1.25rem`. Complex data grids utilize horizontal scrolling containers with sticky header rows.
- **Mobile (< 768px)**: 4 columns with `0.5rem` gutters and `1rem` outer canvas padding. Grids reflow linearly into vertical card decks.

Rhythm is based on a strict 4px base increment, prioritizing compact vertical density (`space-sm` for table cells and filter bars) to maximize situational awareness on enterprise viewports.

## Elevation & Depth

Visual hierarchy is achieved through **low-contrast outlines** and delicate **tonal surface layering**, eschewing heavy blurred dropshadows that muddy soft pastel hues.

- **Base Level (Canvas)**: Background canvas sits at `#F7FAFA`.
- **Level 1 (Panels & Data Grids)**: Surfaces rest at solid `#FFFFFF`, demarcated by a crisp 1px border of `#E3E8EC`. No drop shadow.
- **Level 2 (Hovered Cards & Action Sheets)**: Slight elevation via a soft tinted ambient shadow: `0 4px 16px -2px rgba(131, 204, 210, 0.18)` and a border transition to `#B1E8ED`.
- **Level 3 (Modals, Overlays, & Dropdowns)**: Crisp 1px border in `#D2CCF2` paired with a directional float shadow: `0 12px 32px -4px rgba(30, 38, 56, 0.08)`.
- **Tinted Backdrops**: Modal overlays use `#1E2638` at 20% opacity with a `4px` subtle blur to preserve workspace clarity behind the active task.

## Shapes

The design system adopts **Soft** roundedness (`level 1` / `0.25rem` base border-radius) to uphold disciplined enterprise utility. 

- **Micro Elements (Inputs, Buttons, Badges)**: Bound to `4px` (`0.25rem`) radius, delivering crisp geometry that stacks cleanly in multi-field tables and dense toolbars.
- **Structural Containers (Cards, Modals, Flyouts)**: Bound to `rounded-lg` (`8px` / `0.5rem`), softening the periphery without wasting canvas area.
- **Full Pills (`9999px`)**: Reserved exclusively for inline category tags and numerical counters to quickly differentiate them from interactive button controls.

## Components

### Buttons
- **Primary**: Background `#83CCD2`, high-contrast text `#0E3B3E`, 1px solid `#6FBFC6`. Hover shifts to `#A9E8E8`. Active shifts to `#6FBFC6`.
- **Accent (Call-to-Action)**: Background `#F68BA2`, text `#FFFFFF`, bold weight. Hover shifts to `#ED738E`.
- **Secondary / Outlined**: Pure white surface, 1px border `#BEB9E2`, text `#2A2744`. Hover introduces tint fill `#DFCFF3` at 20% opacity.
- **Destructive**: Soft light-rose fill with deep red-tint text (`#851D32`) and 1px border `#F68BA2`.

### Chips & Badges
- **Status Mint**: Background `#B2EAD3`, text `#154B35`, pill-shaped, uppercase `label-sm`.
- **Status Cyan**: Background `#C0F3EA`, text `#0F4741`.
- **Category Periwinkle**: Background `#DFCFF3`, text `#3D356A`.
- **Metric Pill**: Pure white core, 1px `#E3E8EC` border, housing tabular figures with a colored pastel dot indicator.

### Input Fields & Controls
- **Inputs**: Background `#FFFFFF`, 1px solid `#D8DEE4`, height 36px (compact enterprise standard), text `#1E2638`. Focus state applies a 1px ring in `#83CCD2` and border color `#83CCD2`.
- **Checkboxes & Radios**: 16px square/circle with 1px border `#BEB9E2`. Checked state fills `#83CCD2` displaying a white checkmark or inner dot.

### Tables & Data Grids
- **Header**: Height 36px, background `#F7FAFA`, bottom border 1px solid `#E3E8EC`, text `label-sm` in `#5A6578`.
- **Rows**: Alternating subtle striping option with `#FAFDFD`, row hover highlight `#C0F3EA` at 30% opacity, bottom border 1px `#F0F3F5`.
- **Cell Padding**: 8px vertical, 12px horizontal.

### Cards & Metrics
- Pure white background, 1px solid `#E3E8EC`, 16px interior padding.
- Metric cards incorporate a 3px top accent border using selected swatches (`#83CCD2`, `#BEB9E2`, or `#F68BA2`) to indicate cluster types.