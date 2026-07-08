import { describe, expect, it } from 'vitest';
import { getNav, sortByDate, type Comic } from './comicNav';

function comic(slug: string, date: string): Comic {
  return {
    slug,
    title: slug.toUpperCase(),
    date,
    image: `${date}.jpg`,
    body: '',
    source: 'x',
    transcript: 'panel 1',
    altText: 'alt',
    hoverText: 'hover',
  };
}

const unsorted = [comic('c', '2011-05-30'), comic('a', '2011-05-23'), comic('b', '2011-05-26')];

describe('sortByDate', () => {
  it('sorts ascending by date', () => {
    expect(sortByDate(unsorted).map((c) => c.slug)).toEqual(['a', 'b', 'c']);
  });

  it('tiebreaks equal dates by slug', () => {
    const twins = [comic('z', '2012-01-01'), comic('m', '2012-01-01')];
    expect(sortByDate(twins).map((c) => c.slug)).toEqual(['m', 'z']);
  });

  it('does not mutate the input', () => {
    const copy = [...unsorted];
    sortByDate(unsorted);
    expect(unsorted).toEqual(copy);
  });
});

describe('getNav', () => {
  it('middle comic has all four neighbors', () => {
    const nav = getNav(unsorted, 'b');
    expect(nav.first.slug).toBe('a');
    expect(nav.prev?.slug).toBe('a');
    expect(nav.next?.slug).toBe('c');
    expect(nav.last.slug).toBe('c');
    expect(nav.index).toBe(1);
    expect(nav.total).toBe(3);
  });

  it('first comic has null prev', () => {
    const nav = getNav(unsorted, 'a');
    expect(nav.prev).toBeNull();
    expect(nav.next?.slug).toBe('b');
  });

  it('last comic has null next', () => {
    const nav = getNav(unsorted, 'c');
    expect(nav.next).toBeNull();
    expect(nav.prev?.slug).toBe('b');
  });

  it('throws on unknown slug', () => {
    expect(() => getNav(unsorted, 'nope')).toThrow(/unknown comic/i);
  });
});
