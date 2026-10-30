// node seq2.js <prefix> <list of finale dawnT> [hours mode: H=1] — frozen full-size frames at exact dawn times (calm finale), or at hours
const { chromium } = require('/opt/node22/lib/node_modules/playwright');
const [prefix, list] = [process.argv[2], (process.argv[3] || '').split(',').map(Number)];
const HOURS = process.env.H === '1';
(async () => {
  const b = await chromium.launch();
  const ctx = await b.newContext({ viewport: { width: 364, height: 204 }, serviceWorkers: 'block' });
  const p = await ctx.newPage(); const errs = []; p.on('pageerror', (e) => errs.push(e.message)); p.on('console', (m) => { if (m.type() === 'error') errs.push(m.text()); });
  await p.goto('http://localhost:8123/' + (process.env.PAGE || '_dbg.html') + '?lang=fr' + (process.env.Q ? '&' + process.env.Q : ''), { waitUntil: 'load', timeout: 120000 });
  await p.waitForFunction(() => window.__S && window.__t > 0, null, { timeout: 120000 });
  await p.evaluate(() => { window.__stop = 16; window.__dtHook = (raw) => (window.__t >= window.__stop ? 0 : 0.5); });
  await p.waitForFunction(() => window.__t >= 16, null, { timeout: 600000, polling: 500 });
  await p.setViewportSize({ width: 1456, height: 816 });
  const info = () => p.evaluate(() => { const S = window.__S; return { t: +window.__t.toFixed(2), h: +S.CLOCK.h.toFixed(2), dawnT: +S.SKYF.dawnT.toFixed(2), dp: S.SKYF.dp !== undefined ? +(+S.SKYF.dp).toFixed(2) : null }; });
  if (HOURS) {
    for (const h of list) { await p.evaluate((h) => { window.__S.setTimeOverride(h, 0); window.__stop = window.__t + 2; }, h); await p.waitForFunction(() => window.__t >= window.__stop, null, { timeout: 600000 }); await p.waitForTimeout(3000); await p.screenshot({ path: `${prefix}_h${h}.png`, timeout: 120000 }); console.log('h', h, JSON.stringify(await info())); }
  } else {
    await p.evaluate(() => { window.__S.finStart(true); window.__dtHook = (raw) => { const T = window.__stopDawn; return window.__S.SKYF.dawnT >= T ? 0 : (window.__S.SKYF.dawnT >= 0 ? Math.min(0.25, T - window.__S.SKYF.dawnT + 0.001) : 0.5); }; });
    for (const T of list) { await p.evaluate((T) => { window.__stopDawn = T; }, T); await p.waitForFunction((T) => window.__S.SKYF.dawnT >= T, T, { timeout: 900000, polling: 300 }); await p.waitForTimeout(3000); await p.screenshot({ path: `${prefix}_d${T}.png`, timeout: 120000 }); console.log('d', T, JSON.stringify(await info())); }
  }
  console.log(errs.length ? errs.slice(0, 5) : 'no errors');
  await b.close();
})();
