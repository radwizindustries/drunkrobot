import { defineCollection, z } from 'astro:content';
import { file } from 'astro/loaders';

const comics = defineCollection({
  loader: file('src/data/comics.json', {
    parser: (text) =>
      JSON.parse(text).map((c: { slug: string }) => ({ id: c.slug, ...c })),
  }),
  schema: z.object({
    slug: z.string().min(1),
    title: z.string().min(1),
    date: z.string().regex(/^\d{4}-\d{2}-\d{2}$/),
    image: z.string().min(1),
    body: z.string(),
    source: z.string().url(),
    // Full dialogue/action text. Powers search, SEO, AEO, and accessibility;
    // required for every strip, past and future.
    transcript: z.string().min(1),
    // Describes the image for screen readers. altText describes, hoverText jokes.
    altText: z.string().min(1),
    // The second punchline, xkcd-style, shown on hover/long-press.
    hoverText: z.string().min(1),
    tags: z.array(z.string()).default([]),
    characters: z.array(z.string()).default([]),
  }),
});

export const collections = { comics };
