# Drunk Robot

Archive of the Drunk Robot webcomic (2011-2016), recovered from the Wayback
Machine and rebuilt with Astro. Live at https://drunk-robot.com.

## Develop

    npm install
    npm run dev

## Test and build

    npm test
    npm run build

## Recovery

Comics were recovered by `scripts/recover.py` (Python 3, stdlib only), which
crawls Wayback Machine captures of the original WordPress/ComicPress site and
emits `src/data/comics.json`, `public/comics/`, and `recovery-report.md`.
Re-running it is safe: fetches are cached in `scripts/.cache/`.

## Deploy

Pushes to `main` build and deploy to Hostinger over FTPS via GitHub Actions
(`.github/workflows/deploy.yml`). Secrets: `HOSTINGER_FTP_HOST`,
`HOSTINGER_FTP_USER`, `HOSTINGER_FTP_PASSWORD`.
