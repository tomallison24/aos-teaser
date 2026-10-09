import { chromium } from 'playwright';
import { spawn } from 'child_process';
const out = process.argv[2], FPS = 30, DUR = 30;
const b = await chromium.launch({ executablePath: '/opt/pw-browsers/chromium' });
const p = await b.newPage({ viewport: { width: 1080, height: 1920 }, deviceScaleFactor: 1 });
const errs = []; p.on('pageerror', e => errs.push(e.message));
await p.goto('http://localhost:8765/launch/?export');
await p.waitForFunction(() => window.__ready, null, { timeout: 15000 });
const ff = spawn('ffmpeg', ['-y', '-loglevel', 'error', '-f', 'image2pipe', '-framerate', String(FPS), '-c:v', 'mjpeg', '-i', '-',
  '-c:v', 'libx264', '-pix_fmt', 'yuv420p', '-crf', '21', '-preset', 'medium', '-movflags', '+faststart', out], { stdio: ['pipe', 'inherit', 'inherit'] });
for (let i = 0; i <= DUR * FPS; i++) {
  const d = await p.evaluate(t => { window.renderAt(t); return document.getElementById('film').toDataURL('image/jpeg', .95); }, i / FPS);
  const ok = ff.stdin.write(Buffer.from(d.split(',')[1], 'base64'));
  if (!ok) await new Promise(r => ff.stdin.once('drain', r));
}
ff.stdin.end(); await new Promise(r => ff.on('close', r));
console.log(errs.join('\n') || 'no page errors'); await b.close();
