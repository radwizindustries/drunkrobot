# Drunk Robot "Phosphor" Theme Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Rebuild drunk-robot.com's presentation as a green-screen CRT "barcade" theme with a single-column homepage, a playable canvas mini-game, and refreshed easter eggs, keeping all v2 content/SEO infrastructure.

**Architecture:** Astro 7 static site. A rebuilt `global.css` defines the "Phosphor" design system (tokens + reusable primitives); every page composes those classes. Pure logic (easter-egg detectors, game scoring) lives in plain, unit-tested JS/TS modules; the canvas game is dynamically imported on first interaction so it never affects first paint.

**Tech Stack:** Astro 7, TypeScript, Vitest, Pagefind, `@fontsource/vt323`, `@fontsource/press-start-2p`. No client framework; game is vanilla `<canvas>`.

## Global Constraints

- Astro `^7.0.6`; static output; `compressHTML: true` stays in `astro.config.mjs`.
- No new heavy runtime deps. Allowed new deps: `@fontsource/vt323`, `@fontsource/press-start-2p`. Remove `@fontsource/anton` once orphaned.
- Content collection schema (`src/content.config.ts`) and `src/data/comics.json` are UNCHANGED. Strip images UNCHANGED.
- Writing style: no em dashes (—) in any site copy or docs. Use commas/periods.
- No visible "Internet Archive" / "Wayback Machine" / "restored" copy anywhere on the site.
- All decorative CRT overlays are `aria-hidden` + `pointer-events:none` and never wrap real content.
- All animation (scanlines, flicker, game auto-motion, Matrix rain) gated behind `prefers-reduced-motion: no-preference`.
- Every task ends green: `npm test` passes and `npm run build` succeeds.
- Commit after every task. Conventional Commits. Never commit to `main`; work stays on `feat/phosphor-theme`.

## Design tokens (authoritative — copy exactly)

```
--bg:#040805; --panel:#0a0f0a; --green:#39ff88; --green-dim:#2fbf68;
--amber:#ffb000; --edge:#173a22; --edge2:#0f2416; --mute:#5c8a6c; --ink:#eafff2;
```

## File Structure

- `src/styles/global.css` — REBUILT. Tokens + primitives (`.crt`, `.screen`, `.marquee`, `.pix`, `.btn-arcade`, `.menu`, `.auth`, `.terminal-input`, etc.). Light/dark via `[data-theme]`.
- `src/layouts/Base.astro` — MODIFY: font imports, decorative scanline/vignette overlay, theme toggle already present.
- `src/lib/site.ts` — MODIFY: `SITE_DESCRIPTION` archive clause removed.
- `src/lib/eastereggs.ts` — CREATE: pure detectors (`isMatrixQuery`, `KonamiDetector`). Unit-tested.
- `src/lib/stagger-score.ts` — CREATE: pure score/hi-score logic. Unit-tested.
- `src/scripts/drunk-stagger.js` — CREATE: canvas game module, dynamically imported.
- `src/scripts/site-eggs.ts` — CREATE: wires Konami + console message + Matrix rain to the DOM.
- `src/components/AdSlot.astro` — CREATE: AdSense scaffolding (renders nothing unless enabled).
- `src/components/Mascot.astro` — MODIFY: restyle to phosphor.
- `src/components/ComicReader.astro` — MODIFY: reskin.
- `src/pages/index.astro` — REBUILT: single-column homepage.
- `src/pages/{about,archive,search,404,terminal}.astro`, `src/pages/comic/[slug].astro` — MODIFY: reskin.
- `src/lib/eastereggs.test.ts`, `src/lib/stagger-score.test.ts` — CREATE.

---

### Task 1: Phosphor design-system foundation (fonts + tokens + primitives)

**Files:**
- Modify: `package.json` (deps)
- Create/replace: `src/styles/global.css`
- Modify: `src/layouts/Base.astro` (font imports + decorative CRT overlay)

**Interfaces:**
- Produces CSS classes consumed by all page tasks: `.crt-overlay`, `.screen`, `.marquee`, `.pix`, `.glow`, `.btn-arcade`, `.terminal-input`, `.menu`/`.menu-row`, `.auth`, `.card-panel`, `.boot`. And CSS vars listed in Global Constraints.

- [ ] **Step 1: Swap fonts**

```bash
cd "$(git rev-parse --show-toplevel)"
npm install @fontsource/vt323 @fontsource/press-start-2p
npm uninstall @fontsource/anton
```

- [ ] **Step 2: Replace `src/styles/global.css` entirely**

```css
@import '@fontsource/vt323';
@import '@fontsource/press-start-2p';

/* Phosphor design system (v3) — green-screen CRT barcade.
   Dark ("attract mode") is default. Light lifts the room; strip art
   always renders on white, unfiltered, in both themes. */
:root {
  --bg:#040805; --panel:#0a0f0a; --green:#39ff88; --green-dim:#2fbf68;
  --amber:#ffb000; --edge:#173a22; --edge2:#0f2416; --mute:#5c8a6c; --ink:#eafff2;
  --link:var(--green); --focus:var(--amber);
  --glow:0 0 6px currentColor;
  --font-body:'VT323','Courier New',monospace;
  --font-pix:'Press Start 2P','VT323',monospace;
}
@media (prefers-color-scheme: light) {
  :root:not([data-theme]) {
    --bg:#e7ecdf; --panel:#f3f6ea; --green:#12633a; --green-dim:#1d7a49;
    --amber:#8a5a00; --edge:#b9c7ac; --edge2:#cdd8c0; --mute:#5c6a54; --ink:#12331f;
    --glow:none;
  }
}
:root[data-theme='light'] {
  --bg:#e7ecdf; --panel:#f3f6ea; --green:#12633a; --green-dim:#1d7a49;
  --amber:#8a5a00; --edge:#b9c7ac; --edge2:#cdd8c0; --mute:#5c6a54; --ink:#12331f;
  --glow:none;
}

*,*::before,*::after{ box-sizing:border-box; }
html{ background:var(--bg); }
body{
  margin:0; background:var(--bg); color:var(--green);
  font-family:var(--font-body); font-size:20px; line-height:1.5;
  min-height:100vh; position:relative; overflow-x:hidden;
}
main{ max-width:760px; margin:0 auto; padding:0 clamp(16px,5vw,40px) 48px; }
a{ color:var(--link); text-decoration:none; }
a:hover{ text-shadow:var(--glow); }
:focus-visible{ outline:2px solid var(--focus); outline-offset:2px; }
h1,h2,h3{ color:var(--ink); }

.pix{ font-family:var(--font-pix); line-height:1.4; }
.glow{ text-shadow:var(--glow); }

/* Decorative CRT overlay (added once in Base.astro, aria-hidden) */
.crt-overlay{ position:fixed; inset:0; z-index:9; pointer-events:none;
  box-shadow:inset 0 0 120px rgba(0,0,0,.7); }
@media (prefers-reduced-motion: no-preference){
  .crt-overlay::after{ content:''; position:absolute; inset:0;
    background:repeating-linear-gradient(to bottom,rgba(0,0,0,0) 0 2px,rgba(0,0,0,.28) 2px 3px);
    mix-blend-mode:multiply; }
}

/* CRT "screen" — holds the comic and other framed content */
.screen{ position:relative; border:2px solid var(--edge); border-radius:8px;
  background:var(--panel); box-shadow:inset 0 0 40px rgba(57,255,136,.12);
  padding:16px; }
.screen>.marquee{ position:absolute; top:-13px; left:50%; transform:translateX(-50%);
  background:var(--bg); padding:0 10px; font-size:9px; color:var(--amber); }

.marquee{ font-family:var(--font-pix); }

/* Strip art always on white, unfiltered, both themes */
.strip{ display:block; width:100%; height:auto; background:#fff; border-radius:4px; }

/* Terminal input (search) */
.terminal-input{ display:flex; align-items:center; gap:8px; width:100%;
  border:1px solid var(--edge); background:var(--panel); color:var(--green-dim);
  padding:8px 12px; border-radius:4px; font-family:var(--font-body); font-size:20px; }
.terminal-input input{ flex:1; background:transparent; border:0; color:var(--green);
  font:inherit; outline:none; }
.terminal-input .prompt{ color:var(--amber); }
.cursor{ color:var(--green); }
@media (prefers-reduced-motion: no-preference){ .cursor{ animation:blink 1s steps(1) infinite; } }
@keyframes blink{ 50%{ opacity:0; } }

/* Arcade buttons */
.btn-arcade{ display:inline-block; border:2px solid var(--green); color:var(--green);
  background:transparent; font-family:var(--font-pix); font-size:11px; letter-spacing:1px;
  padding:12px 18px; border-radius:4px; cursor:pointer; }
.btn-arcade:hover{ background:var(--green); color:var(--bg); }
.btn-arcade.amber{ border-color:var(--amber); color:var(--amber); }
.btn-arcade.amber:hover{ background:var(--amber); color:var(--bg); }

/* Terminal menu list */
.menu{ border-top:1px solid var(--edge); margin-top:8px; }
.menu-row{ display:flex; justify-content:space-between; gap:12px; padding:8px 2px;
  border-bottom:1px dotted var(--edge2); color:var(--green-dim); }
.menu-row b{ color:var(--green); }
.menu-row .arw{ color:var(--amber); }

/* Author boxes */
.authors{ display:flex; gap:12px; flex-wrap:wrap; margin:20px 0; }
.auth{ flex:1; min-width:150px; border:1px solid var(--edge); border-radius:6px;
  padding:10px 12px; background:var(--panel); }
.auth .k{ font-size:14px; color:var(--mute); text-transform:uppercase; letter-spacing:.5px; }
.auth .v{ font-size:20px; color:var(--green); }

/* Generic panel/card */
.card-panel{ border:1px solid var(--edge); border-radius:8px; background:var(--panel); padding:16px; }

/* Boot / flavor line */
.boot{ color:var(--mute); padding:12px 0 4px; }
.boot .ok{ color:var(--amber); }

/* Transcript */
details.transcript{ border:1px solid var(--edge); border-radius:6px; background:var(--panel); margin:8px 0 20px; }
details.transcript summary{ cursor:pointer; padding:10px 12px; color:var(--amber); list-style:none; }
details.transcript summary::-webkit-details-marker{ display:none; }
details.transcript .tbody{ padding:0 12px 12px; color:var(--green-dim); }

.visually-hidden{ position:absolute; width:1px; height:1px; overflow:hidden; clip:rect(0 0 0 0); }
```

- [ ] **Step 3: Add the CRT overlay + confirm font import path in `Base.astro`**

In `src/layouts/Base.astro`, immediately after the opening `<body>` tag, add:

```astro
<div class="crt-overlay" aria-hidden="true"></div>
```

`global.css` is already imported at the top of `Base.astro` (line 2). Do not add a second import.

- [ ] **Step 4: Verify build succeeds**

Run: `npm run build`
Expected: build completes, no error about missing `@fontsource/anton`. If any file still imports anton, remove that import.

- [ ] **Step 5: Verify no orphaned anton import remains**

Run: `grep -rn "anton" src/ || echo CLEAN`
Expected: `CLEAN`

- [ ] **Step 6: Commit**

```bash
git add package.json package-lock.json src/styles/global.css src/layouts/Base.astro
git commit -m "feat: Phosphor design system foundation (fonts, tokens, CRT primitives)"
```

---

### Task 2: Remove Internet Archive copy (TDD)

**Files:**
- Modify: `src/lib/site.ts`
- Test: `src/lib/site.test.ts` (create)
- Modify: `src/pages/about.astro` (copy strings only; reskin happens in Task 9)

**Interfaces:**
- Consumes: `SITE_DESCRIPTION` from `src/lib/site.ts`.
- Produces: `SITE_DESCRIPTION` with no archive references (all downstream: RSS, llms.txt, JSON-LD inherit it).

- [ ] **Step 1: Write the failing test** — `src/lib/site.test.ts`

```ts
import { describe, expect, it } from 'vitest';
import { SITE_DESCRIPTION } from './site';

describe('SITE_DESCRIPTION', () => {
  it('names both creators and the run years', () => {
    expect(SITE_DESCRIPTION).toMatch(/Brian Powell/);
    expect(SITE_DESCRIPTION).toMatch(/Jeff Pina/);
    expect(SITE_DESCRIPTION).toMatch(/2011/);
    expect(SITE_DESCRIPTION).toMatch(/2016/);
  });
  it('has no Internet Archive / Wayback / restored copy', () => {
    expect(SITE_DESCRIPTION).not.toMatch(/internet archive|wayback|restored/i);
  });
});
```

- [ ] **Step 2: Run test to verify it fails**

Run: `npx vitest run src/lib/site.test.ts`
Expected: FAIL on the second assertion (current text says "restored from the Internet Archive").

- [ ] **Step 3: Edit `SITE_DESCRIPTION` in `src/lib/site.ts`**

Replace the current value with:

```ts
export const SITE_DESCRIPTION =
  'Drunk Robot is a webcomic written by Brian Powell and drawn by Jeff Pina. ' +
  'It ran weekly from 2011 to 2016 and is publishing again, skewering comics, ' +
  'sci-fi, and nerd culture.';
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `npx vitest run src/lib/site.test.ts`
Expected: PASS

- [ ] **Step 5: Strip archive copy from `about.astro` prose**

In `src/pages/about.astro`, replace the two archive sentences/paragraph and the `web.archive.org` link. Concretely:
- FAQ answer that begins "The original site went offline and its strips were lost..." becomes:
  `'Drunk Robot ran weekly from 2011 to 2016. It is back online and publishing new strips.'`
- The prose paragraph beginning "The original site vanished years ago. This archive was rebuilt from ... Wayback Machine." becomes:
  `Drunk Robot ran from 2011 to 2016 and is publishing again. Every strip carries a full transcript, so the jokes are searchable and readable by everyone.`
- Remove the `<a href="https://web.archive.org">...</a>` anchor entirely.

- [ ] **Step 6: Verify no archive copy remains site-wide**

Run: `grep -rniE "wayback|internet archive|web\.archive\.org|restored" src/ || echo CLEAN`
Expected: `CLEAN`

- [ ] **Step 7: Commit**

```bash
git add src/lib/site.ts src/lib/site.test.ts src/pages/about.astro
git commit -m "feat: remove Internet Archive references from site copy"
```

---

### Task 3: Easter-egg detectors (TDD, pure logic)

**Files:**
- Create: `src/lib/eastereggs.ts`
- Test: `src/lib/eastereggs.test.ts`

**Interfaces:**
- Produces:
  - `isMatrixQuery(q: string): boolean` — true for `neo`, `wake up neo`, `matrix` (case-insensitive, trimmed).
  - `class KonamiDetector { push(key: string): boolean }` — feed `KeyboardEvent.key` values; returns `true` on the frame the full sequence `ArrowUp ArrowUp ArrowDown ArrowDown ArrowLeft ArrowRight ArrowLeft ArrowRight b a` completes; tolerates wrong keys by resetting progress.

- [ ] **Step 1: Write the failing test** — `src/lib/eastereggs.test.ts`

```ts
import { describe, expect, it } from 'vitest';
import { isMatrixQuery, KonamiDetector } from './eastereggs';

describe('isMatrixQuery', () => {
  it('matches the trigger phrases case-insensitively', () => {
    for (const q of ['neo', 'NEO', '  Wake Up Neo ', 'matrix']) {
      expect(isMatrixQuery(q)).toBe(true);
    }
  });
  it('ignores unrelated queries', () => {
    for (const q of ['robot', 'neon', '']) expect(isMatrixQuery(q)).toBe(false);
  });
});

describe('KonamiDetector', () => {
  const seq = ['ArrowUp','ArrowUp','ArrowDown','ArrowDown','ArrowLeft','ArrowRight','ArrowLeft','ArrowRight','b','a'];
  it('fires only when the full sequence completes', () => {
    const d = new KonamiDetector();
    const results = seq.map((k) => d.push(k));
    expect(results.slice(0, 9).every((r) => r === false)).toBe(true);
    expect(results[9]).toBe(true);
  });
  it('resets on a wrong key and accepts uppercase B/A', () => {
    const d = new KonamiDetector();
    d.push('ArrowUp'); d.push('x'); // wrong -> reset
    const results = seq.map((k) => d.push(k === 'b' ? 'B' : k === 'a' ? 'A' : k));
    expect(results[9]).toBe(true);
  });
});
```

- [ ] **Step 2: Run test to verify it fails**

Run: `npx vitest run src/lib/eastereggs.test.ts`
Expected: FAIL ("isMatrixQuery is not a function").

- [ ] **Step 3: Implement `src/lib/eastereggs.ts`**

```ts
const MATRIX_TRIGGERS = new Set(['neo', 'wake up neo', 'matrix']);

export function isMatrixQuery(q: string): boolean {
  return MATRIX_TRIGGERS.has(q.trim().toLowerCase());
}

const KONAMI = [
  'ArrowUp', 'ArrowUp', 'ArrowDown', 'ArrowDown',
  'ArrowLeft', 'ArrowRight', 'ArrowLeft', 'ArrowRight', 'b', 'a',
];

export class KonamiDetector {
  private i = 0;
  /** Returns true on the key press that completes the sequence. */
  push(key: string): boolean {
    const want = KONAMI[this.i];
    const got = key.length === 1 ? key.toLowerCase() : key;
    if (got === want) {
      this.i++;
      if (this.i === KONAMI.length) { this.i = 0; return true; }
      return false;
    }
    // Reset, but allow this key to start a fresh match.
    this.i = got === KONAMI[0] ? 1 : 0;
    return false;
  }
}
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `npx vitest run src/lib/eastereggs.test.ts`
Expected: PASS (both describe blocks green).

- [ ] **Step 5: Commit**

```bash
git add src/lib/eastereggs.ts src/lib/eastereggs.test.ts
git commit -m "feat: easter-egg detectors (matrix query, konami code)"
```

---

### Task 4: Site-wide egg wiring (Konami + console; Matrix rain renderer)

**Files:**
- Create: `src/scripts/site-eggs.ts`
- Modify: `src/layouts/Base.astro` (load the script once, globally)

**Interfaces:**
- Consumes: `KonamiDetector` from `src/lib/eastereggs.ts`.
- Produces: global side effects — console art on load; Konami → `document.documentElement` gets `data-konami="1"` (drives an optional glitch) and dispatches a `CustomEvent('dr:konami')` on `window` (Task 8's game listens); a `startMatrixRain()` export used by search (Task 6).

- [ ] **Step 1: Implement `src/scripts/site-eggs.ts`**

```ts
import { KonamiDetector } from '../lib/eastereggs';

export function startMatrixRain(): void {
  if (matchMedia('(prefers-reduced-motion: reduce)').matches) return;
  if (document.getElementById('dr-matrix')) return;
  const c = document.createElement('canvas');
  c.id = 'dr-matrix';
  Object.assign(c.style, {
    position: 'fixed', inset: '0', zIndex: '9999', background: '#000', cursor: 'pointer',
  } as CSSStyleDeclaration);
  document.body.appendChild(c);
  const ctx = c.getContext('2d')!;
  let cols: number[] = [];
  const glyphs = 'アカサタナ01DRUNKROBOT'.split('');
  function resize() {
    c.width = innerWidth; c.height = innerHeight;
    cols = new Array(Math.ceil(c.width / 14)).fill(0);
  }
  resize();
  addEventListener('resize', resize);
  let raf = 0;
  function draw() {
    ctx.fillStyle = 'rgba(0,0,0,0.08)';
    ctx.fillRect(0, 0, c.width, c.height);
    ctx.fillStyle = '#39ff88';
    ctx.font = '14px monospace';
    cols.forEach((y, i) => {
      ctx.fillText(glyphs[(Math.random() * glyphs.length) | 0], i * 14, y * 14);
      cols[i] = y * 14 > c.height && Math.random() > 0.975 ? 0 : y + 1;
    });
    raf = requestAnimationFrame(draw);
  }
  draw();
  function stop() {
    cancelAnimationFrame(raf);
    removeEventListener('resize', resize);
    c.remove();
  }
  c.addEventListener('click', stop);
  addEventListener('keydown', stop, { once: true });
}

function konamiCelebration(): void {
  document.documentElement.dataset.konami = '1';
  window.dispatchEvent(new CustomEvent('dr:konami'));
  setTimeout(() => { delete document.documentElement.dataset.konami; }, 1200);
}

function initGlobalEggs(): void {
  // Console art
  console.log(
    '%c DRUNK ROBOT %c insert coin to continue ',
    'background:#39ff88;color:#040805;font-weight:bold',
    'color:#ffb000',
  );
  const konami = new KonamiDetector();
  addEventListener('keydown', (e) => {
    if (konami.push(e.key)) konamiCelebration();
  });
}

if (typeof window !== 'undefined') initGlobalEggs();
```

- [ ] **Step 2: Load it once, globally, in `Base.astro`**

Before `</body>` in `src/layouts/Base.astro` add:

```astro
<script>
  import '../scripts/site-eggs.ts';
</script>
```

- [ ] **Step 3: Verify build succeeds**

Run: `npm run build`
Expected: build passes; `grep -rn "dr:konami\|DRUNK ROBOT" dist/ | head -1` shows the bundled script emitted.

- [ ] **Step 4: Manual smoke (document in commit body, not blocking)**

Run `npm run dev`, open the site, type the Konami sequence, confirm the console art appears and no JS errors. (Matrix rain is verified in Task 6.)

- [ ] **Step 5: Commit**

```bash
git add src/scripts/site-eggs.ts src/layouts/Base.astro
git commit -m "feat: global easter eggs (konami event, console art, matrix rain renderer)"
```

---

### Task 5: Homepage — single-column cabinet/scene

**Files:**
- Replace: `src/pages/index.astro`

**Interfaces:**
- Consumes: `getCollection('comics')`, `sortByDate`/`getNav` from `src/lib/comicNav.ts`, `SITE_DESCRIPTION` from `src/lib/site.ts`, classes from Task 1. Renders a `<div id="stagger-mount">` placeholder that Task 8 wires up.

- [ ] **Step 1: Replace `src/pages/index.astro`**

Keep the existing frontmatter data derivation (comics, latest, nav, number, byYear) and the `WebSite`+`SearchAction` structuredData block. Replace the `<Base>...</Base>` body with:

```astro
<Base
  title={`Drunk Robot - ${latest.title}`}
  description={SITE_DESCRIPTION}
  image={`/comics/${latest.image}`}
  structuredData={/* keep existing WebSite + SearchAction object */}
>
  <div class="pix marquee" style="text-align:center;font-size:14px;color:var(--amber);padding:20px 0">DRUNK_ROBOT</div>

  <form class="terminal-input" action="/search/" method="get" role="search">
    <span class="prompt">grep&gt;</span>
    <input type="search" name="q" aria-label="Search the strips" placeholder="search the strips" />
    <span class="cursor" aria-hidden="true">_</span>
  </form>

  <p class="boot">booting attract_mode <span class="ok">[ OK ]</span> · {comics.length} strips loaded · rebooted</p>

  <section class="screen" aria-labelledby="hp-title">
    <span class="marquee">NOW PLAYING</span>
    <a href={`/comic/${latest.slug}/`}>
      <img class="strip" src={`/comics/${latest.image}`} alt={latest.altText} title={latest.hoverText} loading="eager" />
    </a>
  </section>

  <h1 id="hp-title"><span class="pix" style="color:var(--amber);font-size:0.7em">#{number}</span> {latest.title}</h1>
  <p style="color:var(--mute)">// posted {latest.date} · by Brian Powell &amp; Jeff Pina</p>

  <p>{latest.body}</p>

  <div class="authors">
    <div class="auth"><div class="k">Writer</div><div class="v glow">Brian Powell</div></div>
    <div class="auth"><div class="k">Artist</div><div class="v glow">Jeff Pina</div></div>
  </div>

  <details class="transcript" open>
    <summary>▸ TRANSCRIPT.txt</summary>
    <div class="tbody">{latest.transcript}</div>
  </details>

  <section class="card-panel" style="text-align:center" aria-label="Mini game">
    <div id="stagger-mount" data-strips={comics.length}>
      <button class="btn-arcade" id="stagger-start" type="button">► PRESS START</button>
      <p style="color:var(--mute);margin-top:10px">Drunk Stagger · 8-bit · dodge the street</p>
    </div>
  </section>

  <nav class="menu" aria-label="Site sections">
    <a class="menu-row" href="/archive/"><span><b>&gt; ARCHIVE</b> — all {comics.length} strips</span><span class="arw">▸</span></a>
    <a class="menu-row" href="/search/"><span><b>&gt; SEARCH</b> — grep the transcripts</span><span class="arw">▸</span></a>
    <a class="menu-row" href="/about/"><span><b>&gt; ABOUT</b> — who broke this robot</span><span class="arw">▸</span></a>
    <a class="menu-row" href="/rss.xml"><span><b>&gt; RSS</b> — subscribe</span><span class="arw">▸</span></a>
  </nav>
</Base>
```

- [ ] **Step 2: Verify build + content presence**

Run: `npm run build`
Then: `grep -o "TRANSCRIPT.txt\|stagger-mount\|NOW PLAYING\|Brian Powell" dist/index.html | sort -u`
Expected: all four strings present.

- [ ] **Step 3: Verify SEO plumbing intact**

Run: `grep -c "application/ld+json" dist/index.html`
Expected: `1` (the WebSite/SearchAction JSON-LD still emits).

- [ ] **Step 4: Commit**

```bash
git add src/pages/index.astro
git commit -m "feat: single-column phosphor homepage"
```

---

### Task 6: Search page — terminal UI + Matrix egg

**Files:**
- Modify: `src/pages/search.astro`

**Interfaces:**
- Consumes: Pagefind UI (already wired in v2), `isMatrixQuery` from `src/lib/eastereggs.ts`, `startMatrixRain` from `src/scripts/site-eggs.ts`.

- [ ] **Step 1: Reskin the search input** to use `.terminal-input` markup (as in Task 5), keeping the existing Pagefind mount element and its initialization untouched.

- [ ] **Step 2: Add the Matrix trigger** — in the page's client script, after reading the query:

```astro
<script>
  import { isMatrixQuery } from '../lib/eastereggs';
  import { startMatrixRain } from '../scripts/site-eggs';
  const input = document.querySelector<HTMLInputElement>('input[name="q"]');
  function check(v: string){ if (isMatrixQuery(v)) startMatrixRain(); }
  // On load (deep link ?q=neo) and on submit/typing:
  const params = new URLSearchParams(location.search);
  if (params.get('q')) check(params.get('q')!);
  input?.addEventListener('change', () => check(input.value));
</script>
```

- [ ] **Step 3: Verify build**

Run: `npm run build`
Expected: passes; Pagefind step still runs. `grep -c "pagefind" dist/search/index.html` ≥ 1.

- [ ] **Step 4: Manual smoke**

`npm run dev`, visit `/search/?q=neo` → Matrix rain appears; click/keypress dismisses it. Normal queries still search.

- [ ] **Step 5: Commit**

```bash
git add src/pages/search.astro
git commit -m "feat: terminal search UI with matrix easter egg"
```

---

### Task 7: Drunk Stagger — score module (TDD)

**Files:**
- Create: `src/lib/stagger-score.ts`
- Test: `src/lib/stagger-score.test.ts`

**Interfaces:**
- Produces:
  - `readHiScore(store: Pick<Storage,'getItem'>): number` — parses `dr-stagger-hi`, returns `0` if missing/invalid.
  - `commitScore(store: Pick<Storage,'getItem'|'setItem'>, score: number): number` — writes and returns the new hi-score iff `score` beats stored; returns the unchanged hi otherwise.

- [ ] **Step 1: Write the failing test** — `src/lib/stagger-score.test.ts`

```ts
import { describe, expect, it } from 'vitest';
import { readHiScore, commitScore } from './stagger-score';

function fakeStore(init: Record<string,string> = {}) {
  const m = new Map(Object.entries(init));
  return {
    getItem: (k: string) => m.get(k) ?? null,
    setItem: (k: string, v: string) => void m.set(k, v),
    _map: m,
  };
}

describe('stagger score', () => {
  it('reads 0 when absent or garbage', () => {
    expect(readHiScore(fakeStore())).toBe(0);
    expect(readHiScore(fakeStore({ 'dr-stagger-hi': 'x' }))).toBe(0);
  });
  it('reads a stored hi-score', () => {
    expect(readHiScore(fakeStore({ 'dr-stagger-hi': '420' }))).toBe(420);
  });
  it('commits only when beaten', () => {
    const s = fakeStore({ 'dr-stagger-hi': '100' });
    expect(commitScore(s, 90)).toBe(100);
    expect(commitScore(s, 250)).toBe(250);
    expect(s._map.get('dr-stagger-hi')).toBe('250');
  });
});
```

- [ ] **Step 2: Run test to verify it fails**

Run: `npx vitest run src/lib/stagger-score.test.ts`
Expected: FAIL ("readHiScore is not a function").

- [ ] **Step 3: Implement `src/lib/stagger-score.ts`**

```ts
const KEY = 'dr-stagger-hi';

export function readHiScore(store: Pick<Storage, 'getItem'>): number {
  const raw = store.getItem(KEY);
  const n = raw == null ? NaN : parseInt(raw, 10);
  return Number.isFinite(n) && n >= 0 ? n : 0;
}

export function commitScore(store: Pick<Storage, 'getItem' | 'setItem'>, score: number): number {
  const hi = readHiScore(store);
  if (score > hi) { store.setItem(KEY, String(score)); return score; }
  return hi;
}
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `npx vitest run src/lib/stagger-score.test.ts`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add src/lib/stagger-score.ts src/lib/stagger-score.test.ts
git commit -m "feat: drunk-stagger score persistence logic"
```

---

### Task 8: Drunk Stagger — canvas game + lazy homepage wiring

**Files:**
- Create: `src/scripts/drunk-stagger.js`
- Create: `src/scripts/stagger-boot.ts` (the tiny loader wired to `#stagger-start`)
- Modify: `src/pages/index.astro` (import the boot loader)

**Interfaces:**
- Consumes: `commitScore`, `readHiScore` from `src/lib/stagger-score.ts`; listens for `window` event `dr:konami` (Task 4) to grant the cheat.
- `drunk-stagger.js` default-exports `start(canvas: HTMLCanvasElement, opts?: {cheat?: boolean}): { destroy(): void }`.

- [ ] **Step 1: Implement `src/scripts/drunk-stagger.js`** (complete, dependency-free)

```js
// Minimal 8-bit dodge runner. Robot auto-runs; hop (space/tap) over/around
// obstacles; collect bolts for score. Endless, speeds up. No deps.
import { commitScore, readHiScore } from '../lib/stagger-score.ts';

export default function start(canvas, opts = {}) {
  const ctx = canvas.getContext('2d');
  const W = (canvas.width = 480), H = (canvas.height = 200), GROUND = H - 30;
  const reduce = matchMedia('(prefers-reduced-motion: reduce)').matches;
  let store; try { store = localStorage; } catch { store = { getItem: () => null, setItem() {} }; }

  const robot = { x: 60, y: GROUND, vy: 0, on: true };
  let obstacles = [], bolts = [], t = 0, speed = 3, score = 0, over = false;
  let lives = opts.cheat ? 99 : 1;
  const hi0 = readHiScore(store);

  function hop() { if (robot.on && !over) { robot.vy = -9; robot.on = false; } }
  function reset() { obstacles = []; bolts = []; t = 0; speed = 3; score = 0; over = false; lives = opts.cheat ? 99 : 1; }

  function spawn() {
    if (t % 70 === 0) obstacles.push({ x: W, w: 14, h: 22 + (Math.random() * 16 | 0) });
    if (t % 90 === 45) bolts.push({ x: W, y: GROUND - 40 - (Math.random() * 40 | 0), r: 7 });
  }
  function step() {
    t++; spawn(); speed += 0.002;
    robot.vy += 0.6; robot.y += robot.vy;
    if (robot.y >= GROUND) { robot.y = GROUND; robot.vy = 0; robot.on = true; }
    obstacles.forEach((o) => (o.x -= speed));
    bolts.forEach((b) => (b.x -= speed));
    obstacles = obstacles.filter((o) => o.x + o.w > 0);
    bolts = bolts.filter((b) => b.x + b.r > 0);
    // collisions
    for (const o of obstacles) {
      if (60 + 16 > o.x && 60 < o.x + o.w && robot.y > GROUND - o.h) {
        if (--lives <= 0) { over = true; commitScore(store, score); }
        else o.x = -99;
      }
    }
    for (const b of bolts) {
      const dx = 68 - b.x, dy = (robot.y - 8) - b.y;
      if (dx * dx + dy * dy < (b.r + 12) ** 2) { b.x = -99; score += 10; }
    }
    if (t % 6 === 0) score += 1;
  }
  function draw() {
    ctx.fillStyle = '#040805'; ctx.fillRect(0, 0, W, H);
    ctx.strokeStyle = '#173a22'; ctx.beginPath(); ctx.moveTo(0, GROUND + 16); ctx.lineTo(W, GROUND + 16); ctx.stroke();
    ctx.fillStyle = '#5c8a6c'; obstacles.forEach((o) => ctx.fillRect(o.x, GROUND - o.h + 16, o.w, o.h));
    ctx.fillStyle = '#ffb000'; bolts.forEach((b) => { ctx.beginPath(); ctx.arc(b.x, b.y, b.r, 0, 7); ctx.fill(); });
    ctx.fillStyle = '#39ff88'; ctx.fillRect(60, robot.y - 16, 16, 16);
    ctx.font = '12px monospace'; ctx.fillStyle = '#39ff88';
    ctx.fillText('SCORE ' + String(score).padStart(5, '0'), 8, 16);
    const hi = Math.max(hi0, score);
    ctx.fillStyle = '#ffb000'; ctx.fillText('HI ' + String(hi).padStart(5, '0'), W - 92, 16);
    if (over) { ctx.fillStyle = '#ffb000'; ctx.font = '16px monospace'; ctx.fillText('GAME OVER - press space', W / 2 - 110, H / 2); }
  }

  let raf = 0;
  function loop() { if (!over) step(); draw(); raf = requestAnimationFrame(loop); }

  function onKey(e) {
    if (e.code === 'Space' || e.key === ' ') { e.preventDefault(); over ? reset() : hop(); }
  }
  function onTap() { over ? reset() : hop(); }
  addEventListener('keydown', onKey);
  canvas.addEventListener('pointerdown', onTap);
  if (reduce) { draw(); ctx.fillStyle = '#39ff88'; ctx.font = '12px monospace'; ctx.fillText('tap to play', W / 2 - 30, H / 2 + 24); }
  else loop();

  return { destroy() { cancelAnimationFrame(raf); removeEventListener('keydown', onKey); canvas.removeEventListener('pointerdown', onTap); } };
}
```

- [ ] **Step 2: Implement lazy loader `src/scripts/stagger-boot.ts`**

```ts
const mount = document.getElementById('stagger-mount');
const startBtn = document.getElementById('stagger-start');
let cheat = false;
addEventListener('dr:konami', () => { cheat = true; });

async function boot() {
  if (!mount) return;
  const canvas = document.createElement('canvas');
  canvas.setAttribute('aria-label', 'Drunk Stagger mini-game');
  canvas.style.maxWidth = '100%';
  mount.replaceChildren(canvas);
  const { default: start } = await import('./drunk-stagger.js');
  start(canvas, { cheat });
}

startBtn?.addEventListener('click', boot, { once: true });
```

- [ ] **Step 3: Wire the loader into the homepage**

In `src/pages/index.astro`, before `</Base>` add:

```astro
<script>
  import '../scripts/stagger-boot.ts';
</script>
```

- [ ] **Step 4: Verify game code is NOT in first paint**

Run: `npm run build`
Then confirm `drunk-stagger` is a separate lazy chunk, not inlined into the homepage HTML:
`grep -c "requestAnimationFrame" dist/index.html`
Expected: `0` (the game body is in a dynamically-imported chunk under `dist/_astro/`, loaded only on click).

- [ ] **Step 5: Run the full test suite**

Run: `npm test`
Expected: PASS (comicNav, site, eastereggs, stagger-score).

- [ ] **Step 6: Manual smoke**

`npm run dev`: click PRESS START → game runs, space hops, collisions end the game, space restarts, HI persists across reloads. Enter Konami first → 99 lives.

- [ ] **Step 7: Commit**

```bash
git add src/scripts/drunk-stagger.js src/scripts/stagger-boot.ts src/pages/index.astro
git commit -m "feat: Drunk Stagger canvas mini-game with lazy load + konami cheat"
```

---

### Task 9: Reskin comic reader, archive, about, 404, terminal, mascot

**Files:**
- Modify: `src/components/ComicReader.astro`, `src/pages/comic/[slug].astro`, `src/pages/archive.astro`, `src/pages/about.astro`, `src/pages/404.astro`, `src/pages/terminal.astro`, `src/components/Mascot.astro`

**Interfaces:**
- Consumes: Task 1 classes only. No logic changes to `comicNav.ts`, Pagefind, or JSON-LD emitters.

- [ ] **Step 1: Comic reader** — wrap the strip in `.screen`, put the image in `.strip` with `alt={altText}` and `title={hoverText}`, render title/date, `.authors` boxes, `.transcript` details, and prev/next/random as `.btn-arcade`. Keep the existing `getNav` logic and JSON-LD.

- [ ] **Step 2: Archive** — render the year groups as a "HIGH SCORES" table styled with `.card-panel`/`.menu`; each strip links via `.menu-row`. Heading `<h1 class="pix">HIGH SCORES</h1>`.

- [ ] **Step 3: About** — reskin the FAQ into `.card-panel` blocks (copy already fixed in Task 2). Heading in `.pix`.

- [ ] **Step 4: 404** — reskin as a full "GAME OVER" screen using `.screen`, a `.btn-arcade` back to home. Keep it fun.

- [ ] **Step 5: /terminal/** — reskin to the phosphor terminal look; keep its existing easter-egg behavior.

- [ ] **Step 6: Mascot** — restyle the reactive mascot to phosphor colors; keep the boop reaction handler.

- [ ] **Step 7: Verify build across all routes**

Run: `npm run build`
Then: `for f in dist/index.html dist/about/index.html dist/archive/index.html dist/search/index.html dist/404.html dist/terminal/index.html; do echo "$f: $(grep -c 'crt-overlay' "$f")"; done`
Expected: each prints `1` (theme overlay present, i.e. the page rendered through the reskinned layout).

- [ ] **Step 8: Verify a comic page renders art + transcript**

Run: `f=$(ls dist/comic/*/index.html | head -1); grep -o 'class="strip"\|transcript' "$f" | sort -u`
Expected: both `class="strip"` and `transcript` present.

- [ ] **Step 9: Commit**

```bash
git add src/components src/pages
git commit -m "feat: reskin reader, archive, about, 404, terminal, mascot to Phosphor"
```

---

### Task 10: AdSense scaffolding (renders nothing until enabled)

**Files:**
- Create: `src/components/AdSlot.astro`
- Modify: `src/pages/index.astro` (two placements), `src/pages/comic/[slug].astro` (below strip)

**Interfaces:**
- Produces: `<AdSlot slot="home-below-strip" />` — renders an empty reserved box only when `import.meta.env.PUBLIC_ADSENSE_ENABLED === 'true'` AND `import.meta.env.PUBLIC_ADSENSE_CLIENT` is set; otherwise renders nothing.

- [ ] **Step 1: Implement `src/components/AdSlot.astro`**

```astro
---
interface Props { slot: string; }
const { slot } = Astro.props;
const enabled = import.meta.env.PUBLIC_ADSENSE_ENABLED === 'true';
const client = import.meta.env.PUBLIC_ADSENSE_CLIENT;
const show = enabled && !!client;
---
{show && (
  <aside class="card-panel" data-ad-slot={slot} style="min-height:90px;display:flex;align-items:center;justify-content:center;color:var(--mute)" aria-label="Advertisement">
    <ins class="adsbygoogle" style="display:block;width:100%" data-ad-client={client} data-ad-slot={slot} data-ad-format="auto" data-full-width-responsive="true"></ins>
  </aside>
)}
```

(No AdSense `<script>` ships until you later add it behind the same `show` flag. This task only reserves the component; nothing renders by default.)

- [ ] **Step 2: Place slots** — add `<AdSlot slot="home-below-strip" />` after the homepage strip section and `<AdSlot slot="home-above-footer" />` before the footer; add one below the strip in the comic reader.

- [ ] **Step 3: Verify nothing renders by default**

Run: `npm run build && grep -c "adsbygoogle" dist/index.html`
Expected: `0` (flag unset → empty output, no layout element).

- [ ] **Step 4: Commit**

```bash
git add src/components/AdSlot.astro src/pages/index.astro src/pages/comic/\[slug\].astro
git commit -m "feat: AdSense slot scaffolding (disabled by default)"
```

---

### Task 11: Final verification + docs

**Files:**
- Modify: `README.md`, `CHANGELOG.md` (per Global Constraints / repo convention)

- [ ] **Step 1: Full green build + tests**

Run: `npm test && npm run build`
Expected: all tests pass; build + Pagefind index succeed.

- [ ] **Step 2: Audit clean**

Run: `npm audit --omit=dev`
Expected: 0 advisories (matches v2.0.1 baseline).

- [ ] **Step 3: Reduced-motion + a11y spot check** (manual, `npm run dev`)
  - OS "reduce motion" on → no scanline animation, game shows static "tap to play", Matrix rain no-ops.
  - Tab through homepage → visible focus rings; strip has alt text; transcript reachable.

- [ ] **Step 4: Egg checklist** (manual)
  - `/search/?q=neo` → Matrix rain. Konami anywhere → console/glitch + game cheat. Console art on load. Mascot boop works.

- [ ] **Step 5: Verify no archive copy anywhere in output**

Run: `grep -rniE "wayback|internet archive|restored" dist/ || echo CLEAN`
Expected: `CLEAN`

- [ ] **Step 6: Update README.md + CHANGELOG.md**

Document the Phosphor theme, the mini-game, and the easter eggs. Do not bump the version or tag here — release is a separate, user-approved step per the repo's release conventions (show the version bump + changelog before tagging).

- [ ] **Step 7: Commit**

```bash
git add README.md CHANGELOG.md
git commit -m "docs: document Phosphor theme, mini-game, and easter eggs"
```

---

## Self-Review

**Spec coverage:**
- Art direction / tokens → Task 1. ✓
- Single-column homepage w/ all content blocks → Task 5. ✓
- Drunk Stagger (lazy, keyboard+touch, hi-score, reduced-motion) → Tasks 7–8. ✓
- Reskin reader/archive/search/about/404/terminal/mascot → Tasks 6, 9. ✓
- Easter eggs (Matrix, Konami, console, boop) → Tasks 3, 4, 6, 8, 9. ✓
- Remove Internet Archive copy → Task 2 (+ verified in 9, 11). ✓
- SEO/AEO preserved → Tasks 5 (JSON-LD check), 9 (untouched emitters). ✓
- AdSense scaffolding → Task 10. ✓
- Light/dark + reduced-motion → Task 1, verified Task 11. ✓
- Tests stay green / add game+egg unit tests → Tasks 2,3,7 add tests; 8,11 run full suite. ✓

**Placeholder scan:** No TBD/TODO. Reskin steps in Task 9 describe concrete class composition using Task 1 primitives (the CSS itself is fully specified in Task 1, so no per-page CSS is left unspecified). Astro markup verification is by content grep, not vague "test the above."

**Type consistency:** `readHiScore`/`commitScore` signatures match between Task 7 (def) and Task 8 (use). `KonamiDetector.push`/`isMatrixQuery` match between Task 3 (def) and Tasks 4/6 (use). `start(canvas, opts)` default export matches between Task 8 Step 1 (def) and Step 2 (use). `dr:konami` event name consistent across Tasks 4 and 8. `#stagger-mount`/`#stagger-start` ids consistent across Tasks 5 and 8.
