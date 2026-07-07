import { readFileSync } from 'node:fs';
import { defineConfig } from 'astro/config';

const comics = JSON.parse(readFileSync('./src/data/comics.json', 'utf8'));
const redirects = {};
for (const c of comics) {
  redirects[`/${c.slug}`] = `/comic/${c.slug}/`;
  const [y, m, d] = c.date.split('-');
  redirects[`/${y}/${m}/${d}/${c.slug}`] = `/comic/${c.slug}/`;
}

export default defineConfig({
  site: 'https://drunk-robot.com',
  redirects,
});
