# Design system

> Build every screen to the mockups in [`mockups/light`](mockups/light) and [`mockups/dark`](mockups/dark), using the tokens below. Don't introduce new colors, fonts, radii or shadows. The editable source is the Claude Design canvas "Galeway — UI Mockups"; the PNGs here are exported from it and are the reference for implementation.

## 1. Principles

1. **Calm over loud.** A driver checking weather is already stressed. Neutral surfaces, one accent, color reserved for risk.
2. **Risk is the only loud color.** Green → yellow → orange → red → magenta, and always paired with a text label.
3. **Explain, don't just show.** Every level has a reason; every recommendation has a "why."
4. **The map is the hero; the panel is the truth.** Everything on the map is also available as text.
5. **Nothing jumps.** Skeletons match final layout; motion is short and purposeful.

## 2. Brand

| Asset | File |
|---|---|
| Logo (light backgrounds) | [brand/galeway-logo-light.svg](brand/galeway-logo-light.svg) · [png](brand/galeway-logo-light.png) |
| Logo (dark backgrounds) | [brand/galeway-logo-dark.svg](brand/galeway-logo-dark.svg) · [png](brand/galeway-logo-dark.png) |
| Mark (app icon) | [brand/galeway-mark.svg](brand/galeway-mark.svg) · [png](brand/galeway-mark.png) |
| Mark, one color (`currentColor`) | [brand/galeway-mark-mono.svg](brand/galeway-mark-mono.svg) |
| Favicon | [brand/favicon.svg](brand/favicon.svg) |
| App icons | [apple-touch-icon](brand/apple-touch-icon.png) · [192](brand/icon-192.png) · [512](brand/icon-512.png) · [maskable 512](brand/icon-maskable-512.png) |
| Social share image (1200×630) | [brand/og-image.png](brand/og-image.png) |

<p><img src="brand/galeway-logo-light.png" alt="Galeway logo" width="300"></p>

**The mark:** a gust of wind that turns into a road and ends at a destination dot. It reads at 16 px. Keep clear space of ¼ of the mark's width on all sides. Don't recolor it except to the mono version, and don't add effects.

**Wordmark:** "Galeway" in Space Grotesk Bold, letter-spacing −0.02em. In the product header the mark is 30 px and the wordmark 19 px.

## 3. Color tokens

Implemented as CSS variables in `frontend/src/styles/tokens.css` under `:root[data-theme="light"]` and `:root[data-theme="dark"]`, and exposed to Tailwind v4 through `@theme`.

| Token | Light | Dark | Use |
|---|---|---|---|
| `--bg` | `#F6F7F9` | `#0B0F17` | Page background |
| `--panel` | `#FFFFFF` | `#111723` | Surfaces (cards, panels, header) |
| `--sub` | `#F1F3F6` | `#0E131D` | Subtle fill (segmented controls, wells) |
| `--border` | `#E3E7ED` | `#222C3B` | Borders and dividers |
| `--text` | `#0F172A` | `#E5E7EB` | Primary text |
| `--muted` | `#5B6576` | `#9CA3AF` | Secondary text (≥ 4.5:1) |
| `--accent` | `#2563EB` | `#3B82F6` | Primary action, selected route, focus |
| `--accentSoft` | `#EAF1FF` | `#172554` | Selected card fill, info banner |
| `--accentText` | `#1D4ED8` | `#93C5FD` | Links, accent text |
| `--onAccent` | `#FFFFFF` | `#FFFFFF` | Text on accent |
| `--map` | `#E9EEF3` | `#0D1420` | Map land (fallback) |
| `--alt` | `#94A3B8` | `#4B5563` | Alternate routes |
| `--label` | `#1E293B` | `#E2E8F0` | Map labels |
| `--glass` | `rgba(255,255,255,.92)` | `rgba(17,23,35,.92)` | Floating map controls |
| `--skel` | `#E6EAF0` | `#1A2230` | Skeleton blocks |
| `--okFg` | `#047857` | `#6EE7B7` | Success text |
| `--errFg` | `#B91C1C` | `#FCA5A5` | Error text and borders |
| `--errBg` | `#FEF2F2` | `#2A1215` | Error surface |
| `--errBorder` | `#FECACA` | `#5B1D24` | Error surface border |

All text pairs meet WCAG AA (4.5:1) in both themes. Status and risk text always appear with an icon or a label, never as color alone.

### Risk palette

The bar/map colors are the same in both themes. Chips (labels) use tinted backgrounds that pass contrast.

| Level | Bar / map | Chip bg (light) | Chip text (light) | Chip bg (dark) | Chip text (dark) |
|---|---|---|---|---|---|
| Low | `#10B981` | `#D1FAE5` | `#065F46` | `#064E3B` | `#6EE7B7` |
| Moderate | `#EAB308` | `#FEF3C7` | `#92400E` | `#422006` | `#FDE68A` |
| High | `#F97316` | `#FFEDD5` | `#9A3412` | `#431407` | `#FDBA74` |
| Severe | `#DC2626` | `#FEE2E2` | `#991B1B` | `#450A0A` | `#FCA5A5` |
| No travel | `#A21CAF` | `#FAE8FF` | `#86198F` | `#3B0764` | `#F0ABFC` |

`NO_DATA` uses the `--border` color for bars and a dashed outline, labelled "No data."

## 4. Typography

Self-hosted through Fontsource. No external font requests.

| Role | Font | Size / line height | Weight |
|---|---|---|---|
| Page title (h1) | Space Grotesk | 28 / 34, −0.02em | 700 |
| Hero (empty state) | Space Grotesk | 26 / 31, −0.02em | 700 |
| Section title (h2) | Space Grotesk | 16 / 22 | 600 |
| Body | Inter | 14 / 21 | 400 |
| Small / labels | Inter | 12 / 16 | 500 |
| Numbers (stats, ETAs, weights, units) | JetBrains Mono, `tabular-nums` | 12–24 | 400–500 |

Numbers use the mono face so columns line up and values don't jitter while the slider moves.

## 5. Spacing, radius, elevation

- **Spacing**: 4 px base. Used values: 4, 6, 8, 10, 12, 14, 16, 18, 20, 24, 28, 32.
- **Radius**: 6 (chips), 7–8 (small buttons), 10 (inputs, buttons), 12 (cards), 14 (map bars), 16 (dialogs, floating panels), 999 (pills).
- **Elevation**: light `0 1px 2px rgba(15,23,42,.06), 0 8px 24px rgba(15,23,42,.08)`; dark `0 8px 24px rgba(0,0,0,.45)`. Only floating things (popovers, map controls, dialogs, toasts) are elevated.
- **Layout**: header 60 px; side panel 380–420 px; map fills the rest. Below 768 px: map full screen with a bottom sheet (see mobile mockup).

## 6. Components

Built on shadcn/ui (Radix) and restyled with the tokens.

| Component | Notes |
|---|---|
| Button | Primary (accent fill), Secondary (panel + border), Ghost. Height 44 (forms) / 36 (toolbars). Loading state keeps its width. |
| Input / Combobox | 44 px, radius 10, label above, error text below in `--errFg`, `aria-invalid`. Combobox follows the ARIA pattern. |
| Segmented control | `--sub` track, selected item `--panel` + small shadow. Used for interval, layer, table filter. |
| Route card | Selected: `--accentSoft` fill + accent border. Shows name, recommended badge or delta, 3 mono stats, risk bar, worst stretch. |
| Risk chip | 22 px tall, radius 6, tinted bg + strong text. |
| Risk bar | 6 px (cards) / 14 px (detail), 2 px gaps between segments, proportional to miles. |
| Stat tile | Label (12) / value (mono 24) / sub (12). |
| Toast | 360 px, icon + title + body + optional action. See [FRONTEND §8](../04-frontend/FRONTEND.md#8-toasts-sonner). |
| Banner | Full-width inside a panel: info (accentSoft), warning (moderate chip colors), error (errBg), no-travel (ntBg). |
| Dialog / Drawer | 16 radius; drawer is 440 px from the right; focus trap; Esc closes; scrim `rgba(15,23,42,.35–.45)`. |
| Skeleton | `--skel` blocks; a slow shimmer (1.6 s) that is off with reduced motion. |
| Table | Mono numbers; sticky header on scroll; the row for the worst checkpoint gets its level's chip bg; horizontal scroll inside the card on small screens. |

## 7. Map styling

| Element | Style |
|---|---|
| Base map | OpenFreeMap light style; dark = recolored to tokens |
| Selected route | 6 px accent line on an 11 px `--panel` casing |
| Other routes | 5 px `--alt`, dotted (`[1, 10]`), round caps; on hover 6 px |
| Checkpoints | Radius 7 (9 when hovered or selected), risk color fill, 2.5 px `--panel` stroke |
| Origin / destination | 9 px `--text` dot with 3 px `--panel` ring + bold label |
| Truck marker | 28 px accent circle with a truck glyph, shadow; moves with the slider |
| Heatmap | Native heatmap layer; ramp transparent → `#10B981` → `#EAB308` → `#F97316` → `#DC2626` → `#A21CAF`; opacity 0.55 (light), 0.65 (dark); radius scales with zoom |
| Floating controls | `--glass` background, 1 px border, radius 12–14, elevation |

## 8. Motion

| What | Duration | Easing |
|---|---|---|
| Hover, press | 120 ms | ease-out |
| Panels, drawers, popovers | 200 ms | `cubic-bezier(.2,.8,.2,1)` |
| Route select (line width/color) | 200 ms | ease-out (MapLibre transitions) |
| Results appear | 200 ms fade + 4 px rise, 30 ms stagger per card | |
| Camera fit to routes | 600 ms | MapLibre default |

`prefers-reduced-motion: reduce` turns off shimmer, stagger and camera animation, and slows the play speed.

## 9. Screen inventory

Each screen exists in both themes. Light is the default.

| # | Screen | Light | Dark |
|---|---|---|---|
| 01 | First visit: form, examples, saved trips, explainer | ![First visit, light](mockups/light/01-first-visit.png) | ![First visit, dark](mockups/dark/01-first-visit.png) |
| 02 | Planning: real stages, skeletons, cancel | ![Planning loading, light](mockups/light/02-planning-loading.png) | ![Planning loading, dark](mockups/dark/02-planning-loading.png) |
| 03 | Results: routes, map, checkpoint popup, layers, forecast slider | ![Results map, light](mockups/light/03-results-map.png) | ![Results map, dark](mockups/dark/03-results-map.png) |
| 04 | Route detail: stats, why, risk strip, paginated checkpoints | ![Route detail, light](mockups/light/04-route-detail.png) | ![Route detail, dark](mockups/dark/04-route-detail.png) |
| 05 | Saved trips drawer with undo toast | ![Saved trips, light](mockups/light/05-saved-trips.png) | ![Saved trips, dark](mockups/dark/05-saved-trips.png) |
| 06 | States: validation, toasts, blocking error, no safe route, cold start, partial forecast | ![States errors toasts, light](mockups/light/06-states-errors-toasts.png) | ![States errors toasts, dark](mockups/dark/06-states-errors-toasts.png) |
| 07 | How we score risk (modal; also the `/methodology` page) | ![Risk methodology, light](mockups/light/07-risk-methodology.png) | ![Risk methodology, dark](mockups/dark/07-risk-methodology.png) |
| 08 | 404 / broken share link | ![Not found, light](mockups/light/08-not-found.png) | ![Not found, dark](mockups/dark/08-not-found.png) |
| 09 | Mobile results (390 px): bottom sheet, compact slider | ![Mobile results, light](mockups/light/09-mobile-results.png) | ![Mobile results, dark](mockups/dark/09-mobile-results.png) |

All data in the mockups is sample data. The map in the mockups is a stand-in drawing; the real app uses MapLibre with real tiles.

## 10. Content guidelines

- Sentence case everywhere ("Find safest route", not "Find Safest Route").
- Name things the same way in every screen: **route**, **checkpoint**, **load**, **departure**, **No travel**.
- Always show units (mph, in/hr, mi, lb) and time zones (CST, MST).
- Errors say what happened and what to do next, and keep the user's input.
