import { describe, expect, it } from 'vitest';
import { SITE_DESCRIPTION } from './site';

describe('SITE_DESCRIPTION', () => {
  it('names both creators and the run years', () => {
    expect(SITE_DESCRIPTION).toMatch(/Brian Powell/);
    expect(SITE_DESCRIPTION).toMatch(/Jeff Pina/);
    expect(SITE_DESCRIPTION).toMatch(/2011/);
    expect(SITE_DESCRIPTION).toMatch(/2016/);
  });
  it('has no Internet Archive / Wayback / restored copy', () => {
    expect(SITE_DESCRIPTION).not.toMatch(/internet archive|wayback|restored/i);
  });
});
