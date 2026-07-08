const mount = document.getElementById('stagger-mount');
const startBtn = document.getElementById('stagger-start');
let cheat = false;
addEventListener('dr:konami', () => { cheat = true; });

async function boot() {
  if (!mount) return;
  const canvas = document.createElement('canvas');
  canvas.setAttribute('aria-label', 'Drunk Stagger mini-game');
  canvas.style.maxWidth = '100%';
  canvas.style.imageRendering = 'pixelated';
  mount.replaceChildren(canvas);
  const { default: start } = await import('./drunk-stagger.js');
  start(canvas, { cheat });
}

startBtn?.addEventListener('click', boot, { once: true });
