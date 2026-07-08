import { describe, expect, it } from 'vitest';
import { isMatrixQuery, KonamiDetector } from './eastereggs';

describe('isMatrixQuery', () => {
  it('matches the trigger phrases case-insensitively', () => {
    for (const q of ['neo', 'NEO', '  Wake Up Neo ', 'matrix']) {
      expect(isMatrixQuery(q)).toBe(true);
    }
  });
  it('ignores unrelated queries', () => {
    for (const q of ['robot', 'neon', '']) expect(isMatrixQuery(q)).toBe(false);
  });
});

describe('KonamiDetector', () => {
  const seq = ['ArrowUp','ArrowUp','ArrowDown','ArrowDown','ArrowLeft','ArrowRight','ArrowLeft','ArrowRight','b','a'];
  it('fires only when the full sequence completes', () => {
    const d = new KonamiDetector();
    const results = seq.map((k) => d.push(k));
    expect(results.slice(0, 9).every((r) => r === false)).toBe(true);
    expect(results[9]).toBe(true);
  });
  it('resets on a wrong key and accepts uppercase B/A', () => {
    const d = new KonamiDetector();
    d.push('ArrowUp'); d.push('x'); // wrong -> reset
    const results = seq.map((k) => d.push(k === 'b' ? 'B' : k === 'a' ? 'A' : k));
    expect(results[9]).toBe(true);
  });
});
