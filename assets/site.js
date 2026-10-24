/* mtsfj.github.io · what every page shares: the language, the email, the BibTeX, the vignettes.
   No dependency; load it at the end of <body> (or with defer). */
(function () {
  // ---- the language: ?lang= wins, then the last choice, then the browser's (French only for a French browser).
  // A page in two languages marks its blocks data-lang="fr" / data-lang="en" and gives its titles as
  // <html data-title-fr="…" data-title-en="…">; its toggle is the button .lang (it shows the other language).
  const store = { get() { try { return localStorage.getItem('mtsfj-lang'); } catch (e) { return null; } },
    set(v) { try { localStorage.setItem('mtsfj-lang', v); } catch (e) {} } };
  const root = document.documentElement, q = new URLSearchParams(location.search).get('lang');
  const two = !!document.querySelector('[data-lang]');
  let lang = q === 'fr' || q === 'en' ? q : store.get() || ((navigator.language || 'en').toLowerCase().startsWith('fr') ? 'fr' : 'en');
  function apply() {
    if (!two) return;
    root.lang = lang;
    document.querySelectorAll('[data-lang]').forEach((el) => { el.hidden = el.dataset.lang !== lang; });
    document.querySelectorAll('button.lang').forEach((b) => {
      b.textContent = lang === 'fr' ? 'EN' : 'FR'; b.setAttribute('aria-label', lang === 'fr' ? 'Switch to English' : 'Passer en français');
    });
    const t = root.dataset['title' + (lang === 'fr' ? 'Fr' : 'En')]; if (t) document.title = t;
  }
  document.querySelectorAll('button.lang').forEach((b) => b.addEventListener('click', () => {
    lang = lang === 'fr' ? 'en' : 'fr'; store.set(lang); apply();
  }));
  apply();

  // ---- the email: built on a click (never in the page's text, for the scrapers), then a plain link.
  // <button type="button" class="btn mail-reveal">E-mail</button>
  document.querySelectorAll('.mail-reveal').forEach((b) => b.addEventListener('click', () => {
    const at = ['fajeau', 'mathis', '8'].join('') + String.fromCharCode(64) + ['gmail', 'com'].join('.'), a = document.createElement('a');
    a.href = 'mailto:' + at; a.textContent = at; a.className = b.className.replace('mail-reveal', '').trim(); b.replaceWith(a); a.focus();
  }));

  // ---- a BibTeX block shown on demand: <button class="bib-toggle" aria-controls="id" aria-expanded="false">
  document.querySelectorAll('.bib-toggle').forEach((b) => b.addEventListener('click', () => {
    const pre = document.getElementById(b.getAttribute('aria-controls')); if (!pre) return;
    pre.hidden = !pre.hidden; b.setAttribute('aria-expanded', String(!pre.hidden));
  }));

  // ---- the vignette for a post without a picture: a small pixel night, always the same for the same seed.
  // <canvas class="vignette" data-seed="the-post-slug" width="96" height="64"></canvas>
  // A grid of windows on a dark facade, some lit (warm, pink or cyan as the street's), a few stars above.
  function rnd(seed) { let h = 2166136261; for (const c of seed) { h ^= c.charCodeAt(0); h = Math.imul(h, 16777619); } return () => { h ^= h << 13; h ^= h >>> 17; h ^= h << 5; return ((h >>> 0) % 1e6) / 1e6; }; }
  document.querySelectorAll('canvas.vignette[data-seed]').forEach((cv) => {
    const W = cv.width = 96, H = cv.height = 64, g = cv.getContext('2d'), r = rnd(cv.dataset.seed);
    const sky = g.createLinearGradient(0, 0, 0, H); sky.addColorStop(0, '#0f0c22'); sky.addColorStop(1, '#2a1c46'); g.fillStyle = sky; g.fillRect(0, 0, W, H);
    for (let i = 0; i < 14; i++) { g.fillStyle = r() < 0.3 ? '#ffc36b' : '#f1ebe4'; g.globalAlpha = 0.4 + 0.5 * r(); g.fillRect(Math.floor(r() * W), Math.floor(r() * 22), 1, 1); }
    g.globalAlpha = 1;
    const lit = ['#ffc36b', '#ff8ad1', '#5ee6ff'], hue = lit[Math.floor(r() * 3)];
    let x = 0;
    while (x < W) {                                   // the buildings: each its height, its windows
      const bw = 14 + Math.floor(r() * 16), bh = 24 + Math.floor(r() * 30), top = H - bh;
      g.fillStyle = r() < 0.5 ? '#1e1838' : '#241d44'; g.fillRect(x, top, bw - 1, bh);
      for (let wy = top + 3; wy < H - 4; wy += 5) for (let wx = x + 2; wx < x + bw - 3; wx += 4) {
        const v = r(); if (v < 0.28) { g.fillStyle = v < 0.09 ? hue : '#ffc36b'; g.globalAlpha = 0.55 + 0.45 * r(); g.fillRect(wx, wy, 2, 2); g.globalAlpha = 1; }
        else { g.fillStyle = '#17132c'; g.fillRect(wx, wy, 2, 2); }
      }
      x += bw;
    }
    g.fillStyle = 'rgba(255,138,209,.10)'; g.fillRect(0, H - 6, W, 6);   // the street's glow
  });

  // ---- the skyline: the street's roofs at the page's foot, one pixel of it = 4 of the screen, the same for the
  // same seed. <div class="skyline"><canvas data-seed="…"></canvas></div>
  function skyline(cv) {
    const W = Math.max(160, Math.min(720, Math.round(cv.clientWidth / 4))), H = Math.max(14, Math.round(cv.clientHeight / 4));
    cv.width = W; cv.height = H;
    const g = cv.getContext('2d'), r = rnd(cv.dataset.seed || 'skyline'), lit = ['#ffc36b', '#ffc36b', '#ffc36b', '#ff8ad1', '#5ee6ff'];
    g.clearRect(0, 0, W, H);
    let x = 0;
    while (x < W) {
      const bw = 6 + Math.floor(r() * 14), bh = Math.round(H * (0.32 + 0.6 * r())), top = H - bh, c = r() < 0.5 ? '#1b1533' : '#211a3e';
      g.fillStyle = c; g.fillRect(x, top, bw, bh);
      if (r() < 0.25) { g.fillRect(x + Math.floor(bw / 2), top - 2 - Math.floor(r() * 3), 1, 3); }   // an antenna
      if (r() < 0.2 && bw > 8) { g.fillStyle = '#ff3b3b'; g.globalAlpha = 0.8; g.fillRect(x + Math.floor(bw / 2), top - 1, 1, 1); g.globalAlpha = 1; }   // its red light
      for (let wy = top + 2; wy < H - 1; wy += 3) for (let wx = x + 1; wx < x + bw - 1; wx += 2) {
        if (r() < 0.16) { g.fillStyle = lit[Math.floor(r() * lit.length)]; g.globalAlpha = 0.35 + 0.5 * r(); g.fillRect(wx, wy, 1, 1); g.globalAlpha = 1; }
      }
      x += bw + (r() < 0.3 ? 1 : 0);
    }
  }
  const skies = [...document.querySelectorAll('.skyline canvas')];
  if (skies.length) {
    skies.forEach(skyline);
    let tm = 0; addEventListener('resize', () => { clearTimeout(tm); tm = setTimeout(() => skies.forEach(skyline), 150); });
  }

  const still = matchMedia('(prefers-reduced-motion: reduce)').matches;

  // ---- reveal: the page's blocks come in as they are reached, a grid's items one after the other
  const io = 'IntersectionObserver' in window && !still ? new IntersectionObserver((es) => es.forEach((e) => {
    if (e.isIntersecting) { e.target.classList.add('in'); io.unobserve(e.target); }
  }), { rootMargin: '0px 0px -8% 0px', threshold: 0.08 }) : null;
  if (io) {
    const blocks = document.querySelectorAll('.page .section-head, .page .split > *, .page .entries-grid > li, .page .projects > li, .page .chips.tools, .page .pub, .page .cta, .page .more, .page .masthead > *, .page .prose > *, .page .chrono');
    blocks.forEach((el) => {
      const sib = el.parentElement ? [...el.parentElement.children].indexOf(el) : 0;
      el.classList.add('reveal'); el.style.transitionDelay = Math.min(sib, 6) * 80 + 'ms'; io.observe(el);
    });
    document.querySelectorAll('.chrono li').forEach((li, i, all) => li.style.setProperty('--i', [...li.parentElement.children].indexOf(li)));
  }

  // ---- the glow under the pointer, on the glass (cards, projects, spotlit panels)
  document.querySelectorAll('.entry, .project, .panel.spot, .cta').forEach((el) => el.addEventListener('pointermove', (e) => {
    const r = el.getBoundingClientRect(); el.style.setProperty('--mx', (e.clientX - r.left) + 'px'); el.style.setProperty('--my', (e.clientY - r.top) + 'px');
  }));

  // ---- FIG. 01, a game of autotelic agents. Four agents share a grid; each paints the cells it walks on in its colour,
  // and a round is won at 40 % of the board (or by the largest share after 50 s). None is told what to do: each sets
  // its own next goal, of three kinds (expand into free cells, raid the leader, take back what it lost), and picks the
  // kind where its competence is changing fastest (learning progress, |recent - older| success), so its curriculum is
  // its own and moves as the others play. What it learns carries over from round to round.
  // <figure class="fig game"> … <canvas class="game-board"></canvas><ol class="game-score"></ol><p class="game-round"></p>
  const L = () => (document.documentElement.lang === 'en' ? 1 : 0);
  document.querySelectorAll('.game').forEach((root) => {
    const cv = root.querySelector('.game-board'), score = root.querySelector('.game-score'), banner = root.querySelector('.game-round');
    const COLS = 24, ROWS = 16, NC = COLS * ROWS, g = cv.getContext('2d'), R = rnd(root.dataset.seed || 'game');
    const AG = [{ c: [255, 138, 209], n: ['rose', 'pink'] }, { c: [94, 230, 255], n: ['cyan', 'cyan'] }, { c: [255, 195, 107], n: ['ambre', 'amber'] }, { c: [157, 123, 255], n: ['violet', 'violet'] }];
    const KINDS = ['expand', 'raid', 'defend'];
    const owner = new Int8Array(NC).fill(-1), flash = new Float32Array(NC), lostAt = new Float32Array(NC * 4);
    const starts = [[1, 1], [COLS - 2, ROWS - 2], [COLS - 2, 1], [1, ROWS - 2]];
    const agents = AG.map((a, k) => ({ k, x: starts[k][0], y: starts[k][1], goal: null, step: R() * 0.1, wins: 0, hist: { expand: [], raid: [], defend: [] } }));
    let T = 0, roundT = 0, pause = 0, winner = -1, dom = 0;
    const idx = (x, y) => y * COLS + x, count = (k) => { let n = 0; for (let i = 0; i < NC; i++) if (owner[i] === k) n++; return n; };
    const leaderOf = (k) => { let b = -1, bn = -1; for (let j = 0; j < 4; j++) if (j !== k) { const n = count(j); if (n > bn) { bn = n; b = j; } } return b; };
    function lp(h) { if (h.length < 4) return 0.6; const m = (a) => a.reduce((s, v) => s + v, 0) / Math.max(1, a.length); const half = Math.floor(h.length / 2); return Math.abs(m(h.slice(half)) - m(h.slice(0, half))); }
    function regionScore(a, kind, cx, cy, foe) {
      let v = 0;
      for (let y = cy - 2; y <= cy + 2; y++) for (let x = cx - 2; x <= cx + 2; x++) {
        if (x < 0 || y < 0 || x >= COLS || y >= ROWS) continue; const i = idx(x, y), o = owner[i];
        if (kind === 'expand' && o === -1) v++;
        else if (kind === 'raid' && o === foe) v++;
        else if (kind === 'defend' && o !== a.k && o !== -1 && T - lostAt[i * 4 + a.k] < 25) v++;
      }
      return v - 0.12 * (Math.abs(cx - a.x) + Math.abs(cy - a.y));
    }
    function choose(a) {
      const w = KINDS.map((k) => lp(a.hist[k]) + 0.08), sum = w.reduce((s, v) => s + v, 0);
      let r = R() * sum, kind = KINDS[0]; for (let i = 0; i < 3; i++) { r -= w[i]; if (r <= 0) { kind = KINDS[i]; break; } }
      const foe = leaderOf(a.k); let best = null, bs = 0.5;
      for (let t = 0; t < 14; t++) { const cx = 2 + Math.floor(R() * (COLS - 4)), cy = 2 + Math.floor(R() * (ROWS - 4)), v = regionScore(a, kind, cx, cy, foe); if (v > bs) { bs = v; best = [cx, cy]; } }
      if (!best) { if (kind !== 'expand') a.hist[kind].push(0); kind = 'expand'; best = [2 + Math.floor(R() * (COLS - 4)), 2 + Math.floor(R() * (ROWS - 4))]; }
      a.goal = { kind, x: best[0], y: best[1], foe, t0: T, gain: 0, budget: 4 + 0.16 * (Math.abs(best[0] - a.x) + Math.abs(best[1] - a.y)) };
    }
    function paint(a) {
      const i = idx(a.x, a.y), o = owner[i];
      if (o !== a.k) { if (o >= 0) lostAt[i * 4 + o] = T; owner[i] = a.k; flash[i] = 1; const G = a.goal; if (G && Math.abs(a.x - G.x) <= 2 && Math.abs(a.y - G.y) <= 2) G.gain++; }
    }
    function move(a) {
      const G = a.goal, inside = Math.abs(a.x - G.x) <= 2 && Math.abs(a.y - G.y) <= 2;
      const opts = [[1, 0], [-1, 0], [0, 1], [0, -1]].map(([dx, dy]) => [a.x + dx, a.y + dy]).filter(([x, y]) => x >= 0 && y >= 0 && x < COLS && y < ROWS);
      let best = null, bv = -1e9;
      for (const [x, y] of opts) {
        const d = Math.abs(x - G.x) + Math.abs(y - G.y), mine = owner[idx(x, y)] === a.k;
        const v = (inside ? (Math.abs(x - G.x) <= 2 && Math.abs(y - G.y) <= 2 ? 1 : -3) : -d) + (mine ? -0.6 : 0.6) + R() * 0.3;
        if (v > bv) { bv = v; best = [x, y]; }
      }
      a.x = best[0]; a.y = best[1]; paint(a);
    }
    function reset() { owner.fill(-1); flash.fill(0); agents.forEach((a, k) => { a.x = starts[k][0]; a.y = starts[k][1]; a.goal = null; paint(a); }); roundT = 0; winner = -1; }
    function tick(dt) {
      T += dt; for (let i = 0; i < NC; i++) if (flash[i] > 0) flash[i] = Math.max(0, flash[i] - dt * 1.6);
      if (pause > 0) { pause -= dt; if (pause <= 0) reset(); return; }
      roundT += dt;
      for (const a of agents) {
        if (!a.goal) choose(a);
        a.step -= dt; if (a.step > 0) continue; a.step += 0.12;
        const G = a.goal, inside = Math.abs(a.x - G.x) <= 2 && Math.abs(a.y - G.y) <= 2;
        if (T - G.t0 > G.budget || (inside && regionScore(a, G.kind, G.x, G.y, G.foe) + 0.12 * (Math.abs(G.x - a.x) + Math.abs(G.y - a.y)) <= 0)) {
          const h = a.hist[G.kind]; h.push(Math.min(1, G.gain / 7)); if (h.length > 12) h.shift(); choose(a);
        }
        move(a);
      }
      const n = agents.map((a) => count(a.k)), lead = n.indexOf(Math.max(...n));
      if (n[lead] >= 0.40 * NC || roundT > 50) { winner = lead; agents[lead].wins++; pause = 2.6; }
    }
    function draw() {
      const cell = Math.max(4, Math.floor((cv.clientWidth || 480) * (window.devicePixelRatio || 1) / COLS));
      if (cv.width !== COLS * cell) { cv.width = COLS * cell; cv.height = ROWS * cell; }
      g.clearRect(0, 0, cv.width, cv.height);
      const gap = Math.max(1, Math.round(cell / 8));
      for (let y = 0; y < ROWS; y++) for (let x = 0; x < COLS; x++) {
        const i = idx(x, y), o = owner[i];
        if (o < 0) g.fillStyle = 'rgba(255,255,255,.045)';
        else { const [r, gg, b] = AG[o].c, f = flash[i]; g.fillStyle = `rgba(${Math.round(r + (255 - r) * f * .6)},${Math.round(gg + (255 - gg) * f * .6)},${Math.round(b + (255 - b) * f * .6)},${0.42 + 0.4 * f})`; }
        g.fillRect(x * cell + gap, y * cell + gap, cell - 2 * gap, cell - 2 * gap);
      }
      for (const a of agents) {                                      // each goal, outlined in its colour
        if (!a.goal || pause > 0) continue; const [r, gg, b] = AG[a.k].c, G = a.goal;
        g.strokeStyle = `rgba(${r},${gg},${b},.55)`; g.lineWidth = Math.max(1, cell / 10); g.setLineDash([cell / 3, cell / 4]);
        g.strokeRect((G.x - 2) * cell + 1, (G.y - 2) * cell + 1, 5 * cell - 2, 5 * cell - 2); g.setLineDash([]);
      }
      for (const a of agents) {                                      // the agents: a white core in their colour, a glow
        const [r, gg, b] = AG[a.k].c;
        g.shadowColor = `rgba(${r},${gg},${b},.95)`; g.shadowBlur = cell * 1.2;
        g.fillStyle = `rgb(${r},${gg},${b})`; g.fillRect(a.x * cell + 1, a.y * cell + 1, cell - 2, cell - 2);
        g.shadowBlur = 0; g.fillStyle = '#fff'; const q = Math.round(cell * 0.28); g.fillRect(a.x * cell + q, a.y * cell + q, cell - 2 * q, cell - 2 * q);
      }
    }
    function board() {                                                 // the scores, the goals, the rounds (4 a second)
      const l = L(), n = agents.map((a) => count(a.k)), lbl = { expand: ['s’étend', 'expands'], raid: ['attaque', 'raids'], defend: ['reprend', 'takes back'] };
      score.innerHTML = agents.map((a) => {
        const G = a.goal, goal = pause > 0 ? '' : !G ? '…' : lbl[G.kind][l] + (G.kind === 'raid' && G.foe >= 0 ? ' ' + AG[G.foe].n[l] : '');
        return `<li style="--c:rgb(${AG[a.k].c})"><i></i><span class="g-name">${AG[a.k].n[l]}</span><span class="g-bar"><b style="width:${(100 * n[a.k] / NC).toFixed(1)}%"></b></span><span class="g-pct">${Math.round(100 * n[a.k] / NC)} %</span><span class="g-goal">${goal}</span><span class="g-wins" title="${l ? 'rounds won' : 'manches gagnées'}">${a.wins}</span></li>`;
      }).join('');
      banner.textContent = winner >= 0 && pause > 0 ? (l ? `${AG[winner].n[1]} wins the round` : `${AG[winner].n[0]} gagne la manche`) : (l ? '40 % of the board, or the largest share at 50 s' : '40 % de la grille, ou le plus grand territoire à 50 s');
      banner.style.setProperty('--c', winner >= 0 && pause > 0 ? `rgb(${AG[winner].c})` : '');
    }
    reset();
    if (still) { for (let k = 0; k < 400; k++) tick(0.05); draw(); board(); return; }
    let on = false, last = 0;
    if ('IntersectionObserver' in window) new IntersectionObserver((es) => { on = es[0].isIntersecting; }).observe(root); else on = true;
    (function loop(now) {
      if (on && !document.hidden) { const dt = Math.min(0.1, (now - (last || now)) / 1000); last = now; tick(dt); draw(); if ((dom -= dt) <= 0) { dom = 0.25; board(); } } else last = 0;
      requestAnimationFrame(loop);
    })(performance.now());
    board(); draw();
  });

  // ---- the walls: on a wide screen the street goes on down the page's margins, a facade on each side drawn in the
  // scene's pixels (4 screen px a pixel): floors of windows lit or dark (curtains, plants, a cat), vertical neon signs
  // with pictograms, red lanterns, vending machines, noren, balconies and their washing, wires and crows, small neon
  // words. The same for the same page; it lives a little (neon flicker, windows, lanterns swaying) at 12 frames a
  // second while seen, still under reduced motion. The content keeps its own ground: the walls fade toward it.
  const FONT = { O: '111101101101111', P: '111101111100100', E: '111100110100111', N: '101111111111101', '2': '111001111100111', '4': '101101111001001', H: '101101111101101', B: '110101110101110', A: '010101111101101', R: '110101110101101' };
  const PICT = {
    bowl: ['.#..#..', '..#..#.', '#######', '#.....#', '.#...#.', '..###..'],
    cup: ['.#.#..', '#.#...', '......', '#####.', '#...##', '#...#.', '.###..'],
    heart: ['.##.##.', '#######', '#######', '.#####.', '..###..', '...#...'],
    star: ['...#...', '..###..', '#######', '.#####.', '.##.##.', '#.....#'],
    note: ['..####', '..#..#', '..#..#', '..#..#', '###.##', '##.###'],
    cat: ['#...#', '##.##', '#####', '#.#.#', '#####', '.###.'] };
  const NEON = ['#ff8ad1', '#5ee6ff', '#ffc36b', '#9d7bff', '#ff7a63'];
  function walls() {
    const pg = document.querySelector('.page'), ct = pg && pg.querySelector(':scope > .container'); if (!ct) return;
    const sides = ['left', 'right'].map((side) => {
      const wrap = document.createElement('div'); wrap.className = 'wall wall-' + side; wrap.setAttribute('aria-hidden', 'true');
      const base = document.createElement('canvas'), glow = document.createElement('canvas'), inn = document.createElement('div'); glow.className = 'wall-glow'; inn.className = 'wall-in';
      inn.append(base, glow); wrap.append(inn); pg.prepend(wrap);
      return { side, wrap, base, glow, g: base.getContext('2d'), h: glow.getContext('2d'), items: [], W: 0 };
    });
    let P = 4, Hh = 0, on = false, seen = false, t = 0;
    // ---- the parts, in art pixels; e(): an emissive pixel (the glow canvas gets it too)
    function painter(S, oy) {
      const g = S.g, h = S.h;
      const R = (x, y, w, hh, c) => { g.fillStyle = c; g.fillRect(x, y - oy, w, hh); };
      const E = (x, y, w, hh, c, a) => { g.fillStyle = c; g.fillRect(x, y - oy, w, hh); h.globalAlpha = a == null ? 1 : a; h.fillStyle = c; h.fillRect(x, y - oy, w, hh); h.globalAlpha = 1; };
      const bmp = (rows, x, y, f) => rows.forEach((row, yy) => [...row].forEach((ch, xx) => { if (ch !== '.') f(x + xx, y + yy, ch); }));
      return { R, E, bmp };
    }
    const hash = (a, b) => { const v = Math.sin(a * 12.9898 + b * 78.233) * 43758.5453; return v - Math.floor(v); };
    function populate(W, H, r, left) {
      const it = [], F = 46, inner = left ? W : 0;
      const pick = (arr) => arr[Math.floor(r() * arr.length)];
      let y = 26, recent = [], bLeft = 0, style = 'panel', tint = '#120e25';
      while (y + F < H) {
        if (bLeft-- <= 0) { bLeft = 1 + Math.floor(r() * 3); style = pick(['panel', 'brick', 'siding', 'tile']); tint = pick(['#120e25', '#15102b', '#100c21', '#171130', '#130f28']); }
        it.push({ k: 'wall', y, h: F, tint, style });
        it.push({ k: 'ledge', y: y + F - 3 });
        let kind; do kind = pick(['flats', 'flats', 'shop', 'sign', 'wires', 'balcony', 'machines', 'stairs', 'billboard', 'izakaya']); while (recent.includes(kind)); recent.push(kind); if (recent.length > 3) recent.shift();
        const n = Math.max(1, Math.floor((W - 6) / 18));
        if (kind === 'flats' || kind === 'wires' || kind === 'balcony') {
          const m = Math.min(n, 1 + Math.floor(r() * n)), gap = (W - m * 13) / (m + 1);
          for (let k = 0; k < m; k++) it.push({ k: 'window', x: Math.round(gap + k * (13 + gap)), y: y + 10, lit: r() < 0.6, cur: pick(['#c77be8', '#ff8ad1', '#5ee6ff', '#ffc36b']), sill: pick(['', '', 'plant', 'cat']), ph: r() * 100, per: 20 + r() * 40 });
          if (kind === 'wires') { it.push({ k: 'wire', y: y + 4, sag: 3 + Math.floor(r() * 4), crows: Math.floor(r() * 3) + 1, seed: r() }); }
          if (kind === 'balcony') it.push({ k: 'balcony', y: y + 30, cloth: [0, 1, 2, 3].map(() => pick(['#ff8ad1', '#5ee6ff', '#ffc36b', '#f4efe9', '#9d7bff'])) });
        } else if (kind === 'shop') {
          it.push({ k: 'noren', y: y + 6, c: pick(['#283a8f', '#8f2338', '#3a2a6f']) });
          it.push({ k: 'lantern', x: 4, y: y + 4, ph: r() * 6 }); if (W > 30) it.push({ k: 'lantern', x: W - 11, y: y + 4, ph: r() * 6 });
          if (W > 44) it.push({ k: 'word', x: Math.round(W / 2 - 8), y: y + 30, w: pick(['OPEN', 'BAR', 'RAMEN']), c: pick(NEON), ph: r() * 9 });
        } else if (kind === 'sign') {
          const picts = [0, 1, 2].map(() => pick(Object.keys(PICT)));
          it.push({ k: 'sign', x: left ? 3 : W - 13, y: y + 2, picts, c: pick(NEON), ph: r() * 9 });
          if (W > 34) it.push({ k: 'window', x: left ? 18 : Math.max(3, W - 34), y: y + 12, lit: r() < 0.5, cur: pick(['#c77be8', '#ff8ad1']), sill: pick(['', 'plant']), ph: r() * 100, per: 30 });
        } else if (kind === 'machines') {
          const m = Math.max(1, Math.min(3, Math.floor((W - 4) / 15)));
          for (let k = 0; k < m; k++) it.push({ k: 'vend', x: 3 + k * 15, y: y + F - 25, c: pick(['#e8e3f2', '#ff8ad1', '#5ee6ff', '#ffc36b']), seed: r() });
          if (W - m * 15 > 14) it.push({ k: 'word', x: W - 15, y: y + 8, w: '24H', c: pick(NEON), ph: r() * 9 });
        }
        else if (kind === 'stairs') {
          it.push({ k: 'stairs', y, F, dir: r() < 0.5 ? 1 : -1 });
          it.push({ k: 'window', x: left ? 3 : W - 16, y: y + 6, lit: r() < 0.5, cur: pick(['#5ee6ff', '#ffc36b']), sill: '', ph: r() * 100, per: 25 });
        } else if (kind === 'billboard') {
          it.push({ k: 'board', y: y + 6, ph: r() * 20 });
        } else if (kind === 'izakaya') {
          const m = Math.max(2, Math.min(5, Math.floor((W - 6) / 9)));
          for (let k = 0; k < m; k++) it.push({ k: 'lantern', x: 4 + k * Math.floor((W - 12) / Math.max(1, m - 1)), y: y + 1, ph: r() * 6, small: true });
          it.push({ k: 'shoji', y: y + 17, F });
        }
        y += F;
      }
      it.push({ k: 'pipe', x: left ? W - 3 : 1 });
      return it;
    }
    function draw(S, top, rows) {
      const g = S.g, h = S.h, W = S.W, oy = top, { R, E, bmp } = painter(S, oy);
      g.clearRect(0, 0, W, rows); h.clearRect(0, 0, W, rows);
      const vis = (y, hh) => y + hh >= oy - 2 && y <= oy + rows + 2;
      for (const it of S.items) {
        if (it.k === 'wall') {
          if (!vis(it.y, it.h)) continue; R(0, it.y, W, it.h, it.tint);
          if (it.style === 'panel') for (let x = 7; x < W; x += 16) R(x, it.y, 1, it.h, 'rgba(0,0,0,.2)');
          else if (it.style === 'brick') for (let yy = 0; yy < it.h; yy += 3) { R(0, it.y + yy, W, 1, 'rgba(0,0,0,.16)'); for (let x = (yy / 3) % 2 ? 0 : 3; x < W; x += 6) R(x, it.y + yy + 1, 1, 2, 'rgba(0,0,0,.14)'); }
          else if (it.style === 'siding') for (let yy = 0; yy < it.h; yy += 4) { R(0, it.y + yy, W, 1, 'rgba(255,255,255,.035)'); R(0, it.y + yy + 1, W, 1, 'rgba(0,0,0,.18)'); }
          else for (let yy = 0; yy < it.h; yy += 8) { R(0, it.y + yy, W, 1, 'rgba(0,0,0,.15)'); for (let x = 0; x < W; x += 8) R(x, it.y + yy, 1, 8, 'rgba(0,0,0,.12)'); }
        }
      }
      for (const it of S.items) {
        const k = it.k;
        if (k === 'ledge') { if (!vis(it.y, 3)) continue; R(0, it.y, W, 3, '#0a0817'); R(0, it.y, W, 1, 'rgba(255,255,255,.07)'); }
        else if (k === 'pipe') { R(it.x, oy, 2, rows, '#221b40'); for (let y = Math.ceil(oy / 30) * 30; y < oy + rows; y += 30) R(it.x - 1, y, 4, 2, '#2c2452'); }
        else if (k === 'window') {
          if (!vis(it.y, 22)) continue;
          const lit = still ? it.lit : (Math.floor((t + it.ph) / it.per) % 3 === 2 ? !it.lit : it.lit), x = it.x, y = it.y;
          R(x - 1, y - 1, 15, 19, '#241d44');
          if (lit) { h.globalAlpha = .16; h.fillStyle = '#ffb070'; h.fillRect(x - 5, y - 3 - oy, 23, 30); h.globalAlpha = 1; for (let yy = 0; yy < 17; yy++) E(x, y + yy, 13, 1, yy < 8 ? '#ffd08a' : '#ffad72', .55); R(x, y, 3, 17, it.cur); }
          else { R(x, y, 13, 17, '#1a1534'); R(x + 9, y + 2, 2, 1, 'rgba(255,255,255,.12)'); }
          R(x + 6, y, 1, 17, '#241d44'); R(x, y + 8, 13, 1, '#241d44');
          R(x - 2, y + 17, 17, 2, '#3a3168'); R(x - 2, y + 17, 17, 1, 'rgba(255,255,255,.12)');
          if (it.sill === 'plant') { R(x + 8, y + 14, 4, 3, '#ff7a63'); R(x + 7, y + 11, 2, 3, '#2fae6c'); R(x + 9, y + 10, 2, 4, '#3ee08a'); R(x + 11, y + 12, 2, 2, '#2fae6c'); }
          if (it.sill === 'cat') { bmp(['#.#..', '###..', '###.#', '####.', '####.'], x + 2, y + 12, (px, py) => R(px, py, 1, 1, '#07060f')); if (Math.floor(t * 2 + it.ph) % 9) { E(x + 2, y + 13, 1, 1, '#ffc36b'); } }
        }
        else if (k === 'sign') {
          const hh = 5 + it.picts.length * 9; if (!vis(it.y, hh)) continue;
          const off = !still && hash(Math.floor(t * 12), it.ph) < 0.04, c = it.c, a = off ? .15 : 1;
          R(it.x, it.y, 10, hh, '#0c0a1b'); R(it.x + 4, it.y - 3, 2, 3, '#2c2452');
          const tube = (x, y, w, h2) => off ? R(x, y, w, h2, 'rgba(255,255,255,.08)') : E(x, y, w, h2, c, .9);
          tube(it.x, it.y, 10, 1); tube(it.x, it.y + hh - 1, 10, 1); tube(it.x, it.y, 1, hh); tube(it.x + 9, it.y, 1, hh);
          it.picts.forEach((pk, j) => bmp(PICT[pk], it.x + 2 + (7 - PICT[pk][0].length) / 2 | 0, it.y + 3 + j * 9, (px, py) => off ? R(px, py, 1, 1, 'rgba(255,255,255,.1)') : E(px, py, 1, 1, c, a)));
        }
        else if (k === 'lantern') {
          if (!vis(it.y, 16)) continue;
          const dx = still ? 0 : Math.round(Math.sin(t * 1.3 + it.ph)), x = it.x + dx, y = it.y;
          h.globalAlpha = .22; h.fillStyle = '#ff6a4a'; h.fillRect(x - 3, y + 1 - oy, 13, 16); h.globalAlpha = 1;
          R(it.x + 3, y, 1, 3, '#2c2452'); R(x + 1, y + 3, 5, 1, '#07060f');
          for (let yy = 0; yy < 8; yy++) { const w = yy === 0 || yy === 7 ? 5 : 7; E(x + (7 - w) / 2, y + 4 + yy, w, 1, yy % 2 ? '#ff5a4a' : '#ff7a55', .8); }
          R(x + 3, y + 5, 1, 6, 'rgba(255,230,190,.55)'); R(x + 1, y + 12, 5, 1, '#07060f'); R(x + 3, y + 13, 1, 2, '#ffc36b');
        }
        else if (k === 'noren') {
          if (!vis(it.y, 12)) continue; R(1, it.y, W - 2, 1, '#3a3168');
          for (let x = 2; x < W - 2; x += 6) R(x, it.y + 1, 5, 10, it.c);
          const cx = Math.floor(W / 2); R(cx - 2, it.y + 4, 5, 3, 'rgba(244,239,233,.75)'); R(cx - 1, it.y + 3, 3, 5, 'rgba(244,239,233,.75)');
        }
        else if (k === 'word') {
          if (!vis(it.y, 9)) continue; const off = !still && hash(Math.floor(t * 12), it.ph) < 0.05;
          R(it.x - 2, it.y - 2, it.w.length * 4 + 3, 9, '#0c0a1b');
          [...it.w].forEach((ch, j) => { const f = FONT[ch]; if (!f) return; for (let q = 0; q < 15; q++) if (f[q] === '1') { const px = it.x + j * 4 + q % 3, py = it.y + (q / 3 | 0); off ? R(px, py, 1, 1, 'rgba(255,255,255,.1)') : E(px, py, 1, 1, it.c, .9); } });
        }
        else if (k === 'vend') {
          if (!vis(it.y, 25)) continue; const x = it.x, y = it.y;
          h.globalAlpha = .2; h.fillStyle = '#bfefff'; h.fillRect(x - 3, y - 2 - oy, 19, 30); h.globalAlpha = 1;
          R(x, y, 13, 24, it.c); R(x + 12, y, 1, 24, 'rgba(0,0,0,.2)'); E(x + 1, y + 1, 11, 4, '#f4efe9', .5);
          E(x + 1, y + 6, 11, 10, '#d6f6ff', .6);
          const cans = ['#ff7a63', '#5ee6ff', '#ffc36b', '#3ee08a', '#ff8ad1', '#9d7bff'];
          for (let rr = 0; rr < 3; rr++) for (let cc = 0; cc < 4; cc++) R(x + 2 + cc * 3, y + 7 + rr * 3, 2, 2, cans[(rr * 4 + cc + Math.floor(it.seed * 6)) % 6]);
          R(x + 2, y + 18, 9, 3, '#1a1534'); R(x + 9, y + 17, 2, 1, '#07060f');
        }
        else if (k === 'balcony') {
          if (!vis(it.y, 12)) continue; const y = it.y;
          R(2, y + 9, W - 4, 1, '#3a3168'); for (let x = 3; x < W - 3; x += 3) R(x, y + 9, 1, 4, '#2c2452'); R(2, y + 13, W - 4, 1, '#3a3168');
          R(3, y, W - 6, 1, 'rgba(255,255,255,.18)');
          it.cloth.forEach((c, j) => { const x = 5 + j * Math.floor((W - 10) / 4); if (x + 4 < W) { R(x, y + 1, 4, 5, c); R(x + 1, y + 6, 2, 1, c); } });
        }
        else if (k === 'stairs') {
          if (!vis(it.y, it.F)) continue; const n = Math.floor((W - 8) / 3), y0 = it.y + 6;
          for (let i = 0; i < n; i++) { const x = it.dir > 0 ? 4 + i * 3 : W - 7 - i * 3, yy = y0 + Math.round(i * (it.F - 14) / n);
            R(x, yy, 4, 1, '#3d3470'); R(x, yy + 1, 4, 1, '#1d1838'); if (i % 4 === 0) R(x + 1, yy - 6, 1, 6, '#2c2452'); }
          for (let i = 0; i < n * 3; i++) { const x = it.dir > 0 ? 4 + i : W - 4 - i, yy = y0 - 6 + Math.round((i / 3) * (it.F - 14) / n); R(x, yy, 1, 1, '#4a4080'); }
          R(0, it.y + it.F - 8, W, 2, '#2c2452'); R(0, it.y + it.F - 8, W, 1, 'rgba(255,255,255,.08)');
        }
        else if (k === 'board') {
          if (!vis(it.y, 30)) continue; const x0 = 4, w = W - 8, hh = 26, y = it.y, ad = still ? 0 : Math.floor((t + it.ph) / 7) % 2;
          R(x0 - 1, y - 1, w + 2, hh + 2, '#2c2452'); R(x0 + 2, y + hh + 1, 1, 4, '#2c2452'); R(x0 + w - 3, y + hh + 1, 1, 4, '#2c2452');
          if (ad === 0) {                                                      // the street's own sunset: Fuji
            const sky = ['#ff8ad1', '#ff9a8a', '#ffb36e', '#ffc36b', '#ff7a63'];
            for (let yy = 0; yy < hh; yy++) E(x0, y + yy, w, 1, sky[Math.min(4, Math.floor(yy / hh * 5))], .55);
            const mx = x0 + Math.floor(w * 0.55); for (let yy = 0; yy < 12; yy++) { const half = Math.round(yy * 1.6) + 1; R(mx - half, y + hh - 12 + yy, 2 * half, 1, yy < 3 ? '#f4efe9' : '#3a2a5a'); }
            E(x0 + 5, y + 5, 4, 4, '#fff2c8', .8);
          } else {                                                             // a black cat, eyes lit, on the neon pink
            for (let yy = 0; yy < hh; yy++) E(x0, y + yy, w, 1, yy % 2 ? '#c77be8' : '#b46ee0', .45);
            const cx = x0 + Math.floor(w / 2) - 5; bmp(['#....#....', '##..##....', '######....', '#.##.#....', '######..#.', '.####...#.', '.######.#.', '.#######..', '.#######..'], cx, y + hh - 11, (px, py) => R(px, py, 1, 1, '#07060f'));
            E(cx + 1, y + hh - 8, 1, 1, '#ffc36b'); E(cx + 4, y + hh - 8, 1, 1, '#ffc36b');
          }
        }
        else if (k === 'shoji') {
          if (!vis(it.y, it.F)) continue; const w = Math.min(W - 10, 26), x0 = Math.floor((W - w) / 2), y = it.y, hh = it.F - 22;
          h.globalAlpha = .22; h.fillStyle = '#ffc070'; h.fillRect(x0 - 6, y - 4 - oy, w + 12, hh + 10); h.globalAlpha = 1;
          R(x0 - 2, y - 2, w + 4, hh + 2, '#1d1838'); for (let yy = 0; yy < hh; yy++) E(x0, y + yy, w, 1, '#ffd9a0', .5);
          for (let x = x0 + 4; x < x0 + w; x += 5) R(x, y, 1, hh, '#6a4a3a'); for (let yy = y + 4; yy < y + hh; yy += 5) R(x0, yy, w, 1, '#6a4a3a');
          R(x0 + Math.floor(w / 2), y, 1, hh, '#3a2a2a');
        }
        else if (k === 'wire') {
          if (!vis(it.y, 10)) continue;
          for (let x = 0; x < W; x++) { const u = x / W, yy = it.y + Math.round(4 * it.sag * u * (1 - u)); R(x, yy, 1, 1, '#07060f'); }
          for (let c = 0; c < it.crows; c++) { const u = (c + 1) / (it.crows + 1) + (it.seed - .5) * .1, x = Math.round(u * W), yy = it.y + Math.round(4 * it.sag * u * (1 - u));
            bmp(['.##.', '####', '.##.'], x - 2, yy - 3, (px, py) => R(px, py, 1, 1, '#07060f')); R(x + (it.seed > .5 ? 1 : -2), yy - 3, 1, 1, '#07060f'); }
        }
      }
      const fade = 60 - oy; if (fade > 0) { const gr = g.createLinearGradient(0, 0, 0, fade); gr.addColorStop(0, 'rgba(15,12,34,1)'); gr.addColorStop(1, 'rgba(15,12,34,0)'); g.fillStyle = gr; g.fillRect(0, 0, W, fade); h.clearRect(0, 0, W, Math.max(0, fade - 30)); }
    }
    function frame() {
      if (!on) return;
      const pr = pg.getBoundingClientRect(), topCss = Math.max(0, -pr.top), top = Math.floor(topCss / P), rows = Math.ceil(innerHeight / P) + 2;
      for (const S of sides) {
        for (const c of [S.base, S.glow]) { if (c.width !== S.W || c.height !== rows) { c.width = S.W; c.height = rows; c.style.width = S.W * P + 'px'; c.style.height = rows * P + 'px'; } c.style.transform = `translateY(${-(topCss - top * P)}px)`; }
        S.g.imageSmoothingEnabled = false; draw(S, top, rows);
      }
    }
    function layout() {
      const pr = pg.getBoundingClientRect(), cr = ct.getBoundingClientRect(), room = Math.floor(cr.left - pr.left - 36);
      on = room >= 110;
      sides.forEach((S) => { S.wrap.style.display = on ? '' : 'none'; });
      if (!on) return;
      P = room >= 220 ? 4 : 3; Hh = Math.ceil(pg.offsetHeight / P);
      sides.forEach((S, k) => { S.wrap.style.width = room + 'px'; S.W = Math.floor(room / P); S.items = populate(S.W, Hh, rnd('wall' + k), S.side === 'left'); });
      frame();
    }
    layout();
    let lt = 0; const later = () => { clearTimeout(lt); lt = setTimeout(layout, 150); };
    addEventListener('resize', later); addEventListener('load', later);
    if ('ResizeObserver' in window) new ResizeObserver(later).observe(ct);
    let raf = 0; addEventListener('scroll', () => { if (!raf) raf = requestAnimationFrame(() => { raf = 0; frame(); }); }, { passive: true });
    if (!still) {
      if ('IntersectionObserver' in window) new IntersectionObserver((es) => { seen = es[0].isIntersecting; }).observe(pg); else seen = true;
      let acc = 0, last = 0;
      (function loop(now) { if (seen && on && !document.hidden) { acc += Math.min(0.1, (now - (last || now)) / 1000); if (acc > 1 / 12) { t += acc; acc = 0; frame(); } } last = now; requestAnimationFrame(loop); })(performance.now());
    }
  }
  walls();
})();
