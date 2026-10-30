const { chromium } = require('/opt/node22/lib/node_modules/playwright');
(async () => {
  const b = await chromium.launch();
  const ctx = await b.newContext({ viewport: { width: 1456, height: 816 }, serviceWorkers: 'block' });
  const p = await ctx.newPage(); const errs = []; p.on('pageerror', (e) => errs.push(e.message));
  await p.goto('http://localhost:8123/?lang=fr&hour=19.5', { waitUntil: 'load', timeout: 180000 });
  await p.addStyleTag({ content: 'body *{visibility:hidden!important} canvas{visibility:visible!important}' });
  await p.waitForTimeout(40000);
  await p.screenshot({ path: process.argv[2], timeout: 120000 });
  const r = await p.evaluate(() => { const c = document.querySelector('canvas'); const b = c.getBoundingClientRect(); return [b.x, b.y, b.width, b.height, c.width, c.height]; });
  console.log('canvas', r, errs.length ? errs : 'no errors');
  await b.close();
})();
