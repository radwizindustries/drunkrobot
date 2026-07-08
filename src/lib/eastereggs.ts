const MATRIX_TRIGGERS = new Set(['neo', 'wake up neo', 'matrix']);

export function isMatrixQuery(q: string): boolean {
  return MATRIX_TRIGGERS.has(q.trim().toLowerCase());
}

const KONAMI = [
  'ArrowUp', 'ArrowUp', 'ArrowDown', 'ArrowDown',
  'ArrowLeft', 'ArrowRight', 'ArrowLeft', 'ArrowRight', 'b', 'a',
];

export class KonamiDetector {
  private i = 0;
  /** Returns true on the key press that completes the sequence. */
  push(key: string): boolean {
    const want = KONAMI[this.i];
    const got = key.length === 1 ? key.toLowerCase() : key;
    if (got === want) {
      this.i++;
      if (this.i === KONAMI.length) { this.i = 0; return true; }
      return false;
    }
    // Reset, but allow this key to start a fresh match.
    this.i = got === KONAMI[0] ? 1 : 0;
    return false;
  }
}
