# Drunk Robot — "Phosphor" Theme (v3, fresh)

**Date:** 2026-07-08
**Branch:** `feat/phosphor-theme` (off `main` / v2.0.1)
**Status:** Approved design, pre-implementation

## Goal

A fresh, distinctive, professional-but-fun theme for drunk-robot.com with a
barcade feel, replacing the abandoned "Insert Coin" arcade attempt (`feat/arcade-v3`,
which is discarded, not merged). Keep all of v2's structure — content
collections, nav helpers, SEO/AEO infrastructure, RSS/sitemap/llms.txt — and
rebuild only the presentation layer, plus add a playable mini-game and refreshed
easter eggs.

Non-goals: replacing strip artwork (the artist's backup is pending; images stay
as-is), changing the content schema, changing hosting/deploy.

## Art Direction — "Phosphor"

Green-screen CRT barcade. One cohesive system, light/dark aware but dark-first.

| Token | Value | Use |
|-------|-------|-----|
| `--bg` | `#040805` | page background (near-black) |
| `--panel` | `#0a0f0a` | cards, screens |
| `--green` | `#39ff88` | primary text / phosphor |
| `--green-dim` | `#2fbf68` | secondary text |
| `--amber` | `#ffb000` | accents, warnings, "now playing" |
| `--edge` | `#173a22` | borders/hairlines |
| `--mute` | `#5c8a6c` | muted/meta text |

- **Type:** `@fontsource/vt323` (body/UI terminal font) + `@fontsource/press-start-2p`
  (pixel headings, marquees). Remove `@fontsource/anton` if unused after migration.
- **CRT treatment:** subtle scanline overlay + vignette. Bloom/glow on phosphor text.
  All flicker/scanline animation gated behind `prefers-reduced-motion: no-preference`.
- **Light mode:** the theme toggle stays (existing `dr-theme` localStorage + pre-paint
  inline script in `Base.astro`). Light mode lightens the "room" but strip art always
  renders on white, unfiltered, in both themes.
- Rebuild `src/styles/global.css` from scratch on these tokens. Delete the old
  Insert-Coin variables.

## Homepage (`src/pages/index.astro`) — single column

Single reading-order column (good for SEO/AEO + mobile). Top to bottom:

1. **Top bar** — `DRUNK_ROBOT` wordmark + terminal search input (`grep>` prompt) + theme toggle.
2. **Boot line** — one flavor line (e.g. strip count, "last call 2016 > rebooted").
3. **Central CRT screen** — the latest strip, framed as the cabinet screen. Art on white.
4. **Title block** — `#NNN` (padded) + strip title + date + byline (Powell & Pina).
5. **Body copy** — the strip's `body` / author's note.
6. **Author boxes** — Brian Powell (writer) · Jeff Pina (artist).
7. **Transcript** — collapsible `TRANSCRIPT.txt` (`<details>`), open by default, from `transcript`.
8. **Drunk Stagger** — the mini-game panel (see below).
9. **Terminal-menu nav** — Archive / Search / About / RSS as a terminal list.
10. **Footer** — copyright + creators.

## Mini-game — "Drunk Stagger"

- Vanilla `<canvas>` + a single plain JS module (`src/scripts/drunk-stagger.js`),
  dynamically `import()`-ed on first interaction. Not an Astro island, no
  game-engine dependency.
- Gameplay: the Drunk Robot auto-runs a neon street; **Space / tap = hop**; dodge
  lampposts and potholes; collect bolts/beers for score. Endless, speeds up over time.
- HUD: `SCORE` + `HI` (high score persisted in `localStorage`, key `dr-stagger-hi`).
- **Performance:** lazy — the game code loads only on first interaction (click "PRESS
  START" or scroll into view via `IntersectionObserver`), so it never affects first paint
  or Lighthouse. Homepage HTML renders the comic/SEO content without it.
- **Accessibility:** full keyboard + touch; pause on blur/`Esc`; under
  `prefers-reduced-motion: reduce` it does not auto-animate — shows a static "cabinet"
  with an explicit "Play anyway" opt-in.
- Konami cheat hook (see easter eggs).

## Other pages (all reskinned to Phosphor)

- **Comic reader** (`src/pages/comic/[slug].astro`, `ComicReader.astro`): strip on white,
  prev/next/random as arcade buttons, title/date, transcript, author boxes, hoverText as
  the xkcd-style second punchline. Keep existing nav logic (`comicNav.ts`).
- **Archive** (`archive.astro`): "HIGH SCORES" table grouped by year.
- **Search** (`search.astro`): Pagefind stays the engine, wrapped in a `grep>` terminal UI
  (see easter eggs for query-triggered eggs).
- **About** (`about.astro`): reskinned + copy rewrite (see Content Changes).
- **404** + **/terminal/**: keep as full easter-egg pages, reskinned to Phosphor.
- **RSS / sitemap / llms.txt** (`rss.xml.ts`, `sitemap.xml.ts`, `llms.txt.ts`): behavior
  unchanged; only copy that references the Internet Archive is updated.
- **Mascot** (`Mascot.astro`): keep the reactive Drunk Robot mascot; restyle to phosphor,
  keep the boop easter egg.

## Search + Easter Eggs

Engine: Pagefind (unchanged). Terminal-styled input with a blinking cursor.

Easter eggs (all non-blocking, skippable, reduced-motion aware):
1. **Matrix rain** — search query `neo`, `wake up neo`, or `matrix` → full-screen green
   Matrix character rain scroll, dismissible with any key/click.
2. **Konami code** — `↑↑↓↓←→←→ B A` anywhere on the site → a screen "glitch" + a bolt
   confetti burst; on the homepage it also grants the mini-game a cheat (extra lives /
   turbo) for the current session. Marquee/console acknowledges it.
3. **Console message** — a styled ASCII message logged on load.
4. **Mascot boop** — clicking the mascot triggers a reaction animation (carried over).

## Content Changes — remove Internet Archive references

Rewrite visible "restored from the Internet Archive / Wayback Machine" copy. Reframe as
"a webcomic by Brian Powell & Jeff Pina, ran 2011–2016, rebooted and publishing again."
Known locations:
- `src/lib/site.ts` — `SITE_DESCRIPTION` (drop the "restored from the Internet Archive" clause).
- `src/pages/about.astro` — FAQ answer + prose paragraph + the `web.archive.org` link.
- Verify no other surface (RSS/llms.txt/JSON-LD) hardcodes archive copy; they pull from
  `site.ts`, so the `site.ts` edit propagates.

Keep the per-strip `source` URL field in the data (it is metadata, not visible copy).
Leave strip images untouched pending the artist's backup.

## SEO / AEO

Keep and tighten v2's work, adapted to new markup:
- Per-page `<title>`/meta/OG/Twitter via `Base.astro` (unchanged plumbing).
- JSON-LD: `WebSite` + `SearchAction` on home; `ComicStory`/`CreativeWork` per strip;
  `ComicSeries` via `site.ts` helper.
- Sitemap, RSS, `llms.txt`, semantic heading order, alt text all preserved.
- Single-column reading order improves answer-engine extraction.
- CRT/scanline overlays must be decorative (`aria-hidden`, pointer-events:none) and never
  wrap real content.

## AdSense (deferred, scaffolding only)

Add an `<AdSlot>` Astro component that renders nothing unless a config flag
(`ADSENSE_ENABLED`) + publisher ID are set. Reserve two placements — below the strip and
above the footer — sized to avoid layout shift when later enabled. No AdSense script ships
until the flag flips.

## Tech / Constraints

- Astro 7, static output, `compressHTML: true` kept. Content collections + schema untouched.
- New dep: `@fontsource/vt323`. Remove `@fontsource/anton` if orphaned.
- No heavy client frameworks; mini-game is vanilla JS, loaded lazily.
- Existing tests (`comicNav.test.ts`) must still pass; add a small unit test for the game's
  score/high-score persistence logic if it is extracted as a pure function.
- Deploy unchanged (push to `main` auto-deploys; nginx changes remain manual — not needed here).

## Success Criteria

1. `npm run build` succeeds; `npm test` passes; no new npm audit advisories.
2. Home, reader, archive, search, about, 404, /terminal/ all render in the Phosphor theme,
   light + dark.
3. Latest strip, title, date, body, author boxes, and transcript all present on the homepage.
4. Drunk Stagger is playable via keyboard and touch, persists a high score, and does not
   load until interaction (verified: homepage first paint has no game JS).
5. Matrix, Konami, console, and boop easter eggs all fire.
6. No visible Internet Archive / Wayback copy remains anywhere on the site.
7. Lighthouse SEO ~100 retained; JSON-LD validates; sitemap/RSS/llms.txt intact.
8. `prefers-reduced-motion: reduce` disables CRT animation and game auto-motion.
