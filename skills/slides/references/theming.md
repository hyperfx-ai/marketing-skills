---
name: Theming
description: Available themes, how to select one, and CSS variable customization.
---

## Setting a Theme

Set the `theme` field in `meta` inside `src/slides.json`:

```json
{
  "meta": {
    "title": "My Presentation",
    "author": "Author Name",
    "theme": "pitch-dark",
    "brandColor": "#3b82f6"
  }
}
```

The theme controls background colors, text colors, typography, card styles, and visual personality. The `brandColor` is used for accents (bullets, stat values, section labels, decorative bars) across all themes.

## Available Themes

| Theme | Background | Feel | Best For |
|-------|------------|------|----------|
| `pitch-dark` | Near-black (#050505) | Deep contrast, subtle glowing accents, large card radius (24px) | Investor pitch decks, product demos, tech talks |
| `minimal-swiss` | Light grey (#f4f4f5) | Ultra-clean, monochrome, sharp typography, zero border radius | Corporate reports, data presentations, formal decks |
| `neo-brutal` | Vibrant yellow (#ffdf00) | High contrast, thick borders (4px), offset box shadows, uppercase titles | Creative agencies, bold announcements, startup pitches |
| `editorial-nature` | Light sage (#e8ece7) | Elegant, muted earth tones, serif headings (Playfair Display), italic style | Thought leadership, editorial content, sustainability topics |

### Legacy Themes

These are also available but less polished:

| Theme | Background | Notes |
|-------|------------|-------|
| `dark` | Dark navy (#0a0a0f) | Generic dark theme |
| `light` | Off-white (#fafafa) | Generic light theme |
| `corporate` | Deep blue (#0f172a) | Traditional corporate palette |
| `creative` | Deep purple (#1a0533) | Purple-toned creative palette |

## Brand Color

The `brandColor` hex value overrides the `--brand-color` CSS variable. It is used for:

- Bullet point markers
- Stat card values
- Section labels
- Title slide accent bar
- Column headings
- Quote marks
- Progress bar

Pick a brand color that contrasts well with the theme's background. Examples:

| Theme | Good brand colors |
|-------|-------------------|
| `pitch-dark` | `#3b82f6` (blue), `#10b981` (green), `#f59e0b` (amber) |
| `minimal-swiss` | `#000000` (black), `#dc2626` (red), `#2563eb` (blue) |
| `neo-brutal` | `#000000` (black), `#dc2626` (red) — keep high contrast on yellow |
| `editorial-nature` | `#15803d` (green), `#92400e` (brown), `#1e40af` (deep blue) |

## CSS Variable System

Themes are implemented as CSS variable overrides on `[data-theme="<name>"]`. The variables:

| Variable | Controls |
|----------|----------|
| `--bg` | Main slide background |
| `--bg-secondary` | Section slide background |
| `--fg` | Body text color |
| `--fg-muted` | Subtitles, captions, labels |
| `--fg-heading` | Heading text color |
| `--accent` | Derived from `--brand-color` |
| `--surface` | Card/column backgrounds |
| `--surface-border` | Card border color |
| `--font-heading` | Heading font stack |
| `--font-body` | Body font stack |
| `--card-radius` | Card corner radius |
| `--card-shadow` | Card box shadow |
| `--border-width` | Card border thickness |

## Custom Font Overrides

Set `fontHeading` and `fontBody` in the meta object to override the theme's defaults:

```json
{
  "meta": {
    "theme": "pitch-dark",
    "brandColor": "#3b82f6",
    "fontHeading": "Poppins",
    "fontBody": "Source Sans Pro"
  }
}
```

The fonts must be available in the browser (Google Fonts can be loaded via a `<link>` tag in `index.html`).
