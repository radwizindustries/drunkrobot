import type { APIRoute } from 'astro';
import { readFileSync } from 'node:fs';

interface Comic {
  slug: string;
  title: string;
  date: string;
  image: string;
  body: string;
  source: string;
}

// A single flat sitemap.xml, not the sitemap-index.xml + sitemap-N.xml
// split that @astrojs/sitemap always generates -- that split exists for
// sites needing to shard past the 50,000-URL-per-file limit, which this
// 10-URL archive will never approach.
export const GET: APIRoute = ({ site }) => {
  const comics: Comic[] = JSON.parse(readFileSync('./src/data/comics.json', 'utf8'));
  const siteURL = site!.toString().replace(/\/$/, '');
  const latestComicDate = comics.map((c) => c.date).sort().at(-1);

  const entries: { loc: string; lastmod?: string; changefreq: string; priority: string }[] = [
    { loc: '/', lastmod: latestComicDate, changefreq: 'monthly', priority: '1.0' },
    { loc: '/archive/', lastmod: latestComicDate, changefreq: 'monthly', priority: '0.8' },
    { loc: '/about/', changefreq: 'yearly', priority: '0.5' },
    ...comics.map((c) => ({
      loc: `/comic/${c.slug}/`,
      lastmod: c.date,
      changefreq: 'yearly',
      priority: '0.6',
    })),
  ];

  const urls = entries
    .map(
      (e) => `  <url>
    <loc>${siteURL}${e.loc}</loc>
${e.lastmod ? `    <lastmod>${e.lastmod}</lastmod>\n` : ''}    <changefreq>${e.changefreq}</changefreq>
    <priority>${e.priority}</priority>
  </url>`,
    )
    .join('\n');

  const xml = `<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
${urls}
</urlset>
`;

  return new Response(xml, {
    headers: { 'Content-Type': 'application/xml; charset=utf-8' },
  });
};
