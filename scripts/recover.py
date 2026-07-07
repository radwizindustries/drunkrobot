"""Recover the Drunk Robot webcomic from the Wayback Machine.

Usage: python3 recover.py            (run from the scripts/ directory)
Writes ../src/data/comics.json, ../public/comics/*, ../recovery-report.md.
Python 3 stdlib only. See docs/superpowers/specs/2026-07-06-drunk-robot-relaunch-design.md.
"""

import html as html_mod
import json
import re
import time
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime
from pathlib import Path

SITE = "drunk-robot.com"
CDX_API = "https://web.archive.org/cdx/search/cdx"
USER_AGENT = "drunk-robot-recovery/1.0 (site owner restoring own content)"
CUTOFF = "20170101000000"  # site died ~2017; later captures are domain parking

SCRIPT_DIR = Path(__file__).parent
CACHE_DIR = SCRIPT_DIR / ".cache"
REPO_ROOT = SCRIPT_DIR.parent

# top-level path segments that are never comic posts
NON_POST_SEGMENTS = {
    "category", "author", "tag", "page", "feed", "comments",
    "wp-content", "wp-includes", "wp-admin", "comics", "comics-mini", "img",
}
# Extensions that never get a trailing slash in normalize_url. Note: classify()
# deliberately treats only image extensions as "asset" (downloadable media);
# .css/.js/etc. fall through to "other" since the crawler never fetches them.
ASSET_EXTENSIONS = (".jpg", ".jpeg", ".gif", ".png", ".css", ".js", ".ico",
                    ".xml", ".txt", ".php")

THROTTLE_SECONDS = 2.5
FETCH_RETRIES = 5
_last_request = 0.0


def _throttle():
    global _last_request
    wait = _last_request + THROTTLE_SECONDS - time.monotonic()
    if wait > 0:
        time.sleep(wait)
    _last_request = time.monotonic()


def fetch(url: str) -> bytes:
    """GET with a throttled request rate, retries with backoff, 30s timeout.

    archive.org intermittently refuses connections under sustained request
    volume (observed empirically during recovery: isolated test bursts of
    5-10 requests always succeed, but a full ~150-250 request crawl trips
    something -- likely a rate limiter -- that returns ECONNREFUSED rather
    than an HTTP 429). More retries with longer backoff give that window a
    chance to clear rather than abandoning an otherwise-recoverable page.
    """
    last_error = None
    for attempt in range(FETCH_RETRIES):
        _throttle()
        try:
            req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
            with urllib.request.urlopen(req, timeout=30) as resp:
                return resp.read()
        except (urllib.error.URLError, urllib.error.HTTPError, TimeoutError) as e:
            last_error = e
            time.sleep(min(2 ** (attempt + 1), 30))
    raise last_error


def fetch_cached(url: str) -> bytes:
    """fetch() with a local disk cache so re-runs are cheap."""
    CACHE_DIR.mkdir(exist_ok=True)
    key = re.sub(r"[^A-Za-z0-9._-]", "_", url)[-180:]
    cached = CACHE_DIR / key
    if cached.exists():
        return cached.read_bytes()
    data = fetch(url)
    cached.write_bytes(data)
    return data


def cdx_rows(url_pattern: str) -> list:
    """Query the CDX API, return data rows (header stripped)."""
    query = urllib.parse.urlencode({"url": url_pattern, "output": "json"})
    data = json.loads(fetch_cached(f"{CDX_API}?{query}").decode("utf-8"))
    return data[1:] if data else []


def normalize_url(original: str) -> str:
    """Reduce an archived original URL to a canonical site path."""
    parsed = urllib.parse.urlparse(original)
    path = parsed.path or "/"
    if parsed.query:
        p_match = re.match(r"^p=(\d+)$", parsed.query)
        if p_match:
            return f"/?p={p_match.group(1)}"
        # any other query string is dropped
    path = urllib.parse.unquote(path)
    if not path.endswith("/") and not path.lower().endswith(ASSET_EXTENSIONS):
        path += "/"
    return path


def classify(path: str) -> str:
    if re.match(r"^/\?p=\d+$", path):
        return "p-id"
    if path == "/":
        return "other"
    if path.lower().endswith((".jpg", ".jpeg", ".gif", ".png", ".ico")):
        return "asset"
    segments = [s for s in path.strip("/").split("/") if s]
    if not segments:
        return "other"
    if segments[-1] == "feed":
        return "feed"
    if segments[0] in ("category", "author"):
        return "listing"
    if segments[0] in NON_POST_SEGMENTS or "." in segments[0]:
        return "other"
    if (len(segments) == 4 and re.match(r"^\d{4}$", segments[0])
            and re.match(r"^\d{2}$", segments[1]) and re.match(r"^\d{2}$", segments[2])):
        return "post-dated"
    if len(segments) == 1 and re.match(r"^[a-z0-9-]+$", segments[0]):
        return "post-slug"
    return "other"


def best_snapshot(rows: list) -> str | None:
    """Pick the best capture timestamp: latest 200 before CUTOFF, else latest 200."""
    ok = sorted(r[1] for r in rows if r[4] == "200")
    if not ok:
        return None
    pre_cutoff = [ts for ts in ok if ts < CUTOFF]
    return (pre_cutoff or ok)[-1]


MONTHS = {m: i for i, m in enumerate(
    ["January", "February", "March", "April", "May", "June", "July",
     "August", "September", "October", "November", "December"], start=1)}


def _parse_display_date(text: str) -> str | None:
    """'May 23, 2011' -> '2011-05-23'."""
    m = re.match(r"^(\w+) (\d{1,2}), (\d{4})$", text.strip())
    if not m or m.group(1) not in MONTHS:
        return None
    return f"{int(m.group(3)):04d}-{MONTHS[m.group(1)]:02d}-{int(m.group(2)):02d}"


def parse_post(html_text: str) -> dict:
    """Extract comic data from a ComicPress post page (id_ raw HTML)."""
    result = {"title": None, "date": None, "image_urls": [],
              "body": "", "nav_paths": [], "shortlink_id": None}

    m = re.search(r'<h2 class="post-title"><a [^>]*>(.*?)</a></h2>', html_text, re.S)
    if m:
        result["title"] = html_mod.unescape(m.group(1)).strip()

    m = re.search(r'<span class="post-date">(.*?)</span>', html_text, re.S)
    if m:
        result["date"] = _parse_display_date(html_mod.unescape(m.group(1)))

    comic_zone = html_text
    m = re.search(r'<div id="comic">(.*?)<div id="comic-foot', html_text, re.S)
    if m:
        comic_zone = m.group(1)
    result["image_urls"] = re.findall(
        r'<img src="(https?://(?:www\.)?drunk-robot\.com/comics/[^"]+)"', comic_zone)

    result["nav_paths"] = [
        normalize_url(href) for href in
        re.findall(r'<a href="([^"]+)" class="navi[^"]*"', html_text)
    ]

    m = re.search(r"<link rel=['\"]shortlink['\"] href=['\"][^'\"]*\?p=(\d+)['\"]", html_text)
    if m:
        result["shortlink_id"] = int(m.group(1))

    m = re.search(r'<div class="entry">(.*?)<div class="post-foot', html_text, re.S)
    if m:
        body = m.group(1)
        body = re.sub(r"<!-- Facebook Comments.*$", "", body, flags=re.S)
        body = re.sub(r'<div class="fb-comments".*$', "", body, flags=re.S)
        body = re.sub(r"<script\b.*?</script>", "", body, flags=re.S)
        body = re.sub(r"<p>(&nbsp;|\s)*</p>", "", body)
        # drop dangling close-tags left by the fb-comments cut
        body = re.sub(r"(</div>\s*)+$", "", body.strip())
        result["body"] = body.strip()

    return result


def parse_comment_feed(xml_text: str) -> dict:
    """A per-post comment feed names its post: 'Comments on: TITLE' + <link>."""
    result = {"title": None, "path": None}
    m = re.search(r"<title>Comments on: (.*?)</title>", xml_text, re.S)
    if m:
        result["title"] = html_mod.unescape(m.group(1)).strip()
    m = re.search(r"<link>(https?://[^<]+)</link>", xml_text)
    if m:
        result["path"] = normalize_url(m.group(1))
    return result


def parse_site_feed(xml_text: str) -> list:
    """The site RSS feed carries full posts: title, link, pubDate, content."""
    items = []
    for chunk in re.findall(r"<item>(.*?)</item>", xml_text, re.S):
        title = re.search(r"<title>(.*?)</title>", chunk, re.S)
        link = re.search(r"<link>(https?://[^<]+)</link>", chunk)
        pub = re.search(r"<pubDate>(.*?)</pubDate>", chunk)
        content = re.search(r"<content:encoded><!\[CDATA\[(.*?)\]\]></content:encoded>", chunk, re.S)
        date = None
        if pub:
            try:
                date = datetime.strptime(
                    pub.group(1).strip(), "%a, %d %b %Y %H:%M:%S %z").strftime("%Y-%m-%d")
            except ValueError:
                pass
        items.append({
            "title": html_mod.unescape(title.group(1)).strip() if title else None,
            "path": normalize_url(link.group(1)) if link else None,
            "date": date,
            "body": content.group(1).strip() if content else "",
        })
    return items


def crawl(seed_paths: set, snapshots: dict, fetch_page) -> tuple:
    """BFS from seed post paths, following navi links to undiscovered posts.

    snapshots: {path: cdx_rows}. fetch_page(path, ts) -> parsed post dict.
    Returns ({path: parsed}, [skipped_paths]).
    """
    queue = sorted(seed_paths)
    seen, results, skipped = set(queue), {}, []
    while queue:
        path = queue.pop(0)
        ts = best_snapshot(snapshots.get(path, []))
        if ts is None:
            skipped.append(path)
            continue
        try:
            parsed = fetch_page(path, ts)
        except Exception as e:
            print(f"  fetch failed, skipping {path}: {e}")
            skipped.append(path)
            continue
        results[path] = parsed
        for nav_path in parsed.get("nav_paths", []):
            if nav_path not in seen and classify(nav_path) in ("post-slug", "post-dated"):
                seen.add(nav_path)
                queue.append(nav_path)
    return results, skipped


def _slug_of(path: str) -> str:
    return path.strip("/").split("/")[-1].lower()


def build_records(pages: dict, feed_items: list) -> tuple:
    """Merge crawled pages and feed items into comic records + problem list."""
    by_slug, problems = {}, []

    def offer(slug, title, date, image_url, body, source):
        if not (title and date and image_url):
            return False
        image = urllib.parse.unquote(image_url.rsplit("/", 1)[-1])
        existing = by_slug.get(slug)
        record = {"slug": slug, "title": title, "date": date,
                  "image": image, "body": body or "", "source": source}
        # prefer records with a body; then prefer the later source (slug era)
        if existing is None or (not existing["body"] and body):
            by_slug[slug] = record
        return True

    for path, parsed in sorted(pages.items()):
        if parsed is None:
            continue
        images = parsed.get("image_urls", [])
        if len(images) > 1:
            problems.append({"path": path, "reason": "multiple comic images",
                             "details": f"using first of {len(images)}: {images}"})
        ok = offer(_slug_of(path), parsed.get("title"), parsed.get("date"),
                   images[0] if images else None, parsed.get("body"),
                   f"https://web.archive.org/web/*/{SITE}{path}")
        if not ok:
            problems.append({"path": path, "reason": "incomplete extraction",
                             "details": f"title={parsed.get('title')!r} date={parsed.get('date')!r} "
                                        f"images={len(images)}"})

    for item in feed_items:
        if not item.get("path"):
            continue
        slug = _slug_of(item["path"])
        if slug in by_slug:
            continue
        imgs = re.findall(r'<img src="(https?://(?:www\.)?drunk-robot\.com/comics/[^"]+)"',
                          item.get("body") or "")
        ok = offer(slug, item.get("title"), item.get("date"),
                   imgs[0] if imgs else None, "",
                   f"https://web.archive.org/web/*/{SITE}/feed/")
        if not ok:
            problems.append({"path": item["path"], "reason": "feed item incomplete",
                             "details": f"title={item.get('title')!r} date={item.get('date')!r}"})

    records = sorted(by_slug.values(), key=lambda r: (r["date"], r["slug"]))
    return records, problems


def download_image(image_url: str, dest_dir: Path) -> bool:
    """Download the largest 200 capture of an image. Returns success."""
    basename = urllib.parse.unquote(image_url.rsplit("/", 1)[-1])
    dest = dest_dir / basename
    if dest.exists():
        return True
    rows = cdx_rows(image_url)
    ok = [r for r in rows if r[4] == "200"]
    if not ok:
        return False
    best = max(ok, key=lambda r: int(r[6]))
    data = fetch(f"https://web.archive.org/web/{best[1]}im_/{image_url}")
    dest_dir.mkdir(parents=True, exist_ok=True)
    dest.write_bytes(data)
    return True


def main():
    print("Pass 1: CDX discovery")
    rows = cdx_rows(f"{SITE}*")
    snapshots = {}
    for row in rows:
        path = normalize_url(row[2])
        snapshots.setdefault(path, []).append(row)

    seeds, p_ids, feed_paths, listing_paths = set(), [], [], []
    for path in snapshots:
        kind = classify(path)
        if kind in ("post-slug", "post-dated"):
            seeds.add(path)
        elif kind == "p-id":
            p_ids.append(path)
        elif kind == "feed":
            feed_paths.append(path)
        elif kind == "listing":
            listing_paths.append(path)
    print(f"  {len(seeds)} seed posts, {len(p_ids)} ?p= ids, "
          f"{len(feed_paths)} feeds, {len(listing_paths)} listing pages")

    print("Pass 1b: resolve ?p= ids via wayback redirects")
    for path in p_ids:
        rows_p = snapshots.get(path, [])
        ts = best_snapshot(rows_p)  # ?p= captures are usually 301s, so fall back
        if ts is None:
            all_ts = sorted(r[1] for r in rows_p)
            ts = all_ts[-1] if all_ts else None
        if not ts:
            continue
        try:
            req = urllib.request.Request(
                f"https://web.archive.org/web/{ts}/http://{SITE}{path}",
                headers={"User-Agent": USER_AGENT})
            _throttle()
            with urllib.request.urlopen(req, timeout=30) as resp:
                final = resp.geturl()
            m = re.search(r"/web/\d+/https?://(?:www\.)?" + re.escape(SITE) + r"(/.*)$", final)
            if m:
                resolved = normalize_url("http://" + SITE + m.group(1))
                if classify(resolved) in ("post-slug", "post-dated"):
                    seeds.add(resolved)
                    print(f"  {path} -> {resolved}")
        except Exception as e:
            print(f"  {path}: unresolved ({e})")

    print("Pass 1c: mine listing pages for post links")
    for path in listing_paths:
        ts = best_snapshot(snapshots.get(path, []))
        if not ts:
            continue
        try:
            html_text = fetch_cached(
                f"https://web.archive.org/web/{ts}id_/http://{SITE}{path}").decode("utf-8", "replace")
        except Exception as e:
            print(f"  listing page fetch failed, skipping {path}: {e}")
            continue
        for href in re.findall(
                r'<a href="(https?://(?:www\.)?' + re.escape(SITE) + r'/[^"]*)"', html_text):
            p = normalize_url(href)
            if classify(p) in ("post-slug", "post-dated"):
                seeds.add(p)

    print(f"Pass 2: crawl {len(seeds)} candidate posts")

    def fetch_page(path, ts):
        raw = fetch_cached(
            f"https://web.archive.org/web/{ts}id_/http://{SITE}{path}").decode("utf-8", "replace")
        return parse_post(raw)

    pages, skipped = crawl(seeds, snapshots, fetch_page)

    print("Pass 2b: parse feeds for gap-filling")
    feed_items = []
    for path in feed_paths:
        ts = best_snapshot(snapshots.get(path, []))
        if not ts:
            continue
        try:
            xml_text = fetch_cached(
                f"https://web.archive.org/web/{ts}id_/http://{SITE}{path}").decode("utf-8", "replace")
        except Exception as e:
            print(f"  feed fetch failed, skipping {path}: {e}")
            continue
        if "<item>" in xml_text:
            feed_items.extend(parse_site_feed(xml_text))
        else:
            info = parse_comment_feed(xml_text)
            if info["path"] and info["title"]:
                feed_items.append({"title": info["title"], "path": info["path"],
                                   "date": None, "body": ""})

    print("Pass 3: build records")
    records, problems = build_records(pages, feed_items)

    print(f"Pass 3b: download {len(records)} images")
    img_dir = REPO_ROOT / "public" / "comics"
    kept = []
    for rec in records:
        url = f"http://{SITE}/comics/" + urllib.parse.quote(rec["image"])
        try:
            ok = download_image(url, img_dir)
        except Exception as e:
            print(f"  image fetch failed for {rec['slug']}: {e}")
            ok = False
        if ok:
            kept.append(rec)
        else:
            problems.append({"path": f"/comics/{rec['image']}",
                             "reason": "image unrecoverable",
                             "details": f"no usable capture for {rec['slug']}"})

    print("Pass 4: write outputs")
    out = REPO_ROOT / "src" / "data" / "comics.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(kept, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    report = ["# Drunk Robot Recovery Report", "",
              f"- Recovered comics: **{len(kept)}**",
              f"- Skipped (no usable snapshot): **{len(skipped)}**",
              f"- Problems for review: **{len(problems)}**", "",
              "## Recovered", "", "| Date | Slug | Title | Image |", "|---|---|---|---|"]
    for r in kept:
        report.append(f"| {r['date']} | {r['slug']} | {r['title']} | {r['image']} |")
    report += ["", "## Skipped paths", ""]
    report += [f"- `{p}`" for p in skipped] or ["- none"]
    report += ["", "## Problems", ""]
    report += [f"- `{p['path']}`: {p['reason']} ({p['details']})" for p in problems] or ["- none"]
    (REPO_ROOT / "recovery-report.md").write_text("\n".join(report) + "\n", encoding="utf-8")
    print(f"Done: {len(kept)} comics -> {out}")


if __name__ == "__main__":
    main()
