import { KonamiDetector } from '../lib/eastereggs';

export function startMatrixRain(): void {
  if (matchMedia('(prefers-reduced-motion: reduce)').matches) return;
  if (document.getElementById('dr-matrix')) return;
  const c = document.createElement('canvas');
  c.id = 'dr-matrix';
  Object.assign(c.style, {
    position: 'fixed', inset: '0', zIndex: '9999', background: '#000', cursor: 'pointer',
  } as CSSStyleDeclaration);
  document.body.appendChild(c);
  const ctx = c.getContext('2d')!;
  let cols: number[] = [];
  const glyphs = 'アカサタナ01DRUNKROBOT'.split('');
  function resize() {
    c.width = innerWidth; c.height = innerHeight;
    cols = new Array(Math.ceil(c.width / 14)).fill(0);
  }
  resize();
  addEventListener('resize', resize);
  let raf = 0;
  function draw() {
    ctx.fillStyle = 'rgba(0,0,0,0.08)';
    ctx.fillRect(0, 0, c.width, c.height);
    ctx.fillStyle = '#39ff88';
    ctx.font = '14px monospace';
    cols.forEach((y, i) => {
      ctx.fillText(glyphs[(Math.random() * glyphs.length) | 0], i * 14, y * 14);
      cols[i] = y * 14 > c.height && Math.random() > 0.975 ? 0 : y + 1;
    });
    raf = requestAnimationFrame(draw);
  }
  draw();
  function stop() {
    cancelAnimationFrame(raf);
    removeEventListener('resize', resize);
    c.remove();
  }
  c.addEventListener('click', stop);
  addEventListener('keydown', stop, { once: true });
}

function konamiCelebration(): void {
  document.documentElement.dataset.konami = '1';
  window.dispatchEvent(new CustomEvent('dr:konami'));
  setTimeout(() => { delete document.documentElement.dataset.konami; }, 1200);
}

function initGlobalEggs(): void {
  console.log(
    '%c DRUNK ROBOT %c insert coin to continue ',
    'background:#39ff88;color:#040805;font-weight:bold',
    'color:#ffb000',
  );
  const konami = new KonamiDetector();
  addEventListener('keydown', (e) => {
    if (konami.push(e.key)) konamiCelebration();
  });
}

declare global { interface Window { __drEggs?: boolean; } }
if (typeof window !== 'undefined' && !window.__drEggs) {
  window.__drEggs = true;
  initGlobalEggs();
}
