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
    const blocks = document.querySelectorAll('.page .section-head, .page .split > *, .page .stats > li, .page .entries-grid > li, .page .projects > li, .page .chips.tools, .page .pub, .page .cta, .page .more, .page .masthead > *, .page .prose > *, .page .chrono');
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

  // ---- FIG. 01, the research drawn: a grid (a model's space of behaviours), a few explorers that each set themselves a
  // goal, walk to it cell by cell and leave a fading trail, so the grid is slowly mapped. Pixels, like the street.
  // <canvas class="fig-map" data-seed="…"></canvas> (4:3); still (already mapped) under reduced motion
  document.querySelectorAll('canvas.fig-map').forEach((cv) => {
    const W = 96, H = 72, CELL = 6, cols = W / CELL, rows = H / CELL;
    cv.width = W; cv.height = H;
    const g = cv.getContext('2d'), R = rnd(cv.dataset.seed || 'fig'), map = new Float32Array(cols * rows), hue = new Uint8Array(cols * rows);
    const COL = [[255, 138, 209], [94, 230, 255], [255, 195, 107]];
    const agents = [0, 1, 2].map((k) => ({ x: Math.floor(R() * cols), y: Math.floor(R() * rows), gx: 0, gy: 0, k, wait: R(), step: 0 }));
    const goal = (a) => { a.gx = Math.floor(R() * cols); a.gy = Math.floor(R() * rows); };
    agents.forEach(goal);
    function tick(dt) {
      for (const a of agents) {
        if (a.wait > 0) { a.wait -= dt; continue; }
        a.step += dt; if (a.step < 0.22) continue; a.step = 0;
        if (a.x === a.gx && a.y === a.gy) { a.wait = 0.5 + R(); goal(a); continue; }
        if (a.x !== a.gx && (a.y === a.gy || R() < 0.5)) a.x += Math.sign(a.gx - a.x); else a.y += Math.sign(a.gy - a.y);
        map[a.y * cols + a.x] = 1; hue[a.y * cols + a.x] = a.k;
      }
      for (let i = 0; i < map.length; i++) if (map[i] > 0.18) map[i] = Math.max(0.18, map[i] - dt * 0.05);
    }
    function draw() {
      g.clearRect(0, 0, W, H);
      for (let r = 0; r < rows; r++) for (let c = 0; c < cols; c++) {
        const v = map[r * cols + c], x = c * CELL, y = r * CELL;
        if (v > 0) { const [cr, cg, cb] = COL[hue[r * cols + c]]; g.fillStyle = `rgba(${cr},${cg},${cb},${0.1 + 0.55 * v})`; g.fillRect(x + 1, y + 1, CELL - 2, CELL - 2); }
        else { g.fillStyle = 'rgba(205,198,220,.14)'; g.fillRect(x + 2, y + 2, 2, 2); }
      }
      for (const a of agents) { const [cr, cg, cb] = COL[a.k]; g.fillStyle = `rgba(${cr},${cg},${cb},.25)`; g.fillRect(a.x * CELL - 1, a.y * CELL - 1, CELL + 2, CELL + 2); g.fillStyle = '#fff'; g.fillRect(a.x * CELL + 1, a.y * CELL + 1, CELL - 2, CELL - 2); }
    }
    for (let k = 0; k < (still ? 900 : 60); k++) tick(0.1);   // (a little mapped already; much more when it will not move)
    draw();
    if (still) return;
    let on = false, last = 0;
    if ('IntersectionObserver' in window) new IntersectionObserver((es) => { on = es[0].isIntersecting; }).observe(cv); else on = true;
    (function loop(now) { if (on && !document.hidden) { tick(Math.min(0.1, (now - (last || now)) / 1000)); draw(); last = now; } else last = 0; requestAnimationFrame(loop); })(performance.now());
  });
})();
