"""Recover the Drunk Robot webcomic from the Wayback Machine.

Usage: python3 recover.py            (run from the scripts/ directory)
Writes ../src/data/comics.json, ../public/comics/*, ../recovery-report.md.
Python 3 stdlib only. See docs/superpowers/specs/2026-07-06-drunk-robot-relaunch-design.md.
"""

import json
import re
import time
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

SITE = "drunk-robot.com"
CDX_API = "http://web.archive.org/cdx/search/cdx"
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

_last_request = 0.0


def _throttle():
    global _last_request
    wait = _last_request + 1.0 - time.monotonic()
    if wait > 0:
        time.sleep(wait)
    _last_request = time.monotonic()


def fetch(url: str) -> bytes:
    """GET with 1 req/s throttle, 3 retries with backoff, 30s timeout."""
    last_error = None
    for attempt in range(3):
        _throttle()
        try:
            req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
            with urllib.request.urlopen(req, timeout=30) as resp:
                return resp.read()
        except (urllib.error.URLError, urllib.error.HTTPError, TimeoutError) as e:
            last_error = e
            time.sleep(2 ** (attempt + 1))
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


if __name__ == "__main__":
    print("Run via main() added in Task 3.")
