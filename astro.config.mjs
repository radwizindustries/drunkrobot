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
    }),
  ],
});
