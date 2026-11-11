// Renders assets/health/share.png, the /health link preview, from
// share_card.html and the current _data/health.json, with headless Chrome.
//
//   node scripts/health/share_image.mjs
//
// Set CHROME to the browser binary if it isn't in the default macOS place.
// The card has no dates or values, so it only needs re-running when the
// design changes.
import { spawn } from 'node:child_process';
import { mkdtempSync, readFileSync, rmSync, writeFileSync } from 'node:fs';
import { tmpdir } from 'node:os';
import { join } from 'node:path';

const ROOT = new URL('../../', import.meta.url).pathname;
const OUT = join(ROOT, 'assets/health/share.png');
const CHROME = process.env.CHROME || '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome';
const PORT = 9334;

const data = JSON.parse(readFileSync(join(ROOT, '_data/health.json'), 'utf8'));
if (data.enc) throw new Error('_data/health.json is encrypted; the card needs the public data.');
const html = readFileSync(join(ROOT, 'scripts/health/share_card.html'), 'utf8')
  .replace('__HEALTH_DATA__', JSON.stringify(data).replace(/</g, '\\u003c'));

const work = mkdtempSync(join(tmpdir(), 'health-share-'));
const page = join(work, 'card.html');
writeFileSync(page, html);

const chrome = spawn(CHROME, [
  '--headless=new', `--remote-debugging-port=${PORT}`, `--user-data-dir=${join(work, 'profile')}`,
  '--no-first-run', '--no-default-browser-check', '--hide-scrollbars', 'about:blank',
], { stdio: ['ignore', 'ignore', 'pipe'] });

try {
  await new Promise((resolve, reject) => {
    chrome.stderr.on('data', (d) => { if (String(d).includes('DevTools listening')) resolve(); });
    chrome.on('error', reject);
    setTimeout(() => reject(new Error('Chrome did not start')), 20000);
  });
  const targets = await (await fetch(`http://127.0.0.1:${PORT}/json/list`)).json();
  const ws = new WebSocket(targets.find((t) => t.type === 'page').webSocketDebuggerUrl);
  await new Promise((resolve) => ws.addEventListener('open', resolve));

  let seq = 0;
  const pending = new Map();
  ws.addEventListener('message', (event) => {
    const msg = JSON.parse(event.data);
    if (!pending.has(msg.id)) return;
    const { resolve, reject } = pending.get(msg.id);
    pending.delete(msg.id);
    msg.error ? reject(new Error(msg.error.message)) : resolve(msg.result);
  });
  const send = (method, params = {}) => new Promise((resolve, reject) => {
    const id = ++seq;
    pending.set(id, { resolve, reject });
    ws.send(JSON.stringify({ id, method, params }));
  });

  // 1200x630 is the usual link-preview size; 2x keeps the text sharp.
  await send('Emulation.setDeviceMetricsOverride', { width: 1200, height: 630, deviceScaleFactor: 2, mobile: false });
  await send('Page.navigate', { url: `file://${page}` });
  let ready = false;
  for (let i = 0; i < 100 && !ready; i++) {
    await new Promise((r) => setTimeout(r, 200));
    const { result } = await send('Runtime.evaluate', {
      expression: `document.body?.dataset.ready === '1' && document.fonts.status === 'loaded'`,
      returnByValue: true,
    });
    ready = result.value === true;
  }
  if (!ready) throw new Error('The card did not finish rendering (is the Inter font reachable?)');
  const { data: png } = await send('Page.captureScreenshot', {
    format: 'png', clip: { x: 0, y: 0, width: 1200, height: 630, scale: 1 },
  });
  writeFileSync(OUT, Buffer.from(png, 'base64'));
  ws.close();
  console.log(`Wrote ${OUT}`);
} finally {
  // Chrome keeps writing to its profile while it shuts down, so wait for it.
  const exited = new Promise((resolve) => chrome.once('exit', resolve));
  chrome.kill();
  await Promise.race([exited, new Promise((r) => setTimeout(r, 5000))]);
  rmSync(work, { recursive: true, force: true, maxRetries: 5, retryDelay: 200 });
}
