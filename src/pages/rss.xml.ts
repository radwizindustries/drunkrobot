import rss from '@astrojs/rss';
import type { APIRoute } from 'astro';
import { getCollection } from 'astro:content';
import { sortByDate } from '../lib/comicNav';
import { SITE_DESCRIPTION, SITE_NAME } from '../lib/site';

// Full-content feed: the strip image and hover text ride along in the item
// body so feed readers get the whole experience without a click.
export const GET: APIRoute = async (context) => {
  const entries = await getCollection('comics');
  const comics = sortByDate(entries.map((e) => e.data)).reverse(); // newest first

  return rss({
    title: SITE_NAME,
    description: SITE_DESCRIPTION,
    site: context.site!,
    trailingSlash: true,
    customData: '<language>en-us</language>',
    items: comics.map((c) => {
      const imageURL = new URL(`/comics/${c.image}`, context.site).toString();
      return {
        title: c.title,
        link: `/comic/${c.slug}/`,
        pubDate: new Date(c.date + 'T00:00:00Z'),
        description: c.altText,
        content:
          `<p><img src="${imageURL}" alt="${c.altText.replace(/"/g, '&quot;')}" /></p>` +
          `<p><em>${c.hoverText}</em></p>`,
      };
    }),
  });
};
