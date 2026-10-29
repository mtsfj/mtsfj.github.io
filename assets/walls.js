/* mtsfj.github.io · the walls. On a wide screen the street goes on down the page's margins: a facade on each side, in
   the scene's pixels (2 screen px a pixel). Buildings of several materials (brick, concrete with its form-tie holes, wood
   slats, tiles, corrugated metal, stucco, a glass office), each floor with its windows (lit warm or cool, curtains,
   blinds, a figure, a television, plants, washing) or its balcony, a shop on its ground floor (a konbini, an izakaya,
   a ramen counter, a shutter half open, an entrance with its bicycles, vending machines, a bar); between buildings the
   night sky (stars, the moon, a far skyline and its aviation lights) over their roofs (water tanks, aerials, fences,
   stair huts, utility poles and their wires). Every light lights the wall round it, dithered as the street is.
   The still part is drawn once per layout; only what moves is drawn each frame (12 a second, only while seen; nothing
   moves under reduced motion). The content keeps its ground: the walls fade toward it (site.css, .wall). */
(function () {
  const pg = document.querySelector('.page'), ct = pg && pg.querySelector(':scope > .container');
  if (!ct || !window.HTMLCanvasElement) return;
  const still = matchMedia('(prefers-reduced-motion: reduce)').matches, P = 2;
  // the places of the timeline, as lit signs on the walls, in its order down the page (left, right, left…): their
  // faces are pixel versions of the official logos (assets/wall_logos.png; its map below)
  const LOGO_MAP = { airbus: [0, 0, 54, 14], thales: [0, 15, 60, 12], inria: [0, 28, 56, 20], mpg: [0, 49, 48, 46], imt: [0, 96, 42, 16], gatech: [0, 113, 34, 21], ellis: [0, 135, 46, 13] };
  const LOGOS = [['imt', 0.10, 'left'], ['thales', 0.22, 'right'], ['airbus', 0.35, 'left'], ['gatech', 0.48, 'right'], ['mpg', 0.62, 'left'], ['ellis', 0.73, 'right'], ['inria', 0.86, 'left']];
  const atlas = { ok: false, d: null, W: 0 };
  const me = document.currentScript && document.currentScript.src;
  function rnd(seed) { let h = 2166136261; for (const c of String(seed)) { h ^= c.charCodeAt(0); h = Math.imul(h, 16777619); } return () => { h ^= h << 13; h ^= h >>> 17; h ^= h << 5; return ((h >>> 0) % 1e6) / 1e6; }; }
  const C = (s) => [parseInt(s.slice(1, 3), 16), parseInt(s.slice(3, 5), 16), parseInt(s.slice(5, 7), 16)];
  const mix = (a, b, k) => [a[0] + (b[0] - a[0]) * k, a[1] + (b[1] - a[1]) * k, a[2] + (b[2] - a[2]) * k];
  const BAY = [0, 8, 2, 10, 12, 4, 14, 6, 3, 11, 1, 9, 15, 7, 13, 5].map((v) => (v + 0.5) / 16);
  const noise = (x, y, s) => { const v = Math.sin(x * 12.9898 + y * 78.233 + s * 37.719) * 43758.5453; return v - Math.floor(v); };
  const css = (c, a) => `rgba(${c[0] | 0},${c[1] | 0},${c[2] | 0},${a == null ? 1 : a})`;

  // ---- the still layers: colour (with alpha) and light (opaque black, screen-blended, blurred: the glow)
  function Layer(W, H, opaque) {
    const d = new Uint8ClampedArray(W * H * 4); if (opaque) for (let i = 3; i < d.length; i += 4) d[i] = 255;
    return { W, H, d,
      px(x, y, c, a) { x |= 0; y |= 0; if (x < 0 || y < 0 || x >= W || y >= H) return; const i = (y * W + x) * 4, k = a == null ? 1 : a, b = 1 - k; d[i] = d[i] * b + c[0] * k; d[i + 1] = d[i + 1] * b + c[1] * k; d[i + 2] = d[i + 2] * b + c[2] * k; d[i + 3] = Math.max(d[i + 3], 255 * k); },
      add(x, y, c, a) { x |= 0; y |= 0; if (x < 0 || y < 0 || x >= W || y >= H) return; const i = (y * W + x) * 4, k = a == null ? 1 : a; d[i] += c[0] * k; d[i + 1] += c[1] * k; d[i + 2] += c[2] * k; },
      rect(x, y, w, h, c, a) { for (let yy = 0; yy < h; yy++) for (let xx = 0; xx < w; xx++) this.px(x + xx, y + yy, c, a); } };
  }

  // ---- palettes
  const NEON = ['#ff8ad1', '#5ee6ff', '#ffc36b', '#9d7bff', '#ff7a63', '#3ee08a'].map(C);
  const WARM = C('#ffcf8a'), WARM2 = C('#ff9f6a'), COOL = C('#d4ecff'), COOL2 = C('#9fc4ff');
  const INK = C('#07060f'), DARK = C('#100d1f'), FRAME = [C('#4a4660'), C('#3a2a22'), C('#6a6680'), C('#2c2846')];
  const PICT = {
    bowl: ['.#..#..', '..#..#.', '#######', '#.....#', '.#...#.', '..###..'],
    cup: ['.#.#..', '#.#...', '......', '#####.', '#...##', '#...#.', '.###..'],
    heart: ['.##.##.', '#######', '#######', '.#####.', '..###..', '...#...'],
    star: ['...#...', '..###..', '#######', '.#####.', '.##.##.', '#.....#'],
    note: ['..####', '..#..#', '..#..#', '..#..#', '###.##', '##.###'],
    cat: ['#...#', '##.##', '#####', '#.#.#', '#####', '.###.'],
    fish: ['..##...', '.####.#', '#.#####', '.####.#', '..##...'],
    moon: ['.###.', '##...', '#....', '##...', '.###.'] };
  const MATS = {
    brick: { base: [C('#8a4a46'), C('#7a4a5a'), C('#6a4048'), C('#8a5a48')], f(x, y, s, b) {
      const row = Math.floor(y / 3), off = row % 2 ? 3 : 0, bx = Math.floor((x + off) / 6), id = noise(bx, row, s);
      if (y % 3 === 2 || (x + off) % 6 === 5) return mix(b, [58, 48, 56], 0.75);
      const k = 0.82 + id * 0.3 + (noise(x, y, s) - 0.5) * 0.08; return id > 0.93 ? mix(b, [40, 30, 34], 0.5) : [b[0] * k, b[1] * k, b[2] * k]; } },
    concrete: { base: [C('#8c8a98'), C('#8a8290'), C('#7e8290')], f(x, y, s, b) {
      if (x % 32 === 31 || y % 24 === 23) return mix(b, [60, 58, 72], 0.6);
      if (x % 8 === 4 && y % 8 === 4) return mix(b, [50, 48, 60], 0.7);
      const k = 0.92 + (noise(x, y, s) - 0.5) * 0.12 + (noise(x >> 3, y >> 3, s) - 0.5) * 0.1; return [b[0] * k, b[1] * k, b[2] * k]; } },
    wood: { base: [C('#6a4630'), C('#5a3a2a'), C('#74503a')], f(x, y, s, b) {
      if (x % 4 === 3) return mix(b, [26, 16, 12], 0.8);
      const k = 0.85 + noise(x >> 2, 0, s) * 0.2 + (noise(x, y >> 2, s) - 0.5) * 0.12; return [b[0] * k, b[1] * k, b[2] * k]; } },
    tile: { base: [C('#6e8e8a'), C('#a89878'), C('#8a7aa0'), C('#7a8aa0')], f(x, y, s, b) {
      if (x % 4 === 3 || y % 3 === 2) return mix(b, [70, 70, 80], 0.55);
      const k = 0.9 + (noise(x >> 2, Math.floor(y / 3), s) - 0.5) * 0.18; return [b[0] * k, b[1] * k, b[2] * k]; } },
    metal: { base: [C('#6a7488'), C('#74708a')], f(x, y, s, b) {
      const k = [0.72, 0.95, 1.12, 0.95][x % 4], rust = noise(x >> 2, 3, s) > 0.86 ? Math.max(0, 1 - ((y + noise(x, 0, s) * 40) % 60) / 60) : 0;
      return mix([b[0] * k, b[1] * k, b[2] * k], [138, 90, 58], rust * 0.6); } },
    stucco: { base: [C('#9c8c98'), C('#8a8aa0'), C('#a08a80')], f(x, y, s, b) {
      const k = 0.9 + (noise(x, y, s) - 0.5) * 0.16 + (noise(x >> 4, y >> 4, s) - 0.5) * 0.14; return [b[0] * k, b[1] * k, b[2] * k]; } } };

  // ---- one side: its plan (segments, still drawings, lights, moving parts), then its still layers
  function build(W, H, seed, left, signs) {
    const r = rnd(seed), pick = (a) => a[Math.floor(r() * a.length)], chance = (p) => r() < p;
    const outer = left ? 2 : W - 2, toOuter = (w) => (left ? 3 : W - 3 - w);
    const segs = [], draws = [], lights = [], moving = [];
    const light = (x, y, rad, c, k, down) => lights.push({ x, y, r: rad, c: c.map((v) => v / 255), k, down });
    let y = 0, moon = false, lastShop = '', lastMat = '';
    const sky = (h) => { segs.push({ k: 'sky', y0: y, y1: y + h }); y += h; };
    const pending = signs.filter((sg) => LOGO_MAP[sg.k][2] <= W - 10).sort((a, b) => a.y - b.y);
    const due = (yy) => pending.length && pending[0].y <= yy ? pending.shift() : null;
    sky(56 + Math.floor(r() * 30));
    while (y < H - 40) {
      let mat; do mat = pick(['brick', 'concrete', 'wood', 'tile', 'metal', 'stucco', 'glass', 'concrete', 'brick']); while (mat === lastMat); lastMat = mat;
      const F = 62 + Math.floor(r() * 14), nF = 2 + Math.floor(r() * 3), roof = 6, y0 = y, y1 = Math.min(H, y + roof + nF * F);
      const B = { k: 'bld', mat, y0, y1, base: mat === 'glass' ? C('#141a34') : pick(MATS[mat].base), s: r() * 100, frame: pick(FRAME), wst: pick(['sash', 'slider', 'grid', 'tall']) };
      segs.push(B);
      roofline(B, W);
      if (chance(0.7)) pipe(B, chance(0.5) ? toOuter(2) + (left ? 0 : 0) : (left ? W - 8 : 6));
      for (let f = 0; f < nF; f++) {
        const fy = y0 + roof + f * F, ground = f === nF - 1;
        if (f < nF - 1) draws.push((L) => slab(L, fy + F - 3, W, B));
        if (mat === 'glass') { office(fy, F, W, B); continue; }
        const lg = !ground ? due(fy + F) : null;
        if (lg) { lightbox(lg.k, fy, F, W, B); continue; }
        if (ground) { let shop; do shop = pick(['konbini', 'izakaya', 'ramen', 'shutter', 'entrance', 'vending', 'bar']); while (shop === lastShop); lastShop = shop; storefront(shop, fy, F, W, B); }
        else if (chance(0.3)) balcony(fy, F, W, B);
        else windows(fy, F, W, B, f);
        if (!ground && chance(0.22)) sign(toOuter(12), fy + 6, F * 2 - 16);
      }
      y = y1;
      if (y < H - 60 && chance(0.62)) {                                     // between two buildings: sky, or a scene of the street
        const scene = pick(['', '', 'park', 'shrine', 'train']), h = scene ? 84 + Math.floor(r() * 14) : 46 + Math.floor(r() * 44), gy = y;
        segs.push({ k: 'sky', y0: y, y1: y + h, scene }); y += h;
        const lg = !scene && h >= 60 ? due(y) : null;
        if (lg) billboard(lg.k, gy, h, W);
        else if (!scene && chance(0.5)) pole(gy, h, W);
      }
    }
    if (y < H) segs.push({ k: 'sky', y0: y, y1: H, scene: '' });
    // ---- the parts
    function roofline(B, W) {
      draws.push((L) => { L.rect(0, B.y0, W, 6, [30, 25, 52]); L.rect(0, B.y0, W, 1, [96, 88, 140], 0.8); L.rect(0, B.y0 + 5, W, 1, [12, 10, 24]); });
    }
    function slab(L, yy, W, B) {                                       // the line between two floors
      const c = B.mat === 'wood' ? [34, 22, 18] : [22, 18, 40]; for (let x = 0; x < W; x++) { L.px(x, yy, c, 0.75); L.px(x, yy + 1, c, 0.45); L.px(x, yy + 2, [255, 255, 255], 0.05); }
    }
    function pipe(B, x) {
      draws.push((L) => { for (let yy = B.y0 + 6; yy < B.y1; yy++) { L.px(x, yy, [44, 38, 70]); L.px(x + 1, yy, [70, 62, 104]); L.px(x + 2, yy, [30, 26, 50]); if ((yy - B.y0) % 24 === 0) { L.rect(x - 1, yy, 5, 2, [56, 50, 90]); } } });
    }
    function stains(x, yy, w, len) {
      draws.push((L) => { for (let xx = 0; xx < w; xx++) { const n = len * (0.3 + noise(x + xx, yy, 5) * 0.7); for (let k = 0; k < n; k++) L.px(x + xx, yy + k, [10, 8, 20], 0.22 * (1 - k / n)); } });
    }
    function windows(fy, F, W, B, f) {
      const m = W > 84 ? 3 : W > 50 ? 2 : 1, ww = B.wst === 'tall' ? 16 : 20 + Math.floor(r() * 4), wh = B.wst === 'tall' ? 36 : 28 + Math.floor(r() * 4);
      const gap = (W - m * ww) / (m + 1);
      for (let k = 0; k < m; k++) {
        const x = Math.round(gap + k * (ww + gap)), yy = fy + 12;
        const state = pick(['dark', 'dark', 'warm', 'warm', 'warm', 'cool', 'curtain', 'blinds', 'person', 'tv', 'toggle']);
        stains(x, yy + wh + 3, ww, 10 + r() * 14);
        win(x, yy, ww, wh, B, state, k);
      }
      if (chance(0.25)) laundryPole(fy + 6, W);
    }
    function win(x, yy, ww, wh, B, state, k) {
      const cur = pick(['#c77be8', '#ff8ad1', '#5ee6ff', '#ffc36b', '#3ee08a', '#e8e3f2']).slice(), curC = C(cur), sill = pick(['', '', 'plants', 'cat', 'pots', 'grille']);
      const glassDraw = (L, G, st, tt) => glass(L, G, x, yy, ww, wh, B, st, curC, tt);
      draws.push((L, G) => {
        L.rect(x - 1, yy - 3, ww + 2, 2, mix(B.base, [255, 255, 255], 0.15).map((v) => v * 0.3));         // lintel
        L.rect(x - 1, yy - 1, ww + 2, wh + 2, B.frame); L.rect(x + ww + 1, yy, 1, wh + 2, [8, 6, 16], 0.6);   // frame, its shadow
        if (state !== 'tv' && state !== 'toggle') glassDraw(L, G, state, 0);
        L.rect(x - 3, yy + wh + 1, ww + 6, 2, [70, 62, 104]); L.rect(x - 3, yy + wh + 1, ww + 6, 1, [130, 122, 170]); L.rect(x - 3, yy + wh + 3, ww + 6, 1, [8, 6, 16], 0.5);   // sill
        if (sill === 'plants' || sill === 'pots') for (let p = 0; p < (sill === 'pots' ? 3 : 2); p++) {
          const px = x + 2 + p * Math.floor((ww - 6) / 2), pc = pick([C('#ff7a63'), C('#8a5a3a'), C('#5a6a8a')]);
          L.rect(px, yy + wh - 3, 5, 4, pc); L.rect(px, yy + wh - 3, 5, 1, mix(pc, [255, 255, 255], 0.3));
          for (let q = 0; q < 9; q++) L.px(px + 2 + Math.round((noise(px, q, 1) - 0.5) * 6), yy + wh - 4 - Math.floor(noise(q, px, 2) * 6), noise(q, px, 3) > 0.8 ? pick(NEON) : pick([C('#2fae6c'), C('#3ee08a'), C('#1f7a4c')]));
        }
        if (sill === 'grille') { for (let gx = x + 1; gx < x + ww; gx += 3) L.rect(gx, yy, 1, wh, [20, 18, 34]); L.rect(x, yy + Math.floor(wh / 2), ww, 1, [20, 18, 34]); }
        if (sill === 'cat') bmp(L, ['#.#....', '###....', '###...#', '#####.#', '######.', '######.'], x + 3, yy + wh - 5, INK);
      });
      if (state === 'warm' || state === 'person' || state === 'curtain' || state === 'blinds') light(x + ww / 2, yy + wh, 30, state === 'curtain' ? mix(curC, WARM, 0.5) : WARM, 0.85, true);
      if (state === 'cool') light(x + ww / 2, yy + wh, 30, COOL, 0.7, true);
      if (state === 'tv') { light(x + ww / 2, yy + wh, 22, COOL2, 0.35, true); moving.push({ k: 'tv', draw: (D, t) => D.glassNow((L, G) => glassDraw(L, G, 'tv', t)) }); }
      if (state === 'toggle') { const ph = r() * 40, per = 14 + r() * 20; moving.push({ k: 'toggle', draw: (D, t) => D.glassNow((L, G) => glassDraw(L, G, Math.floor((t + ph) / per) % 2 ? 'warm' : 'dark', t)) }); }
      if (sill === 'cat') { const ph = r() * 9; moving.push({ k: 'eyes', draw: (D, t) => { if (Math.floor(t * 2 + ph) % 11) { D.E(x + 4, yy + wh - 4, 1, 1, C('#ffc36b')); D.E(x + 6, yy + wh - 4, 1, 1, C('#ffc36b')); } } }); }
    }
    function glass(L, G, x, yy, ww, wh, B, st, curC, t) {
      if (st === 'dark') {
        for (let j = 0; j < wh; j++) for (let i = 0; i < ww; i++) L.px(x + i, yy + j, (i + j * 2) % 23 < 2 ? [42, 40, 80] : mix([16, 14, 34], [24, 22, 46], j / wh));
        L.rect(x + 1, yy + 1, 3, wh - 2, [30, 26, 54]);
      } else if (st === 'tv') {
        const k = 0.5 + 0.5 * Math.abs(Math.sin(t * 3.1) * Math.sin(t * 7.3)), c = mix(C('#3a6ad8'), C('#9fd0ff'), k);
        for (let j = 0; j < wh; j++) for (let i = 0; i < ww; i++) { const v = mix([18, 18, 40], c, (j / wh) * 0.6 + 0.2); L.px(x + i, yy + j, v); G.add(x + i, yy + j, c, 0.25); }
      } else if (st === 'curtain') {
        for (let j = 0; j < wh; j++) for (let i = 0; i < ww; i++) { const fold = (i % 4 === 0 ? 0.7 : i % 4 === 2 ? 1.08 : 0.92), c = mix(curC, WARM, 0.35).map((v) => v * fold * (0.82 + 0.18 * j / wh)); L.px(x + i, yy + j, c); G.add(x + i, yy + j, c, 0.32); }
      } else if (st === 'blinds') {
        for (let j = 0; j < wh; j++) for (let i = 0; i < ww; i++) { const c = j % 3 === 2 ? [40, 30, 40] : mix(WARM, WARM2, j / wh); L.px(x + i, yy + j, c); if (j % 3 !== 2) G.add(x + i, yy + j, c, 0.3); }
      } else {                                                             // warm, cool, person
        const a = st === 'cool' ? COOL : WARM, b = st === 'cool' ? COOL2 : WARM2;
        for (let j = 0; j < wh; j++) for (let i = 0; i < ww; i++) { const c = mix(a, b, (j / wh) + (BAY[(i & 3) + ((j & 3) << 2)] - 0.5) * 0.2); L.px(x + i, yy + j, c); G.add(x + i, yy + j, c, 0.42); }
        L.rect(x, yy, 4, wh, curC.map((v) => v * 0.8)); L.rect(x + ww - 3, yy, 3, wh, curC.map((v) => v * 0.7));                    // the curtains, drawn aside
        L.rect(x + 5, yy + 2, ww - 9, 1, [255, 255, 255], 0.35);                                                                       // the ceiling light's reflection
        if (st === 'person') bmp(L, ['..###..', '.#####.', '.#####.', '..###..', '.#####.', '#######', '#######', '#######'], x + Math.floor(ww / 2) - 3, yy + wh - 8, [30, 18, 30]);
        else if (st === 'warm') { L.rect(x + ww - 9, yy + wh - 7, 4, 7, [60, 34, 30], 0.8); L.rect(x + ww - 10, yy + wh - 9, 6, 2, [255, 236, 190]); G.add(x + ww - 10, yy + wh - 9, [255, 236, 190], 0.6); }   // a lamp
      }
      // the window's bars
      L.rect(x, yy + Math.floor(wh * 0.55), ww, 1, B.frame);
      if (B.wst === 'sash' || B.wst === 'grid') L.rect(x + Math.floor(ww / 2), yy, 1, wh, B.frame);
      if (B.wst === 'grid') { L.rect(x + Math.floor(ww / 4), yy, 1, wh, B.frame); L.rect(x + Math.floor(3 * ww / 4), yy, 1, wh, B.frame); L.rect(x, yy + Math.floor(wh * 0.25), ww, 1, B.frame); }
      if (B.wst === 'slider') { L.rect(x + Math.floor(ww / 2), yy, 2, wh, B.frame); for (let j = Math.floor(wh * 0.55) + 1; j < wh; j++) for (let i = 0; i < ww; i++) if ((i + j) % 2) L.px(x + i, yy + j, [255, 255, 255], 0.08); }
    }
    function laundryPole(yy, W) {
      const cl = [0, 1, 2, 3, 4].map(() => pick(['#ff8ad1', '#5ee6ff', '#ffc36b', '#e8e3f2', '#9d7bff', '#3ee08a', '#ff7a63']).slice());
      draws.push((L) => {
        L.rect(2, yy, W - 4, 1, [140, 134, 170]); L.rect(2, yy - 1, 1, 3, [90, 84, 120]); L.rect(W - 3, yy - 1, 1, 3, [90, 84, 120]);
        cl.forEach((c, j) => { const x = 6 + j * Math.floor((W - 14) / 5), col = C(c).map((v) => v * 0.55), kind = j % 3;
          if (kind === 0) { L.rect(x, yy + 1, 7, 3, col); L.rect(x + 1, yy + 4, 5, 6, col); }                                   // a shirt
          else if (kind === 1) { L.rect(x, yy + 1, 5, 9, col); for (let q = 0; q < 9; q += 3) L.rect(x, yy + 1 + q, 5, 1, col.map((v) => v * 1.25)); }   // a towel
          else { L.rect(x, yy + 1, 2, 4, col); L.rect(x + 3, yy + 1, 2, 4, col); } });                                    // socks
      });
    }
    function balcony(fy, F, W, B) {
      const lit = chance(0.55), st = lit ? pick(['warm', 'curtain', 'cool']) : 'dark', curC = C(pick(['#c77be8', '#5ee6ff', '#ffc36b']));
      const dy = fy + 10, dh = F - 20, dx = 6, dw = W - 12;
      draws.push((L, G) => {
        L.rect(dx - 1, dy - 1, dw + 2, dh + 2, B.frame); glass(L, G, dx, dy, dw, dh, Object.assign({}, B, { wst: 'slider' }), st, curC, 0);
        const sy = fy + F - 12;
        L.rect(0, sy, W, 4, [36, 30, 60]); L.rect(0, sy, W, 1, [110, 102, 150]); L.rect(0, sy + 4, W, 2, [8, 6, 16], 0.6);      // the slab
        const panel = chance(0.5);
        for (let x = 1; x < W - 1; x++) { if (panel) { L.px(x, sy - 9, [90, 84, 120]); for (let j = sy - 8; j < sy; j++) L.px(x, j, [180, 190, 220], 0.16); } else { L.px(x, sy - 9, [70, 64, 100]); if (x % 3 === 0) for (let j = sy - 8; j < sy; j++) L.px(x, j, [26, 22, 44]); } }
        if (chance(0.5)) { const fx = 8 + Math.floor(r() * (W - 30)), fc = C(pick(['#e8e3f2', '#ff8ad1', '#5ee6ff'])).map((v) => v * 0.5); L.rect(fx, sy - 10, 18, 9, fc); for (let q = 0; q < 18; q += 3) L.rect(fx + q, sy - 7, 1, 1, fc.map((v) => v * 1.5)); }   // a futon airing
        for (let p = 0; p < 2 + Math.floor(r() * 3); p++) { const px = 3 + Math.floor(r() * (W - 8)); for (let q = 0; q < 8; q++) L.px(px + Math.round((noise(px, q, 7) - 0.5) * 5), sy - 9 - Math.floor(noise(q, px, 8) * 4), pick([C('#2fae6c'), C('#3ee08a')])); }
      });
      if (lit) light(W / 2, fy + F - 14, 34, st === 'cool' ? COOL : WARM, 0.8, true);
      if (chance(0.6)) laundryPole(fy + 6, W);
    }
    function sign(x, yy, h) {
      const n = Math.max(2, Math.min(5, Math.floor((h - 6) / 10))), picts = Array.from({ length: n }, () => pick(Object.keys(PICT))), c = pick(NEON), ph = r() * 9;
      const hh = 6 + n * 10;
      draws.push((L) => { L.rect(x + 2, yy - 4, 2, 4, [60, 54, 90]); L.rect(x + 8, yy - 4, 2, 4, [60, 54, 90]); L.rect(x, yy, 12, hh, [12, 10, 26]); L.rect(x + 12, yy + 1, 1, hh, [6, 4, 12], 0.6); });
      light(x + 6, yy + hh / 2, 40, c, 0.9, false);
      moving.push({ k: 'neon', draw: (D, t) => {
        const off = !still && noise(Math.floor(t * 12), ph, 3) < 0.035;
        const tube = (xx, y2, w, h2) => off ? D.R(xx, y2, w, h2, [60, 56, 80]) : D.E(xx, y2, w, h2, c);
        tube(x, yy, 12, 1); tube(x, yy + hh - 1, 12, 1); tube(x, yy, 1, hh); tube(x + 11, yy, 1, hh);
        picts.forEach((pk, j) => { const rows = PICT[pk]; D.bmp(rows, x + 2 + ((8 - rows[0].length) >> 1), yy + 4 + j * 10, off ? [60, 56, 80] : c, !off); });
      } });
    }
    function office(fy, F, W, B) {                                       // a glass office floor: its spandrel, its ribbon of panes
      const seed = r() * 100;
      draws.push((L, G) => {
        const sp = 9;                                                      // the spandrel band at the floor's foot
        for (let j = 0; j < F - 3; j++) for (let i = 0; i < W; i++) {
          const yy = fy + j, pane = Math.floor(i / 8), mull = i % 8 === 0;
          if (j >= F - 3 - sp) { L.px(i, yy, j === F - 3 - sp ? [70, 80, 120] : mix([22, 26, 48], [14, 16, 32], (j - (F - 3 - sp)) / sp)); continue; }
          if (mull) { L.px(i, yy, [46, 54, 84]); continue; }
          const lit = noise(pane, fy, seed) > 0.62, warm = noise(pane, fy + 1, seed) > 0.55, depth = j / (F - 3 - sp);
          let c;
          if (lit) {
            c = mix(warm ? C('#d8c6a8') : C('#a8bee0'), warm ? C('#8a7a6a') : C('#5a6e98'), depth * 0.9);
            if (j === 2) c = warm ? [255, 238, 210] : [230, 242, 255];                                    // the ceiling's light
            if (j > (F - 3 - sp) - 8 && (i % 8) > 2 && (i % 8) < 6 && noise(pane, fy + 2, seed) > 0.5) c = [30, 30, 46];   // a desk, a chair
            if (j === (F - 3 - sp) - 9 && (i % 8) === 4 && noise(pane, fy + 3, seed) > 0.4) c = [120, 230, 255];          // a screen
            G.add(i, yy, c, 0.16);
          } else {
            const refl = ((i + j * 0.7 + fy) % 46) < 3 ? 0.5 : 0;
            c = mix(mix([14, 18, 40], [26, 32, 62], depth), [80, 96, 150], refl);
          }
          L.px(i, yy, c);
        }
      });
      light(W / 2, fy + F / 2, 46, COOL2, 0.18, false);
    }
    function face(L, G, k, x0, y0) {                                     // the logo's face from the atlas, lit
      const [ax, ay, w, h] = LOGO_MAP[k];
      for (let j = 0; j < h; j++) for (let i = 0; i < w; i++) {
        const q = ((ay + j) * atlas.W + ax + i) * 4, c = [atlas.d[q], atlas.d[q + 1], atlas.d[q + 2]];
        L.px(x0 + i, y0 + j, c); G.add(x0 + i, y0 + j, c, (c[0] + c[1] + c[2]) > 600 ? 0.32 : 0.55);
      }
      return [w, h];
    }
    function avgColour(k) {
      const [ax, ay, w, h] = LOGO_MAP[k], t = [0, 0, 0]; let n = 0;
      for (let j = 0; j < h; j++) for (let i = 0; i < w; i++) { const q = ((ay + j) * atlas.W + ax + i) * 4; t[0] += atlas.d[q]; t[1] += atlas.d[q + 1]; t[2] += atlas.d[q + 2]; n++; }
      return t.map((v) => v / n);
    }
    function lightbox(k, fy, F, W, B) {                                   // a lightbox sign on a floor, on two brackets
      const [, , w, h] = LOGO_MAP[k], x0 = Math.round((W - w) / 2), y0 = fy + Math.round((F - 3 - h) / 2) + 2;
      draws.push((L, G) => {
        L.rect(x0 - 2, y0 - 2, w + 4, h + 4, [22, 20, 36]); L.rect(x0 - 2, y0 - 2, w + 4, 1, [92, 88, 120]);   // the case, its lit edge
        L.rect(x0 + 3, y0 - 5, 2, 3, [60, 56, 84]); L.rect(x0 + w - 5, y0 - 5, 2, 3, [60, 56, 84]);          // the brackets
        L.rect(x0 - 1, y0 + h + 2, w + 2, 1, [8, 6, 16], 0.6);                                                // its shadow
        face(L, G, k, x0, y0);
      });
      light(W / 2, y0 + h / 2, Math.max(30, w * 0.75), avgColour(k), 0.55, false);
    }
    function billboard(k, gy, h, W) {                                     // a sign on the roof below a gap of sky, its legs, its lamps
      const [, , w, hh] = LOGO_MAP[k], base = gy + h, x0 = Math.round((W - w) / 2), y0 = base - hh - 12;
      draws.push((L, G) => {
        for (const lx of [x0 + 4, x0 + w - 6]) { L.rect(lx, y0 + hh + 2, 2, base - y0 - hh - 2, [44, 40, 66]); for (let j = y0 + hh + 4; j < base; j += 4) L.px(lx + (j % 8 ? 0 : 1), j, [70, 66, 96]); }
        L.rect(x0 - 3, y0 + hh + 2, w + 6, 1, [70, 66, 96]);                                                  // the catwalk
        L.rect(x0 - 2, y0 - 2, w + 4, hh + 4, [22, 20, 36]); L.rect(x0 - 2, y0 - 2, w + 4, 1, [92, 88, 120]);
        face(L, G, k, x0, y0);
        for (const lx of [x0 + 2, x0 + w - 4]) { L.rect(lx, y0 - 5, 3, 2, [60, 56, 84]); L.px(lx + 1, y0 - 3, [255, 236, 190]); G.add(lx + 1, y0 - 3, [255, 236, 190], 0.9); }
      });
      light(W / 2, y0 + hh / 2, Math.max(30, w * 0.7), avgColour(k), 0.45, false);
    }
    function storefront(shop, fy, F, W, B) {
      const gy = fy + F - 3;                                              // the ground under the shop
      if (shop === 'konbini') {
        const band = [C('#3a8fd8'), C('#f4efe9'), pick([C('#2fae6c'), C('#ff7a3a'), C('#e8314a')])];
        draws.push((L, G) => {
          for (let i = 0; i < 3; i++) { L.rect(2, fy + 8 + i * 2, W - 4, 2, band[i]); for (let x = 2; x < W - 2; x++) G.add(x, fy + 8 + i * 2, band[i], 0.25); }
          const x0 = 4, y0 = fy + 16, w = W - 8, h = gy - y0;
          for (let j = 0; j < h; j++) for (let i = 0; i < w; i++) { const c = mix(C('#f2f8ff'), C('#c8dcf6'), j / h); L.px(x0 + i, y0 + j, c); G.add(x0 + i, y0 + j, c, 0.35); }
          for (let s = 0; s < 3; s++) { const sy = y0 + 6 + s * 9; L.rect(x0 + 2, sy + 4, w - 4, 1, [150, 160, 190]); for (let i = x0 + 3; i < x0 + w - 3; i += 2) L.rect(i, sy, 1, 4, pick(NEON).map((v) => v * 0.85)); }
          L.rect(x0 + Math.floor(w * 0.62), y0, 1, h, [120, 130, 160]); bmp(L, ['.##.', '####', '.##.', '####', '####', '####', '.#.#', '.#.#'], x0 + Math.floor(w * 0.3), gy - 9, [40, 36, 60]);
        });
        light(W / 2, fy + F - 10, 70, COOL, 1.1, false);
      } else if (shop === 'izakaya') {
        const nc = pick([C('#283a8f'), C('#8f2338'), C('#3a2a6f')]);
        draws.push((L, G) => {
          for (let j = fy + 6; j < gy; j++) for (let i = 0; i < W; i++) L.px(i, j, MATS.wood.f(i, j, 3, [70, 46, 32]).map((v) => v * 0.35));
          const w = Math.min(W - 16, 34), x0 = Math.floor((W - w) / 2), y0 = fy + 22, h = gy - y0;
          for (let j = 0; j < h; j++) for (let i = 0; i < w; i++) { const lat = i % 6 === 0 || j % 6 === 0, c = lat ? [90, 60, 44] : mix(C('#ffe2b0'), C('#ffc58a'), j / h); L.px(x0 + i, y0 + j, c); if (!lat) G.add(x0 + i, y0 + j, c, 0.35); }
          L.rect(x0 - 2, fy + 14, w + 4, 1, [70, 64, 100]); for (let x = x0 - 1; x < x0 + w + 1; x += 7) L.rect(x, fy + 15, 6, 12, nc);
          const cx = Math.floor(W / 2); for (let a = 0; a < 6.3; a += 0.3) L.px(cx + Math.round(Math.cos(a) * 3), fy + 20 + Math.round(Math.sin(a) * 3), [240, 236, 230]);
          L.rect(W - 12, gy - 12, 8, 10, [24, 20, 30]); for (let q = 0; q < 4; q++) L.rect(W - 11, gy - 10 + q * 2, 3 + Math.floor(noise(q, fy, 4) * 4), 1, pick([C('#ffc36b'), C('#f4efe9'), C('#ff8ad1')]));   // a menu stand, its chalk strokes
        });
        light(W / 2, fy + F - 14, 50, WARM, 1, false);
        for (const lx of [4, W - 13]) lantern(lx, fy + 6, 'red');
      } else if (shop === 'ramen') {
        draws.push((L, G) => {
          for (let j = 0; j < 9; j++) for (let i = 0; i < W; i++) L.px(i, fy + 8 + j, ((i + j) >> 1) % 2 ? [200, 40, 50] : [236, 226, 214]);
          L.rect(0, fy + 17, W, 1, [10, 6, 14]);
          const y0 = fy + 22, h = 16; for (let j = 0; j < h; j++) for (let i = 4; i < W - 4; i++) { const c = mix(WARM, WARM2, j / h); L.px(i, y0 + j, c); G.add(i, y0 + j, c, 0.4); }
          bmp(L, ['.###.', '#####', '#####', '.###.', '#####', '#####'], Math.floor(W / 2) - 2, y0 + h - 6, [40, 20, 24]); L.rect(Math.floor(W / 2) - 3, y0 - 1, 7, 2, [240, 240, 240]);   // the cook, his hat
          L.rect(2, y0 + h, W - 4, 3, [90, 50, 36]); L.rect(2, y0 + h, W - 4, 1, [160, 100, 70]);
          for (let x = 8; x < W - 8; x += 10) { L.rect(x, gy - 7, 5, 2, [220, 60, 60]); L.rect(x + 2, gy - 5, 1, 5, [50, 44, 70]); }
        });
        light(W / 2, fy + 32, 50, WARM, 1, false);
        lantern(W - 13, fy + 22, 'red');
        const sx = Math.floor(W / 2); moving.push({ k: 'steam', draw: (D, t) => { for (let q = 0; q < 3; q++) { const u = ((t * 0.4 + q / 3) % 1), px = sx + Math.round(Math.sin(u * 7 + q) * 2), py = fy + 30 - Math.round(u * 16); D.R(px, py, 2 + (u > 0.5 ? 1 : 0), 2, [240, 236, 250], (1 - u) * 0.5); } } });
      } else if (shop === 'shutter') {
        const open = chance(0.6), oh = open ? 6 : 0;
        draws.push((L, G) => {
          const x0 = 3, w = W - 6, y0 = fy + 14, h = gy - y0 - oh;
          L.rect(x0 - 1, y0 - 3, w + 2, 3, [60, 56, 84]);
          for (let j = 0; j < h; j++) for (let i = 0; i < w; i++) L.px(x0 + i, y0 + j, j % 2 ? [74, 72, 92] : [104, 102, 124]);
          for (let q = 0; q < 6; q++) { const tx = x0 + 4 + Math.floor(noise(q, fy, 1) * (w - 10)), ty = y0 + 4 + Math.floor(noise(fy, q, 2) * (h - 8)); L.rect(tx, ty, 3 + Math.floor(noise(q, q, 3) * 6), 1, pick(NEON).map((v) => v * 0.6)); }   // a few painted strokes
          if (open) for (let j = 0; j < oh; j++) for (let i = 0; i < w; i++) { const c = mix(WARM, WARM2, j / oh); L.px(x0 + i, gy - oh + j, c); G.add(x0 + i, gy - oh + j, c, 0.5); }
          L.rect(W - 9, fy + 10, 3, 2, [255, 236, 190]); G.add(W - 9, fy + 10, [255, 236, 190], 0.8);
        });
        if (open) light(W / 2, gy, 40, WARM, 0.9, false);
        light(W - 8, fy + 11, 22, WARM, 0.7, false);
        if (chance(0.6)) bike(6 + Math.floor(r() * (W - 30)), gy);
      } else if (shop === 'entrance') {
        draws.push((L, G) => {
          const w = Math.min(28, W - 30), x0 = left ? W - w - 6 : 6, y0 = fy + 16, h = gy - y0;
          L.rect(x0 - 2, y0 - 2, w + 4, h + 2, [40, 36, 60]);
          for (let j = 0; j < h; j++) for (let i = 0; i < w; i++) { const c = mix(COOL, COOL2, j / h); L.px(x0 + i, y0 + j, c); G.add(x0 + i, y0 + j, c, 0.3); }
          L.rect(x0 + Math.floor(w / 2), y0, 1, h, [60, 70, 100]);
          L.rect(x0 + 4, y0 - 6, w - 8, 2, [255, 245, 220]); G.add(x0 + 4, y0 - 6, [255, 245, 220], 0.8);
          const mx = left ? 6 : W - 20; for (let a = 0; a < 3; a++) for (let b = 0; b < 3; b++) { L.rect(mx + a * 5, y0 + 2 + b * 4, 4, 3, [120, 116, 140]); L.rect(mx + a * 5 + 1, y0 + 3 + b * 4, 2, 1, [40, 36, 60]); }   // the letterboxes
        });
        light(left ? W - 20 : 20, fy + F - 12, 48, COOL, 0.8, false);
        bike(left ? 4 : W - 26, gy); if (W > 70) bike(left ? 24 : W - 46, gy);
      } else if (shop === 'vending') {
        const m = Math.max(1, Math.min(4, Math.floor((W - 6) / 19)));
        for (let k = 0; k < m; k++) vend(4 + k * 19, gy - 34);
        draws.push((L) => { const bx = 4 + m * 19; if (bx + 8 < W) { L.rect(bx, gy - 9, 7, 9, [60, 90, 140]); L.rect(bx + 1, gy - 9, 5, 2, [20, 30, 50]); } });
      } else if (shop === 'bar') {
        draws.push((L, G) => {
          const x0 = left ? W - 22 : 6, y0 = fy + 22;
          L.rect(x0, y0, 16, gy - y0, [22, 16, 26]); L.rect(x0 + 1, y0 + 1, 14, gy - y0 - 1, [44, 26, 30]); L.rect(x0 + 12, y0 + 12, 2, 2, [200, 170, 120]);
          for (let s = 0; s < 6; s++) L.rect(left ? 4 + s * 3 : W - 22 + s * 3, gy - 2 - s * 2, 4, 1, [70, 64, 100]);
          L.rect(x0 + 6, y0 - 6, 3, 2, [255, 210, 150]); G.add(x0 + 6, y0 - 6, [255, 210, 150], 0.9);
        });
        light(left ? W - 14 : 14, fy + 18, 30, WARM, 0.8, false);
        const c = pick(NEON), pk = pick(Object.keys(PICT)), sx = left ? W - 30 : 26, sy = fy + 8, ph = r() * 9;
        light(sx + 6, sy + 6, 30, c, 0.7, false);
        moving.push({ k: 'neon', draw: (D, t) => { const off = !still && noise(Math.floor(t * 12), ph, 3) < 0.05, cc = off ? [60, 56, 80] : c; D.R(sx, sy, 13, 12, [12, 10, 26]); D.bmp(PICT[pk], sx + 3, sy + 3, cc, !off); } });
      }
    }
    function vend(x, yy) {
      const body = C(pick(['#e8e3f2', '#ff8ad1', '#5ee6ff', '#ffc36b', '#e8314a'])), s = r();
      draws.push((L, G) => {
        L.rect(x, yy, 17, 34, body); L.rect(x + 15, yy, 2, 34, body.map((v) => v * 0.7)); L.rect(x, yy, 17, 1, body.map((v) => Math.min(255, v * 1.2)));
        for (let j = 0; j < 16; j++) for (let i = 0; i < 13; i++) { const c = mix(C('#f4fbff'), C('#cfe8ff'), j / 16); L.px(x + 1 + i, yy + 3 + j, c); G.add(x + 1 + i, yy + 3 + j, c, 0.35); }
        const cans = NEON.concat([C('#e8e3f2')]);
        for (let rr = 0; rr < 3; rr++) { for (let cc = 0; cc < 4; cc++) { const cn = cans[(rr * 4 + cc + Math.floor(s * 7)) % cans.length]; L.rect(x + 2 + cc * 3, yy + 4 + rr * 5, 2, 3, cn); L.px(x + 2 + cc * 3, yy + 4 + rr * 5, [255, 255, 255], 0.6); } L.rect(x + 2, yy + 8 + rr * 5, 12, 1, [150, 160, 190]); for (let cc = 0; cc < 4; cc++) L.px(x + 3 + cc * 3, yy + 8 + rr * 5, [255, 80, 80]); }
        L.rect(x + 2, yy + 22, 9, 2, [30, 30, 50]); L.rect(x + 12, yy + 21, 2, 4, [60, 60, 80]); L.rect(x + 2, yy + 27, 13, 5, [20, 18, 34]); L.rect(x + 3, yy + 28, 11, 1, [60, 56, 80]);
      });
      light(x + 8, yy + 12, 34, COOL, 0.8, false);
    }
    function bike(x, gy) {
      draws.push((L) => {
        const c = C(pick(['#e8314a', '#5ee6ff', '#e8e3f2', '#ffc36b'])).map((v) => v * 0.6), wc = [30, 26, 48];
        for (const cx of [x + 4, x + 16]) for (let a = 0; a < 6.3; a += 0.25) L.px(cx + Math.round(Math.cos(a) * 4), gy - 5 + Math.round(Math.sin(a) * 4), wc);
        for (let i = 0; i <= 12; i++) L.px(x + 4 + i, gy - 5 - Math.round(i * 0.4), c);
        for (let i = 0; i <= 6; i++) { L.px(x + 10 + Math.round(i * 0.5), gy - 5 - i, c); L.px(x + 4 + i, gy - 5 - Math.round(i * 0.9), c); }
        L.rect(x + 9, gy - 12, 4, 1, [20, 18, 30]); L.rect(x + 15, gy - 11, 3, 1, [120, 116, 140]); L.rect(x + 16, gy - 10, 1, 5, c);
        L.rect(x + 14, gy - 13, 6, 3, [30, 26, 48]);                                   // the basket
      });
    }
    function lantern(x, yy, kind) {
      const ph = r() * 6;
      light(x + 4, yy + 9, 26, C('#ff6a4a'), 0.9, false);
      moving.push({ k: 'lantern', draw: (D, t) => {
        const dx = still ? 0 : Math.round(Math.sin(t * 1.3 + ph)), xx = x + dx;
        D.R(x + 4, yy, 1, 3, [60, 54, 90]); D.R(xx + 2, yy + 3, 5, 1, INK);
        for (let j = 0; j < 11; j++) { const w = j === 0 || j === 10 ? 5 : j === 1 || j === 9 ? 7 : 9; D.E(xx + ((9 - w) >> 1), yy + 4 + j, w, 1, j % 2 ? C('#ff4a3a') : C('#ff6a4a')); }
        D.R(xx + 4, yy + 6, 1, 7, [255, 230, 190], 0.6); D.R(xx + 2, yy + 15, 5, 1, INK); D.R(xx + 4, yy + 16, 1, 3, [255, 195, 107]);
      } });
    }
    function pole(gy, h, W) {
      const px = left ? 12 + Math.floor(r() * 10) : W - 18 - Math.floor(r() * 10), top = gy + 6;
      draws.push((L) => {
        for (let yy = top; yy < gy + h; yy++) { L.px(px, yy, [36, 30, 54]); L.px(px + 1, yy, [60, 54, 84]); L.px(px + 2, yy, [26, 22, 40]); }
        L.rect(px - 9, top + 6, 21, 2, [44, 38, 64]); L.rect(px - 6, top + 14, 15, 2, [44, 38, 64]);
        for (const ix of [px - 8, px - 3, px + 5, px + 10]) L.rect(ix, top + 4, 1, 2, [190, 186, 210]);
        L.rect(px + 3, top + 18, 6, 9, [70, 72, 92]); L.rect(px + 3, top + 18, 6, 1, [120, 122, 150]);   // the transformer
        for (const [sx, sy, sag] of [[px - 8, top + 4, 7], [px + 10, top + 4, 6], [px - 6, top + 14, 9]]) {
          const ex = sx < px ? 0 : W; for (let i = 0; i <= Math.abs(ex - sx); i++) { const u = i / Math.max(1, Math.abs(ex - sx)), x = sx + Math.sign(ex - sx) * i; L.px(x, sy + Math.round(4 * sag * u * (1 - u)), INK); }
        }
        if (chance(0.6)) { const cx = left ? px + 18 : px - 22, u = Math.abs(cx - (px + 10)) / Math.max(1, Math.abs((cx < px ? 0 : W) - (px + 10))); bmp(L, ['.##..', '####.', '.###.', '..#..'], cx, top + 4 + Math.round(24 * u * (1 - u)) - 4, INK); }
      });
    }
    // ---- the still layers
    const L = Layer(W, H), G = Layer(W, H, true), Lmap = new Float32Array(W * H * 3);
    for (const sg of segs) {                                                 // the sky, the buildings' materials
      if (sg.k === 'sky') { paintSky(L, G, sg, W, r, moving, () => { if (moon) return false; moon = true; return true; }); if (sg.scene) paintScene(L, G, sg, W, r, moving, left); }
      else if (sg.mat !== 'glass') { const M = MATS[sg.mat]; for (let yy = sg.y0 + 6; yy < sg.y1; yy++) for (let x = 0; x < W; x++) L.px(x, yy, M.f(x, yy - sg.y0, sg.s, sg.base)); }
      else for (let yy = sg.y0 + 6; yy < sg.y1; yy++) for (let x = 0; x < W; x++) L.px(x, yy, [20, 26, 52]);
    }
    for (const l of lights) {                                                // every light, on the wall round it
      const x0 = Math.max(0, Math.floor(l.x - l.r)), x1 = Math.min(W - 1, Math.ceil(l.x + l.r)), y0 = Math.max(0, Math.floor(l.y - l.r)), y1 = Math.min(H - 1, Math.ceil(l.y + l.r * (l.down ? 1.4 : 1)));
      for (let yy = y0; yy <= y1; yy++) for (let x = x0; x <= x1; x++) {
        const dy = yy - l.y, d = Math.hypot(x - l.x, dy < 0 && l.down ? dy * 2.4 : l.down ? dy * 0.7 : dy) / l.r; if (d >= 1) continue;
        const f = (1 - d) * (1 - d) * l.k, i = (yy * W + x) * 3; Lmap[i] += l.c[0] * f; Lmap[i + 1] += l.c[1] * f; Lmap[i + 2] += l.c[2] * f;
      }
    }
    const amb = [0.17, 0.15, 0.29];
    for (const sg of segs) {                                                 // the walls lit and dithered
      if (sg.k !== 'bld' || sg.mat === 'glass') continue;
      for (let yy = sg.y0 + 6; yy < sg.y1; yy++) {
        const rim = Math.max(0, 1 - (yy - sg.y0 - 6) / 10) * 0.12;
        for (let x = 0; x < W; x++) {
          const i = (yy * W + x) * 4, j = (yy * W + x) * 3, b = BAY[(x & 3) + ((yy & 3) << 2)];
          for (let ch = 0; ch < 3; ch++) { const v = L.d[i + ch] * (amb[ch] + rim * (ch === 2 ? 1.4 : 1) + Lmap[j + ch] * 0.95); L.d[i + ch] = Math.min(255, Math.floor(v / 5 + b) * 5); }
        }
      }
    }
    for (const d of draws) d(L, G);
    return { L, G, moving };
  }
  function paintSky(L, G, sg, W, r, moving, takeMoon) {
    const h = sg.y1 - sg.y0, top = C('#0b0920'), bot = C('#2c1d4c'), haze = C('#5a2a5e');
    for (let j = 0; j < h; j++) for (let x = 0; x < W; x++) { const u = j / h, b = BAY[(x & 3) + ((j & 3) << 2)], c = mix(mix(top, bot, Math.min(1, u * 1.2) + (b - 0.5) * 0.06), haze, Math.max(0, u - 0.75) * 1.6); L.px(x, sg.y0 + j, c); }
    for (let s = 0; s < W * h / 140; s++) { const x = Math.floor(r() * W), y = sg.y0 + Math.floor(r() * h * 0.6), k = 0.3 + r() * 0.7; L.px(x, y, [255, 246, 230], k); if (k > 0.85) G.add(x, y, [255, 246, 230], 0.6); }
    for (let s = 0; s < 3; s++) { const x = Math.floor(r() * W), y = sg.y0 + 2 + Math.floor(r() * h * 0.5), ph = r() * 9; moving.push({ k: 'twinkle', draw: (D, t) => { const k = 0.5 + 0.5 * Math.sin(t * 2.3 + ph); D.E(x, y, 1, 1, [255, 246, 230], k); if (k > 0.8) { D.R(x - 1, y, 3, 1, [255, 246, 230], 0.35); D.R(x, y - 1, 1, 3, [255, 246, 230], 0.35); } } }); }
    if (h > 50 && takeMoon()) {                                              // the moon, once a side
      const mx = Math.floor(W * (0.3 + r() * 0.4)), my = sg.y0 + 12, mr = 7;
      for (let j = -mr - 6; j <= mr + 6; j++) for (let i = -mr - 6; i <= mr + 6; i++) { const d = Math.hypot(i, j); if (d <= mr) { const c = mix(C('#fff4dc'), C('#e8d8c0'), Math.max(0, (i + j) / (mr * 2))); const crater = (i - 2) * (i - 2) + (j + 1) * (j + 1) < 4 || (i + 3) * (i + 3) + (j - 3) * (j - 3) < 3; L.px(mx + i, my + j, crater ? c.map((v) => v * 0.86) : c); G.add(mx + i, my + j, [255, 240, 210], 0.5); } else if (d < mr + 6) G.add(mx + i, my + j, [120, 110, 170], 0.25 * (1 - (d - mr) / 6)); }
    }
    let x = 0; const base = sg.y1;                                           // the far skyline
    if (sg.scene) return;
    while (x < W) {
      const w = 6 + Math.floor(r() * 14), bh = 6 + Math.floor(r() * Math.min(30, h * 0.6)), c = [18 + r() * 8, 14 + r() * 6, 38 + r() * 10];
      for (let j = 0; j < bh; j++) for (let i = 0; i < w && x + i < W; i++) L.px(x + i, base - 1 - j, c);
      for (let j = 2; j < bh - 2; j += 3) for (let i = 1; i < w - 1 && x + i < W; i += 2) if (r() < 0.22) { const wc = r() < 0.7 ? [255, 200, 130] : [180, 210, 255]; L.px(x + i, base - 1 - j, wc, 0.75); G.add(x + i, base - 1 - j, wc, 0.25); }
      if (bh > 22 && r() < 0.7) { const ax = x + (w >> 1), ay = base - bh - 1, ph = r() * 2; L.px(ax, ay, [60, 54, 90]); moving.push({ k: 'avi', draw: (D, t) => { if ((t + ph) % 2 < 1) D.E(ax, ay - 1, 1, 1, [255, 40, 40]); } }); }
      x += w + (r() < 0.3 ? 1 + Math.floor(r() * 3) : 0);
    }
    // the roof of the building below (the next segment starts at base): a water tank, aerials, a fence, a stair hut
    const props = [];
    if (r() < 0.7) props.push('tank'); if (r() < 0.6) props.push('aerial'); if (r() < 0.5) props.push('fence'); if (r() < 0.45) props.push('hut'); if (r() < 0.3) props.push('dish');
    for (const p of props) {
      const px = 4 + Math.floor(r() * Math.max(1, W - 30));
      if (p === 'tank') { const ty = base - 22; for (let j = 0; j < 11; j++) for (let i = 0; i < 16; i++) L.px(px + i, ty + j, mix([90, 96, 120], [50, 54, 76], i / 16)); L.rect(px, ty, 16, 1, [150, 156, 180]); L.rect(px + 1, ty + 11, 1, 11, [40, 38, 60]); L.rect(px + 14, ty + 11, 1, 11, [40, 38, 60]); L.rect(px + 1, ty + 16, 14, 1, [40, 38, 60]); for (let j = 0; j < 9; j += 2) L.rect(px + 17, ty + 2 + j, 2, 1, [70, 66, 96]); }
      else if (p === 'aerial') { L.rect(px, base - 24, 1, 24, [70, 66, 96]); for (let k = 0; k < 4; k++) L.rect(px - 4 + k, base - 22 + k * 3, 9 - 2 * k, 1, [90, 86, 120]); }
      else if (p === 'fence') { for (let i = 0; i < W; i++) { L.px(i, base - 8, [60, 56, 84]); for (let j = 1; j < 8; j++) if ((i + j) % 3 === 0) L.px(i, base - 8 + j, [44, 40, 66]); } }
      else if (p === 'hut') { const hx = Math.min(W - 22, px); L.rect(hx, base - 18, 20, 18, [44, 40, 66]); L.rect(hx, base - 18, 20, 1, [110, 104, 150]); L.rect(hx + 12, base - 13, 6, 13, [24, 22, 40]); L.rect(hx + 13, base - 16, 3, 2, [255, 230, 180]); G.add(hx + 13, base - 16, [255, 230, 180], 0.8); }
      else if (p === 'dish') { for (let a = -1.4; a < 1.4; a += 0.15) L.px(px + 6 + Math.round(Math.sin(a) * 5), base - 12 + Math.round(Math.cos(a) * 5), [150, 150, 170]); L.rect(px + 6, base - 7, 1, 7, [70, 66, 96]); }
    }
  }
  // ---- the scenes that are not facades
  function paintScene(L, G, sg, W, r, moving, left) {
    const base = sg.y1, h = sg.y1 - sg.y0, pick = (a) => a[Math.floor(r() * a.length)];
    // a far, low skyline behind every scene
    for (let x = 0; x < W;) { const w = 5 + Math.floor(r() * 10), bh = 8 + Math.floor(r() * 16); for (let j = 0; j < bh; j++) for (let i = 0; i < w && x + i < W; i++) L.px(x + i, base - 14 - j, [20, 16, 40]); for (let q = 0; q < w * bh / 14; q++) { const wx = x + Math.floor(r() * w), wy = base - 15 - Math.floor(r() * (bh - 2)); if (wx < W) { L.px(wx, wy, [255, 200, 130], 0.6); } } x += w; }
    if (sg.scene === 'park') {
      for (let j = 0; j < 14; j++) for (let x = 0; x < W; x++) L.px(x, base - 14 + j, mix([24, 44, 40], [14, 26, 26], j / 14 + (BAY[(x & 3) + ((j & 3) << 2)] - 0.5) * 0.3));   // the grass
      const tx = left ? Math.floor(W * 0.38) : Math.floor(W * 0.62);
      for (let j = 0; j < 30; j++) { const w = j < 6 ? 5 : 3; for (let i = 0; i < w; i++) L.px(tx - (w >> 1) + i + Math.round(Math.sin(j * 0.3) * 1), base - 12 - j, i === 0 ? [40, 24, 30] : [74, 44, 46]); }   // the trunk
      for (const [bx, by, l] of [[-14, -30, 16], [12, -34, 14], [-6, -40, 10], [8, -26, 12]]) for (let i = 0; i < l; i++) L.px(tx + Math.round(bx * i / l), base - 12 + Math.round(by * (0.6 + 0.4 * i / l)), [74, 44, 46]);
      const pinks = [C('#ffb3d9'), C('#ff8ad1'), C('#ffd1ec'), C('#e070b0')];
      for (let q = 0; q < 420; q++) { const a = r() * 6.28, d = Math.sqrt(r()), cx = tx + Math.round(Math.cos(a) * d * 26), cy = base - 50 + Math.round(Math.sin(a) * d * 16); const c = pinks[Math.floor(r() * 4)]; L.px(cx, cy, c.map((v) => v * (0.55 + 0.35 * (1 - (cy - (base - 66)) / 32)))); }
      G.add(tx, base - 50, [255, 138, 209], 0);
      const lx = left ? W - 16 : 12; L.rect(lx, base - 40, 2, 28, [50, 46, 74]); L.rect(lx - 3, base - 43, 8, 3, [36, 32, 56]); L.rect(lx - 2, base - 40, 6, 2, [255, 226, 170]);
      for (let j = 0; j < 30; j++) for (let i = -10; i < 12; i++) { const d = Math.hypot(i, j * 0.6) / 14; if (d < 1) G.add(lx + i, base - 39 + j, [255, 210, 150], 0.12 * (1 - d)); }
      G.add(lx, base - 40, [255, 226, 170], 0.9);
      const bx2 = left ? 4 : W - 24; L.rect(bx2, base - 18, 20, 2, [110, 70, 50]); L.rect(bx2, base - 22, 20, 1, [90, 56, 40]); L.rect(bx2 + 2, base - 16, 1, 4, [40, 36, 60]); L.rect(bx2 + 17, base - 16, 1, 4, [40, 36, 60]);   // a bench
      for (let p = 0; p < 7; p++) { const ph = r() * 10, x0 = tx - 24 + r() * 48, sp = 0.6 + r() * 0.5; moving.push({ k: 'petal', draw: (D, t) => { const u = ((t * 0.08 * sp + ph) % 1); D.R(Math.round(x0 + Math.sin(t * 1.4 + ph) * 4 + u * 10), Math.round(base - 46 + u * 34), 1, 1, [255, 190, 225], 1 - u * 0.5); } }); }
    } else if (sg.scene === 'shrine') {
      for (let j = 0; j < 12; j++) for (let x = 0; x < W; x++) L.px(x, base - 12 + j, (x >> 2) % 2 === (j >> 1) % 2 ? [56, 52, 72] : [46, 42, 62]);   // the stone path
      const cx = Math.floor(W / 2), half = Math.min(28, Math.floor(W * 0.36)), red = C('#c8323a'), redD = C('#8a1e2a');
      for (const sx of [cx - half + 4, cx + half - 7]) { L.rect(sx, base - 56, 3, 44, red); L.rect(sx + 2, base - 56, 1, 44, redD); L.rect(sx - 1, base - 15, 5, 3, [20, 16, 24]); }
      L.rect(cx - half - 2, base - 62, 2 * half + 4, 3, [24, 18, 26]); L.rect(cx - half - 4, base - 63, 2 * half + 8, 1, [40, 30, 40]);   // kasagi
      L.rect(cx - half, base - 59, 2 * half, 3, red); L.rect(cx - half + 2, base - 50, 2 * half - 4, 2, red); L.rect(cx - 1, base - 58, 3, 8, redD);   // shimaki, nuki, gakuzuka
      for (const tx of [cx - half - 10, cx + half + 6]) { if (tx < 0 || tx + 6 > W) continue; L.rect(tx, base - 14, 6, 2, [100, 98, 118]); L.rect(tx + 2, base - 22, 2, 8, [90, 88, 108]); L.rect(tx - 1, base - 28, 8, 6, [110, 108, 128]); L.rect(tx + 1, base - 26, 4, 3, [255, 200, 120]); G.add(tx + 1, base - 26, [255, 200, 120], 0.8); G.add(tx + 2, base - 25, [255, 160, 90], 0.5); L.rect(tx - 2, base - 31, 10, 3, [80, 78, 100]); }
      for (let j = 0; j < 40; j++) for (let i = -half; i < half; i++) { const d = Math.hypot(i, j - 20) / 34; if (d < 1) G.add(cx + i, base - 50 + j, [200, 40, 50], 0.05 * (1 - d)); }
    } else if (sg.scene === 'train') {
      const ty = base - 40;
      for (let j = 0; j < 8; j++) for (let x = 0; x < W; x++) L.px(x, ty + j, j === 0 ? [110, 106, 140] : mix([70, 66, 92], [40, 36, 60], j / 8));   // the viaduct's deck
      for (let px = 6; px < W; px += 34) for (let j = 8; j < 40; j++) for (let i = 0; i < 6; i++) L.px(px + i, ty + j, i === 0 ? [80, 76, 104] : [46, 42, 66]);   // its pillars
      for (let x = 0; x < W; x++) { L.px(x, ty - 1, [150, 150, 170]); if (x % 5 === 0) L.px(x, ty - 2, [60, 56, 84]); }
      for (let x = 8; x < W; x += 24) { L.rect(x, ty - 22, 1, 21, [60, 56, 84]); L.rect(x - 2, ty - 22, 5, 1, [60, 56, 84]); }   // the catenary's masts
      for (let x = 0; x < W; x++) L.px(x, ty - 20 + Math.round(Math.sin(x / 24 * Math.PI) * 1), [30, 28, 48]);
      const ph = r() * 30, per = 26 + r() * 14, dir = r() < 0.5 ? 1 : -1, stripe = pick([C('#3ee08a'), C('#ff7a63'), C('#5ee6ff'), C('#ffc36b')]);
      moving.push({ k: 'train', draw: (D, t) => {
        const u = ((t + ph) % per) / 6; if (u > 1) return;                              // it crosses in 6 s, then the track is empty
        const len = 140, x0 = dir > 0 ? Math.round(-len + u * (W + len)) : Math.round(W - u * (W + len));
        for (let cxx = 0; cxx < 3; cxx++) { const cx0 = x0 + cxx * 47; D.R(cx0, ty - 17, 45, 15, [196, 200, 214]); D.R(cx0, ty - 17, 45, 1, [235, 238, 246]); D.R(cx0, ty - 7, 45, 2, stripe); D.R(cx0, ty - 3, 45, 2, [40, 40, 56]);
          for (let w = 0; w < 5; w++) D.E(cx0 + 3 + w * 9, ty - 14, 6, 5, [255, 236, 190], 0.85); }
      } });
    }
  }
  function bmp(L, rows, x, y, c) { rows.forEach((row, yy) => [...row].forEach((ch, xx) => { if (ch !== '.') L.px(x + xx, y + yy, c); })); }

  // ---- on the page: two sticky canvases a side (the colour, the glow), the still layers sliced into them as the page scrolls
  const sides = ['left', 'right'].map((side) => {
    const wrap = document.createElement('div'); wrap.className = 'wall wall-' + side; wrap.setAttribute('aria-hidden', 'true');
    const inn = document.createElement('div'); inn.className = 'wall-in';
    const base = document.createElement('canvas'), glow = document.createElement('canvas'); glow.className = 'wall-glow';
    inn.append(base, glow); wrap.append(inn); pg.prepend(wrap);
    return { side, wrap, base, glow, g: base.getContext('2d'), h: glow.getContext('2d'), W: 0, still: null, stillG: null, moving: [] };
  });
  let on = false, seen = false, t = 0;
  function frame() {
    if (!on) return;
    const pr = pg.getBoundingClientRect(), topCss = Math.max(0, -pr.top), top = Math.floor(topCss / P), rows = Math.ceil(innerHeight / P) + 2;
    for (const S of sides) {
      for (const c of [S.base, S.glow]) { if (c.width !== S.W || c.height !== rows) { c.width = S.W; c.height = rows; c.style.width = S.W * P + 'px'; c.style.height = rows * P + 'px'; } c.style.transform = `translateY(${-(topCss - top * P)}px)`; }
      const g = S.g, h = S.h, W = S.W, n = Math.max(0, Math.min(rows, S.H - top));
      g.imageSmoothingEnabled = false; h.imageSmoothingEnabled = false;
      g.clearRect(0, 0, W, rows); h.fillStyle = '#000'; h.fillRect(0, 0, W, rows);
      if (n > 0) { g.drawImage(S.still, 0, top, W, n, 0, 0, W, n); h.drawImage(S.stillG, 0, top, W, n, 0, 0, W, n); }
      const D = {
        R: (x, y, w, hh, c, a) => { g.fillStyle = css(c, a); g.fillRect(x, y - top, w, hh); },
        E: (x, y, w, hh, c, a) => { g.fillStyle = css(c, a); g.fillRect(x, y - top, w, hh); h.fillStyle = css(c, a == null ? 0.9 : a); h.fillRect(x, y - top, w, hh); },
        bmp: (rows2, x, y, c, lit) => rows2.forEach((row, yy) => [...row].forEach((ch, xx) => { if (ch === '.') return; g.fillStyle = css(c); g.fillRect(x + xx, y + yy - top, 1, 1); if (lit) { h.fillStyle = css(c, 0.9); h.fillRect(x + xx, y + yy - top, 1, 1); } })),
        glassNow: (f) => { f({ px: (x, y, c, a) => { g.fillStyle = css(c, a); g.fillRect(x, y - top, 1, 1); }, rect: (x, y, w, hh, c, a) => { g.fillStyle = css(c, a); g.fillRect(x, y - top, w, hh); } },
                             { add: (x, y, c, a) => { h.fillStyle = css(c, a); h.fillRect(x, y - top, 1, 1); } }); } };
      for (const m of S.moving) m.draw(D, t);
    }
  }
  function layout() {
    const pr = pg.getBoundingClientRect(), cr = ct.getBoundingClientRect(), room = Math.min(240, Math.floor((cr.left - pr.left) * 0.55));   // (a little over half the margin: the content leads)
    on = room >= 90;
    sides.forEach((S) => { S.wrap.style.display = on ? '' : 'none'; });
    if (!on) return;
    const H = Math.ceil(pg.offsetHeight / P);
    sides.forEach((S, k) => {
      S.wrap.style.width = room + 'px'; S.W = Math.floor(room / P); S.H = H;
      const signs = atlas.ok ? LOGOS.filter((l) => l[2] === S.side).map((l) => ({ k: l[0], y: Math.round(l[1] * H) })) : [];
      const B = build(S.W, H, 'wall' + k + ':' + S.W, S.side === 'left', signs);
      const toCanvas = (Ly) => { const c = document.createElement('canvas'); c.width = S.W; c.height = H; c.getContext('2d').putImageData(new ImageData(Ly.d, S.W, H), 0, 0); return c; };
      S.still = toCanvas(B.L); S.stillG = toCanvas(B.G); S.moving = B.moving;
    });
    frame();
  }
  layout();
  if (me) {
    const img = new Image();
    img.onload = () => { try { const c = document.createElement('canvas'); c.width = img.width; c.height = img.height; const g = c.getContext('2d'); g.drawImage(img, 0, 0); atlas.d = g.getImageData(0, 0, img.width, img.height).data; atlas.W = img.width; atlas.ok = true; layout(); } catch (e) { /* the walls without their signs */ } };
    img.src = new URL('wall_logos.png?v=2', me).href;
  }
  let lt = 0, lastH = 0; const later = () => { clearTimeout(lt); lt = setTimeout(() => { if (Math.abs(pg.offsetHeight - lastH) > 2 || true) { lastH = pg.offsetHeight; layout(); } }, 200); };
  addEventListener('resize', later); addEventListener('load', later);
  if ('ResizeObserver' in window) new ResizeObserver(later).observe(ct);
  let raf = 0; addEventListener('scroll', () => { if (!raf) raf = requestAnimationFrame(() => { raf = 0; frame(); }); }, { passive: true });
  if (!still) {
    if ('IntersectionObserver' in window) new IntersectionObserver((es) => { seen = es[0].isIntersecting; }).observe(pg); else seen = true;
    let acc = 0, last = 0;
    (function loop(now) { if (seen && on && !document.hidden) { acc += Math.min(0.1, (now - (last || now)) / 1000); if (acc > 1 / 12) { t += acc; acc = 0; frame(); } } last = now; requestAnimationFrame(loop); })(performance.now());
  }
})();
