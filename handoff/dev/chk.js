const { chromium } = require('/opt/node22/lib/node_modules/playwright');
(async () => {
  const b = await chromium.launch();
  for (const path of ['', 'blog/', 'blog/modele.html', 'articles/pinductor.html', 'articles/sycophancy.html', '404.html']) {
    const p = await b.newPage({ viewport: { width: 1920, height: 1080 } }); const errs = [];
    p.on('pageerror', (e) => errs.push(e.message)); p.on('console', (m) => { if (m.type() === 'error') errs.push(m.text()); });
    p.on('requestfailed', (r) => errs.push('FAILED ' + r.url()));
    await p.goto('http://localhost:8123/' + path, { waitUntil: 'domcontentloaded' }); await p.waitForTimeout(path === '' ? 6000 : 2500);
    const info = await p.evaluate(() => ({ title: document.title, ld: document.querySelectorAll('head script[type="application/ld+json"]').length, an: !!document.querySelector('script[src*="analytics.js"]'), walls: document.querySelectorAll('.wall').length }));
    console.log(path || '/', JSON.stringify(info), errs.length ? errs.slice(0, 4) : 'no errors');
    await p.close();
  }
  await b.close();
})();
