const KEY = 'dr-stagger-hi';

export function readHiScore(store: Pick<Storage, 'getItem'>): number {
  const raw = store.getItem(KEY);
  const n = raw == null ? NaN : parseInt(raw, 10);
  return Number.isFinite(n) && n >= 0 ? n : 0;
}

export function commitScore(store: Pick<Storage, 'getItem' | 'setItem'>, score: number): number {
  const hi = readHiScore(store);
  if (score > hi) { store.setItem(KEY, String(score)); return score; }
  return hi;
}
