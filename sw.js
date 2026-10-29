/* mtsfj.github.io · the site's files kept in the browser between visits (a service worker, registered by assets/site.js).
   GitHub Pages lets a file be kept 10 minutes; after that the browser asks the server again for each of the page's files. Here:
   - a file whose address carries its version (?v=…) never changes under that address: served from here, from the network only
     the first time (when a new version comes, the older one of the same file is dropped);
   - a page (HTML): from the network first (a new post shows at once), this copy only offline;
   - any other file of the site (fonts, three.min.js, a layer without ?v=): from here at once, fetched again behind, for the
     next visit.
   Other sites' files (the audience count) are not touched. To change these rules, change CACHE: the old cache is emptied. */
const CACHE = 'mtsfj-1';

self.addEventListener('install', () => self.skipWaiting());
self.addEventListener('activate', (e) => e.waitUntil((async () => {
  for (const k of await caches.keys()) if (k !== CACHE) await caches.delete(k);
  if (self.registration.navigationPreload) await self.registration.navigationPreload.enable();
  await self.clients.claim();
})()));

self.addEventListener('fetch', (e) => {
  const r = e.request, u = new URL(r.url);
  if (r.method !== 'GET' || u.origin !== location.origin || r.headers.has('range') || u.pathname === '/sw.js') return;
  if (r.mode === 'navigate') e.respondWith(page(e));
  else if (/[?&]v=/.test(u.search)) e.respondWith(kept(e, u));
  else e.respondWith(fresh(e));
});

const ok = (res) => res && res.ok && res.type === 'basic';
const match = (c, r) => c.match(r, { ignoreVary: true });

async function page(e) {
  try {
    const res = (await e.preloadResponse) || await fetch(e.request);
    if (ok(res)) { const copy = res.clone(); e.waitUntil(caches.open(CACHE).then((c) => c.put(e.request, copy)).catch(() => {})); }
    return res;
  } catch (err) {
    const c = await caches.open(CACHE), hit = await match(c, e.request) || await c.match(e.request, { ignoreVary: true, ignoreSearch: true });
    if (hit) return hit;
    throw err;
  }
}

async function kept(e, u) {
  const c = await caches.open(CACHE), hit = await match(c, e.request);
  if (hit) return hit;
  const res = await fetch(e.request);
  if (ok(res)) {
    const copy = res.clone();
    e.waitUntil((async () => {
      for (const k of await c.keys()) { const ku = new URL(k.url); if (ku.pathname === u.pathname && ku.search !== u.search) await c.delete(k); }
      await c.put(e.request, copy);
    })().catch(() => {}));
  }
  return res;
}

async function fresh(e) {
  const c = await caches.open(CACHE), hit = await match(c, e.request);
  const net = fetch(e.request).then((res) => {
    if (ok(res)) { const copy = res.clone(); e.waitUntil(c.put(e.request, copy).catch(() => {})); }
    return res;
  });
  if (hit) { e.waitUntil(net.catch(() => {})); return hit; }
  return net;
}
