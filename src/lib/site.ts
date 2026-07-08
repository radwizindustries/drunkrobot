/**
 * Canonical entity signals. Every surface that names the series (pages,
 * JSON-LD, llms.txt, RSS) must pull from here so search and answer engines
 * see one consistent entity.
 */
export const SITE_NAME = 'Drunk Robot';

export const SITE_DESCRIPTION =
  'Drunk Robot is a webcomic written by Brian Powell and drawn by Jeff Pina. ' +
  'It ran weekly from 2011 to 2016, was restored from the Internet Archive, ' +
  'and is publishing again, skewering comics, sci-fi, and nerd culture.';

export const AUTHORS = [
  { name: 'Brian Powell', role: 'writer' },
  { name: 'Jeff Pina', role: 'artist' },
] as const;

/** schema.org Person objects for the creators. */
export const AUTHOR_SCHEMA = AUTHORS.map((a) => ({
  '@type': 'Person',
  name: a.name,
}));

/** schema.org ComicSeries node, embeddable via isPartOf. */
export function comicSeriesSchema(site: URL | undefined) {
  return {
    '@type': 'ComicSeries',
    name: SITE_NAME,
    url: new URL('/', site).toString(),
    description: SITE_DESCRIPTION,
    startDate: '2011',
    author: AUTHOR_SCHEMA,
  };
}
