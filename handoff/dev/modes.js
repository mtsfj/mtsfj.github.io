// red night (hour 21, ?night=red) and the fuses' power cut at night (hour 1, ~2.5 s into the cut): full frames
const { chromium } = require('/opt/node22/lib/node_modules/playwright');
(async () => {
  const b = await chromium.launch();
  for (const [name, q, cut] of [['red', 'hour=21&night=red', false], ['cut', 'hour=1', true]]) {
    const ctx = await b.newContext({ viewport: { width: 364, height: 204 }, serviceWorkers: 'block' });
    const p = await ctx.newPage(); const errs = []; p.on('pageerror', (e) => errs.push(e.message));
    await p.goto('http://localhost:8123/' + (process.env.PAGE || '_dbg.html') + '?lang=fr&' + q, { waitUntil: 'load', timeout: 120000 });
    await p.waitForFunction(() => window.__S && window.__t > 0, null, { timeout: 120000 });
    await p.evaluate(() => { window.__stop = 18; window.__dtHook = () => (window.__t >= window.__stop ? 0 : 0.5); });
    await p.waitForFunction(() => window.__t >= 18, null, { timeout: 600000, polling: 500 });
    await p.setViewportSize({ width: 1456, height: 816 });
    if (cut) { await p.evaluate(() => { window.__S.powerCut(); window.__stop = window.__t + 2.5; window.__dtHook = () => (window.__t >= window.__stop ? 0 : 0.1); }); await p.waitForFunction(() => window.__t >= window.__stop, null, { timeout: 600000, polling: 500 }); }
    await p.waitForTimeout(4000);
    await p.screenshot({ path: `${process.argv[2]}_${name}.png`, timeout: 120000 });
    console.log(name, errs.length ? errs : 'no errors');
    await ctx.close();
  }
  await b.close();
})();
