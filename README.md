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

The site runs on a Hostinger VPS behind Traefik, alongside several other
sites, each served from its own `nginx:alpine` container. Pushes to `main`
build the site and deploy it via `rsync` over SSH to that VPS through GitHub
Actions (`.github/workflows/deploy.yml`), landing in
`/opt/drunk-robot-site/dist/`, which the container serves. The
docker-compose/nginx.conf that define the container and Traefik routing live
in `deploy/` for reference; they're already provisioned on the VPS and are
not touched by the deploy workflow.

Secrets: `HOSTINGER_SSH_HOST`, `HOSTINGER_SSH_USER`, `HOSTINGER_SSH_KEY`
(private key, PEM format).
