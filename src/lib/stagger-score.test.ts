import { describe, expect, it } from 'vitest';
import { readHiScore, commitScore } from './stagger-score';

function fakeStore(init: Record<string, string> = {}) {
  const m = new Map(Object.entries(init));
  return {
    getItem: (k: string) => m.get(k) ?? null,
    setItem: (k: string, v: string) => void m.set(k, v),
    _map: m,
  };
}

describe('stagger score', () => {
  it('reads 0 when absent or garbage', () => {
    expect(readHiScore(fakeStore())).toBe(0);
    expect(readHiScore(fakeStore({ 'dr-stagger-hi': 'x' }))).toBe(0);
  });
  it('reads a stored hi-score', () => {
    expect(readHiScore(fakeStore({ 'dr-stagger-hi': '420' }))).toBe(420);
  });
  it('commits only when beaten', () => {
    const s = fakeStore({ 'dr-stagger-hi': '100' });
    expect(commitScore(s, 90)).toBe(100);
    expect(commitScore(s, 250)).toBe(250);
    expect(s._map.get('dr-stagger-hi')).toBe('250');
  });
});
