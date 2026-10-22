// Renders the aOS 2 teaser to an MP4 (1080x1920, 30fps), and with --og the link preview (og.png).
//   node render.mjs film.mp4        (serve the repo first: python3 -m http.server 8765; PORT=... for another port)
//   node render.mjs --og og.png
// Playwright is loaded from the global node_modules, so nothing is installed here.
import { createRequire } from 'module';
import { execSync, spawn } from 'child_process';
import fs from 'fs';
const require = createRequire(execSync('npm root -g').toString().trim() + '/');
const { chromium } = require('playwright');
const OG = process.argv[2] === '--og', out = process.argv[OG ? 3 : 2], FPS = 30, DUR = 38;
const URL = `http://localhost:${process.env.PORT || 8765}/aos2/?export`;
const b = await chromium.launch({ executablePath: '/opt/pw-browsers/chromium' });
const p = await b.newPage({ viewport: { width: 1080, height: 1920 }, deviceScaleFactor: 1 });
const errs = []; p.on('pageerror', e => errs.push(e.message));
await p.goto(URL);
await p.waitForFunction(() => window.__ready, null, { timeout: 15000 });
if (OG) {
  const d = await p.evaluate(() => { const c = document.createElement('canvas'); c.width = 1200; c.height = 630; window.renderOG(c); return c.toDataURL('image/png'); });
  fs.writeFileSync(out, Buffer.from(d.split(',')[1], 'base64'));
} else {
  const ff = spawn('ffmpeg', ['-y', '-loglevel', 'error', '-f', 'image2pipe', '-framerate', String(FPS), '-c:v', 'mjpeg', '-i', '-',
    '-c:v', 'libx264', '-pix_fmt', 'yuv420p', '-crf', '21', '-preset', 'medium', '-movflags', '+faststart', out], { stdio: ['pipe', 'inherit', 'inherit'] });
  for (let i = 0; i <= DUR * FPS; i++) {
    const d = await p.evaluate(t => { window.renderAt(t); return document.getElementById('film').toDataURL('image/jpeg', .95); }, i / FPS);
    const ok = ff.stdin.write(Buffer.from(d.split(',')[1], 'base64'));
    if (!ok) await new Promise(r => ff.stdin.once('drain', r));
  }
  ff.stdin.end(); await new Promise(r => ff.on('close', r));
}
console.log(errs.join('\n') || 'no page errors'); await b.close();
