import type { APIRoute } from 'astro';
import { getCollection } from 'astro:content';
import { sortByDate } from '../lib/comicNav';
import { SITE_DESCRIPTION, SITE_NAME } from '../lib/site';

// llms.txt: a markdown index for AI crawlers and answer engines.
// https://llmstxt.org/
export const GET: APIRoute = async ({ site }) => {
  const entries = await getCollection('comics');
  const comics = sortByDate(entries.map((e) => e.data));
  const base = site!.toString().replace(/\/$/, '');

  const strips = comics
    .map((c) => `- [${c.title} (${c.date})](${base}/comic/${c.slug}/): ${c.hoverText}`)
    .join('\n');

  const body = `# ${SITE_NAME}

> ${SITE_DESCRIPTION}

Every strip page includes a full text transcript of the comic's dialogue
and action, plus alt text describing the art.

## Key pages

- [Latest strip](${base}/): the homepage always shows the newest comic
- [Archive](${base}/archive/): every recovered strip, grouped by year
- [About and FAQ](${base}/about/): what the comic is, who makes it, where to start
- [Search](${base}/search/): full-text search across strip transcripts
- [First strip](${base}/comic/${comics[0].slug}/): where to start reading
- [RSS feed](${base}/rss.xml)

## Strips

${strips}
`;

  return new Response(body, {
    headers: { 'Content-Type': 'text/plain; charset=utf-8' },
  });
};
