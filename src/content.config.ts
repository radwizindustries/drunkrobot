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
  }),
});

export const collections = { comics };
