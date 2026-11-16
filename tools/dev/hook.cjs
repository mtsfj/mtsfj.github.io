// A test hook for renders and checks, shipping nothing to visitors: serves assets/street.js (unminified) in place of
// street.min.js with a snippet inserted after an anchor line, so a Playwright script can reach the street's internals
// (force a state, step a clock, trigger an event, grab a canvas). Use from your own Playwright script:
//     const { hookStreet } = require('./tools/dev/hook.cjs');
//     await hookStreet(ctx, { anchor: "ws.L = ws.light ? 1 : 0;", snippet: "window.__S = { ws };" });
//     ... page.goto(...); await page.waitForFunction(() => !!window.__S); await page.evaluate(() => { window.__S.ws.state = 'sit'; });
// The anchor must occur once in street.js, at a point where the names the snippet uses are in scope.
const fs = require('fs'); const path = require('path');
async function hookStreet(ctx, { anchor, snippet, src }) {
  const file = src || path.join(__dirname, '..', '..', 'assets', 'street.js');
  await ctx.route(/fonts\.(googleapis|gstatic)\.com/, (r) => r.abort());
  await ctx.route(/\/assets\/street\.min\.js(\?.*)?$/, (r) => {
    let js = fs.readFileSync(file, 'utf8');
    if (js.split(anchor).length !== 2) throw new Error('hook anchor must occur exactly once: ' + anchor);
    js = js.replace(anchor, anchor + '\n' + snippet + '\n');
    return r.fulfill({ body: js, contentType: 'application/javascript' });
  });
}
module.exports = { hookStreet };
