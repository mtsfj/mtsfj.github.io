const { chromium } = require('/opt/node22/lib/node_modules/playwright');
(async () => {
  const b = await chromium.launch();
  for (const h of ['19.5', '7.5']) {
    const ctx = await b.newContext({ viewport: { width: 390, height: 844 }, deviceScaleFactor: 2, isMobile: true, hasTouch: true, serviceWorkers: 'block' });
    const p = await ctx.newPage(); const errs = []; p.on('pageerror', (e) => errs.push(e.message)); p.on('console', (m) => { if (m.type() === 'error') errs.push(m.text()); });
    await p.goto('http://localhost:8123/?lang=fr&hour=' + h, { waitUntil: 'load', timeout: 180000 });
    await p.waitForTimeout(25000);
    await p.screenshot({ path: process.argv[2] + '_' + h + '.png', timeout: 120000 });
    const ov = await p.evaluate(() => document.documentElement.scrollWidth - document.documentElement.clientWidth);
    console.log(h, 'overflow', ov, errs.length ? errs.slice(0, 3) : 'no errors');
    await ctx.close();
  }
  await b.close();
})();
