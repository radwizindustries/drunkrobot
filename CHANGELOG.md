# Changelog

All notable changes to drunk-robot.com. Format follows
[Keep a Changelog](https://keepachangelog.com); versions are tagged
`vX.Y.Z` in git.

## [3.0.0] - Unreleased "Phosphor"

### Added
- **Phosphor theme:** a green-screen CRT "barcade" redesign. New design
  system in `src/styles/global.css` (near-black + phosphor green + amber,
  VT323 + Press Start 2P, a reduced-motion-gated scanline/vignette overlay).
- **Single-column homepage:** terminal search, latest strip in a CRT screen,
  title/byline/body, author boxes, transcript, mini-game, terminal-menu nav.
- **Drunk Stagger:** an 8-bit `<canvas>` dodge-runner (`src/scripts/
  drunk-stagger.js`), lazy-loaded on first click so no game code is in first
  paint; keyboard + touch; high score in `localStorage`.
- **Easter eggs:** Matrix rain (`neo`/`wake up neo`/`matrix` in search),
  Konami code (screen glitch + mini-game cheat), refreshed console greeting;
  kept the `boop` → `/terminal/` egg.
- **AdSense scaffolding** (`AdSlot.astro`), disabled by default behind
  `PUBLIC_ADSENSE_ENABLED`; the ad loader is gated by the same flag.

### Changed
- Reskinned reader, archive, search, about, 404, and terminal to Phosphor.
  Archive thumbnails now use `object-fit: contain`. Comic art always renders
  on white, above the CRT overlay.

### Removed
- All visible "Internet Archive" / "Wayback Machine" / "restored" copy
  (`site.ts` `SITE_DESCRIPTION`, About page, footer). Strip images unchanged
  pending the artist's backup.

## [2.0.1] - 2026-07-07

### Changed
- Upgraded Astro 5 to 7 (with Zod 4): `z` now imports from `astro/zod`,
  `source` uses `z.url()`, and `compressHTML: true` is pinned to keep
  spaces around inline elements (Astro 7 defaults to JSX-style stripping).
  Clears all `npm audit` advisories (previously 1 high, 1 low against
  Astro 5's bundled toolchain). No user-facing changes.

## [2.0.0] - 2026-07-07 "The Reboot"

### Added
- `transcript`, `altText`, `hoverText`, `tags`, `characters` fields on
  every strip; all 7 recovered strips backfilled with real transcripts.
- Full-text search at `/search/` (Pagefind, built at build time from the
  visible transcripts), with `?q=` deep links, a header link, and an
  archive search box.
- Full-content RSS feed at `/rss.xml` (strip image + hover text in items),
  autodiscovery tag, footer link.
- SEO/AEO layer: `ComicStory`/`ComicSeries` + `BreadcrumbList` JSON-LD per
  strip, `WebSite` + `SearchAction`, `AboutPage` + `FAQPage`; rewritten
  About page with FAQ; generated `/llms.txt`; transcript-derived meta
  descriptions; centralized entity signals (`src/lib/site.ts`).
- Reader UX: keyboard (arrow keys) and swipe navigation, Prev/Next
  duplicated above the strip, collapsible on-page transcript, hover-text
  tap target, next-strip image preload, random-without-repeats,
  continue-reading resume link on the homepage.
- Light theme with a LIGHTS toggle (OS preference honored, choice stored).
- Easter eggs: "ROBOT MEMORY CORRUPTED" 404, `/terminal/` DR-OS console,
  devtools console greeting, `boop` trigger.
- `CHANGELOG.md`, comprehensive `README.md`.

### Changed
- "Misprint" design system: ink-stroke comic-panel chrome, off-register red
  offset signature, amber LED accent, monospace robot readouts, archive
  grouped by year, WCAG AA link/focus colors in both themes.
- Per-strip `<title>` format is now `#NNN – Title | Drunk Robot`.
- `deploy/nginx.conf` (apply manually on the VPS): CSP `script-src` gains
  `'wasm-unsafe-eval'` for Pagefind; `error_page 404 /404.html` serves the
  themed 404.

## [1.0.0] - 2026-07 (retro-tagged)

Wayback restoration baseline: Astro 5 static site with 7 recovered strips,
comic reader with First/Prev/Random/Next/Last, archive grid, about page,
legacy URL redirects, sitemap, OG/Twitter meta, GA4 + AdSense, GitHub
Actions rsync deploy to the Hostinger VPS.
