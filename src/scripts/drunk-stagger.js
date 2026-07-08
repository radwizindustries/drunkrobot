// Minimal 8-bit dodge runner. Robot auto-runs; hop (space/tap) over/around
// obstacles; collect bolts for score. Endless, speeds up. No deps.
import { commitScore, readHiScore } from '../lib/stagger-score.ts';

export default function start(canvas, opts = {}) {
  const ctx = canvas.getContext('2d');
  const W = (canvas.width = 480), H = (canvas.height = 200), GROUND = H - 30;
  const reduce = matchMedia('(prefers-reduced-motion: reduce)').matches;
  let store; try { store = localStorage; } catch { store = { getItem: () => null, setItem() {} }; }

  const robot = { x: 60, y: GROUND, vy: 0, on: true };
  let obstacles = [], bolts = [], t = 0, speed = 3, score = 0, over = false;
  let lives = opts.cheat ? 99 : 1;
  const hi0 = readHiScore(store);

  function hop() { if (robot.on && !over) { robot.vy = -9; robot.on = false; } }
  // over=false lets the already-running loop resume stepping; do not start a
  // second rAF loop here or the game runs at double speed.
  function reset() { obstacles = []; bolts = []; t = 0; speed = 3; score = 0; over = false; lives = opts.cheat ? 99 : 1; }

  function spawn() {
    if (t % 70 === 0) obstacles.push({ x: W, w: 14, h: 22 + (Math.random() * 16 | 0) });
    if (t % 90 === 45) bolts.push({ x: W, y: GROUND - 40 - (Math.random() * 40 | 0), r: 7 });
  }
  function step() {
    t++; spawn(); speed += 0.002;
    robot.vy += 0.6; robot.y += robot.vy;
    if (robot.y >= GROUND) { robot.y = GROUND; robot.vy = 0; robot.on = true; }
    obstacles.forEach((o) => (o.x -= speed));
    bolts.forEach((b) => (b.x -= speed));
    obstacles = obstacles.filter((o) => o.x + o.w > 0);
    bolts = bolts.filter((b) => b.x + b.r > 0);
    for (const o of obstacles) {
      if (60 + 16 > o.x && 60 < o.x + o.w && robot.y > GROUND - o.h) {
        if (--lives <= 0) { over = true; commitScore(store, score); }
        else o.x = -99;
      }
    }
    for (const b of bolts) {
      const dx = 68 - b.x, dy = (robot.y - 8) - b.y;
      if (dx * dx + dy * dy < (b.r + 12) ** 2) { b.x = -99; score += 10; }
    }
    if (t % 6 === 0) score += 1;
  }
  function draw() {
    ctx.fillStyle = '#040805'; ctx.fillRect(0, 0, W, H);
    ctx.strokeStyle = '#173a22'; ctx.beginPath(); ctx.moveTo(0, GROUND + 16); ctx.lineTo(W, GROUND + 16); ctx.stroke();
    ctx.fillStyle = '#5c8a6c'; obstacles.forEach((o) => ctx.fillRect(o.x, GROUND - o.h + 16, o.w, o.h));
    ctx.fillStyle = '#ffb000'; bolts.forEach((b) => { ctx.beginPath(); ctx.arc(b.x, b.y, b.r, 0, 7); ctx.fill(); });
    ctx.fillStyle = '#39ff88'; ctx.fillRect(60, robot.y - 16, 16, 16);
    ctx.font = '12px monospace'; ctx.fillStyle = '#39ff88';
    ctx.fillText('SCORE ' + String(score).padStart(5, '0'), 8, 16);
    const hi = Math.max(hi0, score);
    ctx.fillStyle = '#ffb000'; ctx.fillText('HI ' + String(hi).padStart(5, '0'), W - 92, 16);
    if (over) { ctx.fillStyle = '#ffb000'; ctx.font = '16px monospace'; ctx.fillText('GAME OVER - press space', W / 2 - 110, H / 2); }
  }

  let raf = 0;
  function loop() { if (!over) step(); draw(); raf = requestAnimationFrame(loop); }

  function onKey(e) {
    if (e.code === 'Space' || e.key === ' ') { e.preventDefault(); over ? reset() : hop(); }
  }
  function onTap() { over ? reset() : hop(); }
  addEventListener('keydown', onKey);
  canvas.addEventListener('pointerdown', onTap);
  if (reduce) { draw(); ctx.fillStyle = '#39ff88'; ctx.font = '12px monospace'; ctx.fillText('tap to play', W / 2 - 30, H / 2 + 24); }
  else loop();

  return { destroy() { cancelAnimationFrame(raf); removeEventListener('keydown', onKey); canvas.removeEventListener('pointerdown', onTap); } };
}
