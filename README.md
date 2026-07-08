# Drunk Robot

The website for Drunk Robot, a webcomic written by Brian Powell and drawn by
Jeff Pina. It ran weekly from 2011 to 2016 and is publishing again. Live at
<https://drunk-robot.com>.

> **Keep this README current.** Whenever the site changes (new features,
> layout changes, new pages, workflow changes), update the relevant section
> here in the same change. This file is the single source of truth for how
> the site is built, laid out, and operated.

## Stack

- [Astro 7](https://astro.build), fully static output (no SSR, no backend);
  `compressHTML: true` is pinned in `astro.config.mjs` because Astro 7's
  JSX-style default strips the deliberate spaces around inline elements
- [Pagefind](https://pagefind.app) for build-time full-text search
- [@astrojs/rss](https://docs.astro.build/en/recipes/rss/) for the feed
- Vitest for unit tests
- Node 22, npm

## Commands

    npm install        # once
    npm run dev        # dev server at localhost:4321 (search index absent in dev)
    npm test           # vitest (nav logic)
    npm run build      # astro build + pagefind index -> dist/
    npm run preview    # serve dist/ locally

## Site layout (pages and URLs)

| URL | Source | Purpose |
|-----|--------|---------|
| `/` | `src/pages/index.astro` | Single-column "arcade cabinet" homepage: terminal search, the latest strip in a CRT screen, title/byline/body, author boxes, transcript, the Drunk Stagger mini-game, and a terminal-menu nav. |
| `/comic/<slug>/` | `src/pages/comic/[slug].astro` | One page per strip, the SEO unit. **Never break these URLs.** |
| `/archive/` | `src/pages/archive.astro` | Every strip, grouped by year, with thumbnails and a search box. |
| `/search/` | `src/pages/search.astro` | Pagefind full-text search over transcripts. Supports `?q=` deep links. |
| `/about/` | `src/pages/about.astro` | Answers what/who/when in the first sentences; FAQ with `FAQPage` schema. |
| `/terminal/` | `src/pages/terminal.astro` | Easter egg: fake DR-OS console (strip lookup, `reboot`, drinks). |
| `/404.html` | `src/pages/404.astro` | "ROBOT MEMORY CORRUPTED" screen linking Random/Search/Archive. |
| `/rss.xml` | `src/pages/rss.xml.ts` | Full-content feed: strip image + hover text in each item. |
| `/sitemap.xml` | `src/pages/sitemap.xml.ts` | Single flat sitemap (hand-rolled; 50k-URL sharding is irrelevant here). |
| `/llms.txt` | `src/pages/llms.txt.ts` | Markdown index for AI crawlers/answer engines, generated from the collection. |
| `/robots.txt` | `public/robots.txt` | Allows everything, including AI crawlers, on purpose. |

Legacy WordPress-era URLs (`/<slug>`, `/YYYY/MM/DD/<slug>`) redirect to
`/comic/<slug>/` via the `redirects` map built in `astro.config.mjs`.

## Content model

Strips live in `src/data/comics.json`, loaded as the `comics` content
collection (schema in `src/content.config.ts`). Fields per strip:

| Field | Required | Purpose |
|-------|----------|---------|
| `slug` | yes | Stable, descriptive URL segment. Never change after publishing. |
| `title` | yes | Display title. |
| `date` | yes | `YYYY-MM-DD`; drives ordering, archive grouping, RSS dates. |
| `image` | yes | Filename inside `public/comics/`. |
| `body` | yes (may be `""`) | Author commentary HTML shown under the strip. |
| `source` | yes | Wayback provenance URL for recovered strips. |
| `transcript` | yes | Full dialogue/action text, `Panel N.` per line. Powers search, SEO, AEO, and accessibility. The single highest-leverage field. |
| `altText` | yes | Describes the image for screen readers. altText describes, hoverText jokes. |
| `hoverText` | yes | The xkcd-style second punchline (img `title`, `···` tap target, RSS body, llms.txt). |
| `tags` | no | Topic tags (feed JSON-LD keywords; future hub pages). |
| `characters` | no | Reserved for future character tagging. |

### Publishing a new strip

1. Drop the image into `public/comics/` (name it `YYYY-MM-DD.ext`).
2. Append an entry to `src/data/comics.json` with every required field,
   including a real transcript, altText, and hoverText.
3. `npm run build` locally; the homepage, archive, sitemap, RSS, llms.txt,
   and search index all update from the collection automatically.
4. Commit and push to `main`; GitHub Actions deploys.

**Caution:** `scripts/recover.py` (the Wayback recovery crawler) regenerates
`comics.json` with only the base fields. Recovery is essentially complete
(the Wayback Machine captured just 8 comic images for the domain; 7 were
recovered), so don't re-run it without merging the hand-written
transcript/altText/hoverText fields back in.

## Design system ("Phosphor")

Green-screen CRT barcade. Defined in `src/styles/global.css` as CSS custom
properties; components keep their own scoped styles.

- **Themes:** dark ("attract mode", default) and light, toggled by the header
  LIGHTS button. Stored choice (`localStorage.dr-theme`) wins, else
  `prefers-color-scheme`, else dark. A `data-theme` attribute is set on
  `<html>` before first paint. The comic art itself is never dimmed or
  filtered by either theme, and always renders on white.
- **Palette:** near-black `#040805` background, phosphor green `#39ff88`
  text, amber `#ffb000` accents/warnings, dim green `#2fbf68` for secondary
  text, `#173a22` hairlines. Light mode uses dark green on warm paper.
- **Signature:** a fixed decorative CRT overlay (scanlines + vignette,
  `aria-hidden`, `prefers-reduced-motion`-gated). Comic art (`.screen`,
  `.frame`, archive `.thumb`) is lifted above the overlay so scanlines never
  fall on the strips.
- **Type:** VT323 for body/UI (the terminal readout font) and Press Start 2P
  (`.pix`) for pixel headings and marquees.
- **Components:** `.screen` (CRT frame), `.terminal-input` (`grep>` search),
  `.btn-arcade` / `.btn-panel` (arcade buttons), `.menu` / `.menu-row`
  (terminal nav), `.auth` (author boxes), `details.transcript`, `.card-panel`.
  A small compat layer aliases v2 class/var names onto Phosphor tokens.
- **Accessibility:** `:focus-visible` amber outline, alt text on every strip,
  transcripts as structured text, and all animation (scanlines, cursor blink,
  Matrix rain, the mini-game) gated behind `prefers-reduced-motion`.

## Mini-game: Drunk Stagger

An 8-bit dodge-runner on the homepage (`src/scripts/drunk-stagger.js`, vanilla
`<canvas>`, no engine). The robot auto-runs a neon street; Space/tap hops over
lampposts and potholes, bolts score points, it speeds up, high score persists
in `localStorage` (`dr-stagger-hi`; logic + tests in `src/lib/stagger-score.ts`).
It is dynamically `import()`-ed on first click (`src/scripts/stagger-boot.ts`),
so no game code ships in the homepage's first paint. The Konami code grants a
session cheat (extra lives). Reduced-motion shows a static "tap to play" cabinet.

## Reader features

- First / Prev / Random / Next / Last panel buttons under the strip, with a
  compact Prev/Next pair above it; on phones the main nav is a fixed bottom
  bar. Left/right arrow keys and swipe gestures also navigate.
- Random never repeats a strip within a session (`sessionStorage.dr-seen`).
- Comic pages record the last-read slug (`localStorage.dr-last`) for future
  use; the homepage always shows the latest strip.
- Each strip page shows a collapsible transcript; hover text lives on the
  image `title` and behind the `···` tap target for touch screens.
- The next strip's image is preloaded from each comic page.

## SEO / AEO

- Unique per-strip `<title>` (`#NNN – Title | Drunk Robot`) and meta
  description pulled from the transcript's first line.
- JSON-LD: `ComicStory` (with transcript text) inside a `ComicSeries` +
  `BreadcrumbList` per strip; `WebSite` + `SearchAction` on the homepage;
  `AboutPage` + `FAQPage` on About. Entity signals (site name, description,
  authors) are centralized in `src/lib/site.ts`; always pull from there.
- Visible transcripts are the indexable text for an image-heavy site, and
  what lets answer engines cite strips.
- `llms.txt`, permissive `robots.txt`, canonical URLs, OG/Twitter cards
  with the strip image.

## Easter eggs

Cheap, additive, never gating real navigation (detectors in
`src/lib/eastereggs.ts`, wiring in `src/scripts/site-eggs.ts`):

- **Matrix rain:** searching `neo`, `wake up neo`, or `matrix` triggers a
  full-screen green glyph rain (dismiss with any key/click).
- **Konami code** (↑↑↓↓←→←→ B A) anywhere: a screen glitch + a `dr:konami`
  event; on the homepage it grants the mini-game a session cheat.
- **Console greeting** on load; hover text on every strip; typing `boop`
  opens the `/terminal/` DR-OS console; and the themed "GAME OVER" 404.

## Ads

Display ads are scaffolded but off. `src/components/AdSlot.astro` renders
nothing until `PUBLIC_ADSENSE_ENABLED=true` (and `PUBLIC_ADSENSE_CLIENT`);
the AdSense loader in `Base.astro` is gated by the same flag, so no ad script
ships by default. Slots exist on the homepage and comic pages.

## Recovery (history)

The 2011-2016 archive was recovered by `scripts/recover.py` (Python 3,
stdlib only), which crawled Wayback Machine captures of the original
WordPress/ComicPress site and emitted `src/data/comics.json`,
`public/comics/`, and `recovery-report.md`. Fetches are cached in
`scripts/.cache/`. The Wayback Machine only captured 8 comic images for the
domain; 7 strips were recoverable. See the caution above before re-running.

## Deploy

The site runs on a Hostinger VPS behind Traefik, alongside other sites,
served from an `nginx:alpine` container. Pushes to `main` build the site
and rsync `dist/` over SSH to `/opt/drunk-robot-site/dist/` via GitHub
Actions (`.github/workflows/deploy.yml`).

Secrets: `HOSTINGER_SSH_HOST`, `HOSTINGER_SSH_USER`, `HOSTINGER_SSH_KEY`.

**`deploy/docker-compose.yml` and `deploy/nginx.conf` are reference copies**
of what's provisioned on the VPS; the workflow does not apply them. When
they change in this repo, apply them on the VPS manually and reload nginx.
The v2.0.0 release changed nginx.conf twice: CSP `script-src` gained
`'wasm-unsafe-eval'` (Pagefind's WASM ranking engine) and `error_page 404
/404.html` now serves the themed 404.

## Releases

- Semantic-ish versioning for a site: major = redesign/feature era, minor =
  features, patch = fixes. Version lives in `package.json`.
- Work happens on feature branches (`feat/...`), merged to `main` with
  `--no-ff`, tagged `vX.Y.Z` (annotated), pushed with tags, and published
  as a GitHub release. `CHANGELOG.md` follows Keep a Changelog.
- `v1.0.0` = Wayback restoration baseline. `v2.0.0` = "The Reboot"
  (redesign, transcripts, search, RSS, SEO/AEO layer, easter eggs).

## Roadmap (non-goals for now)

New strips resume publishing; remaining plan items: responsive AVIF/WebP
images via the Astro image pipeline, tag/character hub pages. Deliberately
out of scope: comments, newsletter, accounts, merch, webtoon vertical
format.
