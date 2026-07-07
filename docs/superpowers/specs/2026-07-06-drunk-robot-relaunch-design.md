# Drunk Robot Relaunch: Design

**Date:** 2026-07-06
**Status:** Approved pending user spec review

## Goal

Resurrect drunk-robot.com, a webcomic site that ran on WordPress + ComicPress from roughly 2011 to 2016 and is now offline. Recover the comics (images, titles, dates, post text) from the Internet Archive's Wayback Machine, rebuild the site as a modern static Astro site, publish the source to `git@github.com:radwizindustries/drunkrobot.git`, and deploy the built site to the user's Hostinger server, where the drunk-robot.com domain already points.

## Decisions Made

- **Recovery scope:** best-effort recovery of all comics. Accept that some may be unrecoverable if Wayback never captured them.
- **Sub-strips** (`chuck-hero`, `reboot`, `bing`, `space-time-improbability`, `total-recall-reboot`, etc.): ordinary comic posts, same treatment as everything else, one unified archive.
- **Legacy features:** dropped. No comments, no RSS, no share buttons, no buy-print. Clean archive plus an about page.
- **Visual direction:** Panel Noir: bold, high-contrast, near-black background, signature red comic-gutter framing, condensed display type.
- **Homepage:** Classic Reader: the latest strip with First / Prev / Random / Next navigation.
- **Recovery method:** purpose-built Python crawl script kept in the repo (reproducible, produces a recovery report), not a bulk mirror tool or ad-hoc fetching.
- **Deploy method:** GitHub Actions builds on push to `main` and uploads over FTPS to Hostinger. Chosen because it works on every Hostinger plan, unlike hPanel's Git feature.

## What the Archive Contains (verified)

- Old stack: WordPress with the ComicPress theme, custom child theme `newdr`.
- Comic images: `http://drunk-robot.com/comics/YYYY-MM-DD.jpg` (one early `.gif`), thumbnails at `/comics-mini/`.
- 50+ post slugs visible in CDX captures, spanning 2011-05 to at least 2015-09. Two URL eras: dated (`/2011/05/23/cosplay-faux-pas/`) and root-level slugs (`/cosplay-faux-pas/`).
- Several posts survive only as RSS `/feed/` captures, which still contain title, date, and body text.
- Coverage is uneven; there are known gaps. A single complete archive listing does not exist in Wayback.

## Component 1: Recovery Script

`scripts/recover.py`, Python 3 stdlib only. Four passes:

1. **Discover**: query the Wayback CDX API for all captures under `drunk-robot.com/*`. Seed a candidate post list from root-level slug pages, dated post URLs, `?p=NNN` WordPress IDs, and category/author archive listing pages.
2. **Crawl**: fetch the best snapshot of each candidate post. Follow prev/next navigation links inside fetched pages to discover posts CDX never indexed. Parse feed snapshots for posts that survive only as RSS.
3. **Extract**: per post: title, publish date, slug, comic image filename, author commentary HTML. Download each comic image, preferring the largest capture when several exist.
4. **Report**: emit `src/data/comics.json` and `recovery-report.md` (recovered / known-but-unrecoverable / ambiguous items for human review).

### Data model (`src/data/comics.json`)

One record per comic:

```json
{
  "slug": "cosplay-faux-pas",
  "title": "Cosplay Faux Pas",
  "date": "2011-05-23",
  "image": "2011-05-23.gif",
  "body": "<p>optional author commentary HTML</p>",
  "source": "https://web.archive.org/web/20130903160646/http://drunk-robot.com/cosplay-faux-pas/"
}
```

Images land in `public/comics/` with their original `YYYY-MM-DD.*` filenames. Script, JSON, and images are all committed; the live site never depends on archive.org.

## Component 2: Astro Site

Fully static output. Pages:

| Route | Purpose |
|---|---|
| `/` | Classic Reader showing the latest strip: Panel Noir frame, title, date, commentary, First / Prev / Random / Next |
| `/comic/[slug]/` | Same reader for every strip; prev/next ordered by date |
| `/archive/` | Thumbnail grid of all strips, newest first, title + date |
| `/about/` | Short history of the comic and its 2011–2016 run |
| old WP URLs | Static redirect stubs from `/<slug>/` and `/YYYY/MM/DD/<slug>/` to `/comic/<slug>/` |

Comics load through Astro's content-collection API backed by `comics.json`. Adding a comic later = one image file + one JSON record. The only client-side JavaScript is the Random button (picks a slug at click time); everything else ships zero JS.

### Design system: Panel Noir

- Background near-black `#111`, body text white/off-white, secondary text gray.
- Signature red `#e0263f`: thick border frame around the strip (comic-gutter effect), logo accent (DRUNK**ROBOT**), active nav states.
- Type: condensed display face for logotype and comic titles (self-hosted webfont, no third-party font CDN); system sans for body.
- Responsive: strip scales to viewport width; on mobile the reader nav becomes a fixed bottom bar.

## Component 3: Repo + Deploy

- Everything in `git@github.com:radwizindustries/drunkrobot.git` (currently empty, SSH access verified). `main` is the deploy branch.
- GitHub Actions workflow on push to `main`: checkout → Node 20 → `npm ci && npm run build` → `SamKirkland/FTP-Deploy-Action` uploads `dist/` to `public_html/` over FTPS. Incremental sync.
- Credentials as repo secrets: `HOSTINGER_FTP_HOST`, `HOSTINGER_FTP_USER`, `HOSTINGER_FTP_PASSWORD`. Never committed, never pasted in chat; user copies them from hPanel into GitHub settings.

## Error Handling

- Recovery script: a failed fetch retries with backoff, then logs to the report rather than aborting the run. Ambiguous extractions (missing title, undated post) go in the report's review section instead of silently guessing.
- Build: every record in `comics.json` must produce a page; malformed records fail the Astro build loudly rather than dropping comics.
- Deploy: workflow fails visibly in GitHub Actions on build or upload error; nothing partial goes live silently (FTPS sync only runs after a successful build).

## Verification

1. **Recovery checkpoint:** user reviews `recovery-report.md` before the site is built around the data.
2. **Local preview:** run the dev server and check the reader, archive grid, redirects, and mobile layout against real data.
3. **Post-deploy:** confirm live homepage, several comic pages, and the archive at `https://drunk-robot.com`.

## Out of Scope

- Comments, RSS, social share, merch/buy-print features.
- New comic authoring workflow beyond "add image + JSON record."
- Preserving WordPress internals (feeds, xmlrpc, query-string URLs) beyond the human-facing redirect stubs.
