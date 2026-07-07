export interface Comic {
  slug: string;
  title: string;
  date: string;
  image: string;
  body: string;
  source: string;
}

export function sortByDate(comics: Comic[]): Comic[] {
  return [...comics].sort(
    (a, b) => a.date.localeCompare(b.date) || a.slug.localeCompare(b.slug),
  );
}

export interface ComicNav {
  first: Comic;
  prev: Comic | null;
  next: Comic | null;
  last: Comic;
  index: number;
  total: number;
}

export function getNav(comics: Comic[], slug: string): ComicNav {
  const sorted = sortByDate(comics);
  const index = sorted.findIndex((c) => c.slug === slug);
  if (index === -1) throw new Error(`unknown comic slug: ${slug}`);
  return {
    first: sorted[0],
    prev: index > 0 ? sorted[index - 1] : null,
    next: index < sorted.length - 1 ? sorted[index + 1] : null,
    last: sorted[sorted.length - 1],
    index,
    total: sorted.length,
  };
}
