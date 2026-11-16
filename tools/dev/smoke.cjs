// node tools/dev/smoke.cjs : the home loaded on a desktop and a phone at 14 h, 22 h, 3 h, the red night and 5 h; prints "ok" or
// the page's errors for each, and every asset that answered 404. Serve the repository first (python3 -m http.server PORT);
// PORT env (default 8811). Exit 1 on any error or 404.
const { chromium, devices } = require('playwright');
const PORT = process.env.PORT || 8811;
(async () => {
  const b = await chromium.launch(); let bad = 0;
  for (const [label, opts] of [['desktop', { viewport: { width: 1456, height: 816 } }], ['phone', devices['Pixel 7']]]) {
    for (const q of ['?hour=14', '?hour=22', '?hour=3', '?hour=22&night=red', '?hour=5']) {
      const c = await b.newContext(opts); const p = await c.newPage(); const errs = [];
      p.on('pageerror', (e) => errs.push(e.message)); p.on('console', (m) => m.type() === 'error' && errs.push(m.text()));
      p.on('response', (r) => { if (r.status() === 404 && r.url().includes('127.0.0.1')) errs.push('404 ' + r.url()); });
      await p.goto(`http://127.0.0.1:${PORT}/` + q, { waitUntil: 'load' }); await p.waitForTimeout(7000);
      console.log(label, q, errs.length ? 'ERRORS ' + errs.slice(0, 3).join(' | ') : 'ok'); bad += errs.length; await c.close();
    }
  }
  await b.close(); process.exit(bad ? 1 : 0);
})();
