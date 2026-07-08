# Changelog

All notable changes to drunk-robot.com. Format follows
[Keep a Changelog](https://keepachangelog.com); versions are tagged
`vX.Y.Z` in git.

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
