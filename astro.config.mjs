import { readFileSync } from 'node:fs';
import { defineConfig } from 'astro/config';
import sitemap from '@astrojs/sitemap';

const comics = JSON.parse(readFileSync('./src/data/comics.json', 'utf8'));
const redirects = {};
const redirectPaths = new Set();
for (const c of comics) {
  redirects[`/${c.slug}`] = `/comic/${c.slug}/`;
  redirectPaths.add(`/${c.slug}/`);
  const [y, m, d] = c.date.split('-');
  redirects[`/${y}/${m}/${d}/${c.slug}`] = `/comic/${c.slug}/`;
  redirectPaths.add(`/${y}/${m}/${d}/${c.slug}/`);
}
const comicBySlug = new Map(comics.map((c) => [c.slug, c]));
const latestComicDate = comics.map((c) => c.date).sort().at(-1);

export default defineConfig({
  site: 'https://drunk-robot.com',
  redirects,
  integrations: [
    sitemap({
      // Exclude the legacy-URL redirect stubs: they 200 with a meta-refresh
      // (Astro's static-redirect mechanism) rather than a real 3xx, so
      // without this filter the sitemap would list each comic twice (once
      // at its real /comic/<slug>/ URL, once at the old WordPress-era URL).
      filter: (page) => !redirectPaths.has(new URL(page).pathname),
      // lastmod uses each comic's real publish date, not a synthetic
      // build-time stamp -- the archive is frozen (recovery is done, no new
      // comics), so a comic's lastmod should stay stable across rebuilds
      // instead of changing every time we redeploy for unrelated reasons.
      serialize(item) {
        const path = new URL(item.url).pathname;
        if (path === '/') {
          return { ...item, lastmod: latestComicDate, changefreq: 'monthly', priority: 1.0 };
        }
        if (path === '/archive/') {
          return { ...item, lastmod: latestComicDate, changefreq: 'monthly', priority: 0.8 };
        }
        if (path === '/about/') {
          return { ...item, changefreq: 'yearly', priority: 0.5 };
        }
        const comicMatch = path.match(/^\/comic\/([^/]+)\/$/);
        const comic = comicMatch && comicBySlug.get(comicMatch[1]);
        if (comic) {
          return { ...item, lastmod: comic.date, changefreq: 'yearly', priority: 0.6 };
        }
        return item;
      },
    }),
  ],
});
