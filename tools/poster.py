#!/usr/bin/env python3
"""The street's poster: its first frame, as the hero shows it at once while three.js and the street load (index.html).

    python3 tools/poster.py            render, encode, compare: writes assets/poster_{open,settled}.{avif,webp} (whole) and
                                       assets/poster_{open,settled}_m.{avif,webp} (a phone's: the middle CROP columns)
    python3 tools/poster.py --check    render and compare with the posters there (nothing written): run it after any change to the
                                       street's look (a layer, a light, a grade); a poster that no longer matches is redone by the first form

The first frame is drawn by the street itself (Chromium headless through Playwright for Node: npm i -g playwright; the repository
served on a free port), whole (1456 x 816, one pixel a scene pixel), at 14 h (the painted evening: everything open, no grade; the
hours index.html shows a poster at), its clock held, the moment its fade starts: on the tab's first visit as the opening sets the
street (open), after it as the evening is under way (settled); the rain's two curtains left out (they fall over the poster, as over
the placeholder before), the homes' windows lit (street.js lights them under a poster); Math.random seeded, so it is the same each
time. Encoded AVIF (4:4:4, QUALITY: about 200 KB, what a phone on 4G gets in well under a second; WebP for the browsers without it).
Printed: how far each poster is from its frame (per pixel, the largest channel), and how far the street's own first frame moves
from one load to the next (the water, the steam, the rain under the lamp, the lights' breathing: the poster can be no closer).
Needs Pillow built with AVIF (pip install pillow) and numpy.
"""
import argparse, functools, http.server, io, json, os, socket, subprocess, sys, tempfile, threading
import numpy as np
from PIL import Image

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
QUALITY = 78                                       # AVIF quality (4:4:4, tuned for SSIM: the painting's grain kept best)
CROP = (448, 1008)                                 # a phone's poster: these scene columns (index.html: a view up to 560 px wide, centred)
WEBP_QUALITY = 90
HOUR = 14

CAPTURE = r"""
// (written by tools/poster.py) the street's first frame, held: node capture.js <url> <out.png> <settled 0|1> <pre seconds>
const pw = require('playwright'), fs = require('fs');
const [url, out, settled, pre] = process.argv.slice(2);
(async () => {
  const b = await pw.chromium.launch();
  const ctx = await b.newContext({ viewport: { width: 1456, height: 816 }, deviceScaleFactor: 1, serviceWorkers: 'block' });
  await ctx.addInitScript(() => {                  // seeded, the clock held (dt 0) until told
    // (each caller its own seeded sequence, by where it is called from: the same draws whatever runs between them)
    const sites = new Map(), h32 = (str) => { let h = 2166136261; for (let i = 0; i < str.length; i++) { h ^= str.charCodeAt(i); h = Math.imul(h, 16777619); } return h >>> 0; };
    const m32 = (a) => { a = a + 0x6D2B79F5 | 0; let t = Math.imul(a ^ a >>> 15, 1 | a); t = t + Math.imul(t ^ t >>> 7, 61 | t) ^ t; return ((t ^ t >>> 14) >>> 0) / 4294967296; };
    Math.random = function () { const st = new Error().stack.split('\n').slice(2, 4).map((l) => { const m = l.match(/at (?:(\S+) \()?.*:(\d+):(\d+)\)?$/); return m ? (m[1] || '') + ':' + m[3] : l; }).join('|'); const c = (sites.get(st) || 0) + 1; sites.set(st, c); return m32(h32(st) ^ Math.imul(c, 0x9E3779B1) ^ 4242); };
    window.__dt = 0;
    Object.defineProperty(window, '__poster', { value: { on: true }, writable: false });   // (street.js as under a poster; none drawn)
  });
  if (settled === '1') await ctx.addInitScript(() => { try { sessionStorage.setItem('mtsfj-opened', '1'); } catch (e) {} });
  await ctx.route(/\/assets\/street(\.min)?\.js(\?.*)?$/, async (route) => {
    const r = await route.fetch(); let s = await r.text();
    if (/\.min\.js/.test(route.request().url())) s = fs.readFileSync(process.env.STREET_SRC, 'utf8');   // (the readable source: its names)
    const rep = (a, c) => { if (s.indexOf(a) < 0) throw new Error('street.js changed: ' + a.slice(0, 50)); s = s.replace(a, c); };
    rep('const dt = Math.min(clock.getDelta(), 0.05); t += dt;', 'const dt = window.__dt; t += dt;');
    rep('THREE.DefaultLoadingManager.onLoad = () => {', 'THREE.DefaultLoadingManager.onLoad = () => { window.__loaded = true;');   // (everything in: on a slow machine the fade may have started before)
    rep('\n  frame();\n  if (reduced) setTimeout(frame, 800);', '\n  window.__S = { frame, renderer, rain, rain2, FADE, LATE, OPEN, PACE, get t() { return t; } };\n  frame();\n  if (reduced) setTimeout(frame, 800);');
    await route.fulfill({ response: r, body: s, headers: { ...r.headers(), 'content-length': undefined } });
  });
  const p = await ctx.newPage(); const errs = [];
  p.on('pageerror', (e) => errs.push(e.message)); p.on('console', (m) => { if (m.type() === 'error' && !/poster_|Failed to load resource/.test(m.text())) errs.push(m.text()); });
  await p.goto(url, { waitUntil: 'load', timeout: 120000 });
  await p.waitForFunction(() => window.__S, null, { timeout: 60000 });
  await p.evaluate(() => { window.__S.PACE.t0 = Infinity; });
  await p.waitForFunction(() => { const S = window.__S; return window.__loaded && S.FADE.done && S.LATE.started && S.LATE.pending === 0; }, null, { timeout: 180000, polling: 250 });
  await p.waitForTimeout(1500);
  const png = await p.evaluate(async (pre) => {
    const S = window.__S, R = S.renderer;
    window.requestAnimationFrame = () => 1; await new Promise((r) => setTimeout(r, 300));
    S.OPEN.t0 = -1;                                 // (the opening waits, as before the fade, while `pre` seconds go by)
    const real = R.render; R.render = function () {};
    for (let done = 0; done < pre - 1e-9; done += 1 / 60) { window.__dt = Math.min(1 / 60, pre - done); S.frame(); }
    R.render = real; S.OPEN.t0 = S.t; window.__dt = 0;
    S.rain.visible = false; S.rain2.visible = false;
    S.frame();
    return R.domElement.toDataURL('image/png');
  }, +pre);
  fs.writeFileSync(out, Buffer.from(png.split(',')[1], 'base64'));
  if (errs.length) { console.error(errs.join('\n')); process.exit(2); }
  await b.close();
})();
"""


def serve():
    h = functools.partial(http.server.SimpleHTTPRequestHandler, directory=ROOT)
    class Quiet(h.func):
        def log_message(self, *a): pass
    s = socket.socket(); s.bind(('127.0.0.1', 0)); port = s.getsockname()[1]; s.close()
    srv = http.server.ThreadingHTTPServer(('127.0.0.1', port), functools.partial(Quiet, directory=ROOT))
    threading.Thread(target=srv.serve_forever, daemon=True).start()
    return srv, port


def capture(port, settled, pre, tmp):
    js = os.path.join(tmp, 'capture.js'); open(js, 'w').write(CAPTURE)
    out = os.path.join(tmp, f'first_{settled}_{pre}.png')
    env = dict(os.environ, STREET_SRC=os.path.join(ROOT, 'assets', 'street.js'))
    if 'NODE_PATH' not in env:
        g = subprocess.run(['npm', 'root', '-g'], capture_output=True, text=True).stdout.strip()
        if g: env['NODE_PATH'] = g
    subprocess.run(['node', js, f'http://127.0.0.1:{port}/index.html?hour={HOUR}', out, '1' if settled else '0', str(pre)], check=True, env=env)
    return np.asarray(Image.open(out).convert('RGB'))


def diff(a, b):
    d = np.abs(a.astype(int) - b.astype(int)).max(axis=2)
    return {'max': int(d.max()), 'mean': round(float(d.mean()), 2), 'over8': round(float((d > 8).mean()), 4), 'over32': round(float((d > 32).mean()), 5)}


def encode(rgb):
    im = Image.fromarray(rgb, 'RGB')
    b = io.BytesIO(); im.save(b, 'AVIF', quality=QUALITY, subsampling='4:4:4', speed=4, advanced=(('tune', 'ssim'),)); avif = b.getvalue()
    b = io.BytesIO(); im.save(b, 'WEBP', quality=WEBP_QUALITY, method=6); webp = b.getvalue()
    return avif, webp


def main():
    ap = argparse.ArgumentParser(description="le poster de la rue (voir la docstring)")
    ap.add_argument('--check', action='store_true', help="compare seulement, n'écrit rien")
    a = ap.parse_args()
    srv, port = serve()
    report = {}
    with tempfile.TemporaryDirectory() as tmp:
        for name, settled in (('open', False), ('settled', True)):
            ref = capture(port, settled, 0, tmp)
            later = capture(port, settled, 3, tmp)      # (the same frame after 3 s of waiting for the layers: what moves by itself)
            for sfx, sl in (('', slice(None)), ('_m', slice(*CROP))):
                avif_p, webp_p = (os.path.join(ROOT, 'assets', f'poster_{name}{sfx}.{x}') for x in ('avif', 'webp'))
                r0, l0 = np.ascontiguousarray(ref[:, sl]), np.ascontiguousarray(later[:, sl])
                if not a.check:
                    avif, webp = encode(r0)
                    open(avif_p, 'wb').write(avif); open(webp_p, 'wb').write(webp)
                r = {'bytes': {'avif': os.path.getsize(avif_p), 'webp': os.path.getsize(webp_p)}, 'living': diff(r0, l0)}
                for x, pth in (('avif', avif_p), ('webp', webp_p)):
                    dec = np.asarray(Image.open(pth).convert('RGB'))
                    r[x] = diff(dec, r0); r[x + '_vs_3s'] = diff(dec, l0)
                report[name + sfx] = r
                print(name + sfx, json.dumps(r))
    srv.shutdown()
    bad = [n for n, r in report.items() if r['avif']['over32'] > 0.001 or r['avif']['mean'] > 3.5]
    if bad:
        print('the poster no longer matches the street:', ', '.join(bad), '(python3 tools/poster.py)')
        sys.exit(1)


if __name__ == '__main__':
    main()
