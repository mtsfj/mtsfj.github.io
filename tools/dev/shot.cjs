// node tools/dev/shot.cjs <hour> <out.png> [layerDir] [extraQuery] : the street held at <hour>, the canvas only, at the
// painting's own size (1456 x 816, one pixel a scene pixel). layerDir: serve layer_city_off.webp / street_unlit.webp from that
// folder instead (to show options in the real street). extraQuery: e.g. '&night=red'. PORT env (default 8811).
// One full screenshot per page load: repeated screenshots in one page tend to time out in headless software GL.
const { chromium } = require('playwright'); const fs = require('fs'); const path = require('path');
const [hour, out, layerDir, extra] = process.argv.slice(2);
(async () => {
  const b = await chromium.launch(); const ctx = await b.newContext({ viewport: { width: 1456, height: 816 }, deviceScaleFactor: 1 });
  if (layerDir) await ctx.route(/\/assets\/(layer_city_off|street_unlit)\.webp(\?.*)?$/, async (route) => {
    const name = route.request().url().match(/assets\/([a-z_]+\.webp)/)[1]; const f = path.join(layerDir, name);
    if (fs.existsSync(f)) return route.fulfill({ body: fs.readFileSync(f), contentType: 'image/webp' }); return route.continue(); });
  const p = await ctx.newPage(); const errs = []; p.on('pageerror', (e) => errs.push(e.message));
  await p.goto(`http://127.0.0.1:${process.env.PORT || 8811}/?hour=${hour}${extra || ''}`, { waitUntil: 'load' });
  await p.waitForFunction(() => window.__loaded === true, null, { timeout: 120000 }).catch(() => {});
  await p.waitForTimeout(6000);
  const canvas = await p.$('canvas'); const box = await canvas.boundingBox();
  await p.screenshot({ path: out, clip: { x: box.x, y: box.y, width: Math.min(box.width, 1456), height: Math.min(box.height, 816) } });
  console.log(JSON.stringify({ box, errs: errs.length }));
  await b.close();
})();
