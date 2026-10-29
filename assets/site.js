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


  const en = () => document.documentElement.lang === 'en';
  // ---- the table of contents: in once the street is passed, the section being read lit (and kept in view on a phone)
  const toc = document.querySelector('.toc'), hero = document.querySelector('.hero');
  if (toc && 'IntersectionObserver' in window) {
    if (hero) new IntersectionObserver((es) => toc.classList.toggle('on', !es[0].isIntersecting), { rootMargin: '-60px 0px 0px 0px' }).observe(hero);
    else toc.classList.add('on');
    const links = [...toc.querySelectorAll('.toc-links a')], byId = new Map(links.map((a) => [a.getAttribute('href').slice(1), a]));
    const io2 = new IntersectionObserver((es) => es.forEach((e) => {
      if (!e.isIntersecting) return; const a = byId.get(e.target.id); if (!a) return;
      links.forEach((l) => l.classList.toggle('on', l === a));
      const box = a.parentElement; if (box.scrollWidth > box.clientWidth) box.scrollTo({ left: a.offsetLeft - box.clientWidth / 2 + a.offsetWidth / 2, behavior: still ? 'auto' : 'smooth' });
    }), { rootMargin: '-38% 0px -58% 0px' });
    byId.forEach((a, id) => { const sec = document.getElementById(id); if (sec) io2.observe(sec); });
  }

  // ---- copy a citation: <button class="bib-copy" data-target="id-of-the-pre" data-done-fr="…" data-done-en="…">
  function copy(text) {
    if (navigator.clipboard && window.isSecureContext) return navigator.clipboard.writeText(text);
    return new Promise((ok, ko) => { const t = document.createElement('textarea'); t.value = text; t.style.position = 'fixed'; t.style.opacity = '0'; document.body.appendChild(t); t.select();
      try { document.execCommand('copy') ? ok() : ko(); } catch (e) { ko(e); } t.remove(); });
  }
  document.querySelectorAll('.bib-copy').forEach((b) => b.addEventListener('click', () => {
    const pre = document.getElementById(b.dataset.target); if (!pre) return;
    const label = b.innerHTML;
    copy(pre.textContent.trim()).then(() => { b.classList.add('done'); b.textContent = en() ? b.dataset.doneEn : b.dataset.doneFr; setTimeout(() => { b.classList.remove('done'); b.innerHTML = label; }, 1800); }, () => { pre.hidden = false; });
  }));

  // ---- subscribe: a small panel with the feed's address, to copy into a reader (the raw XML is not for people)
  const FEED = 'https://mtsfj.github.io/blog/feed.xml';
  document.querySelectorAll('.rss-btn').forEach((b) => b.addEventListener('click', (ev) => {
    ev.stopPropagation();
    const host = b.parentElement, old = host.querySelector('.rss-pop'); if (old) { old.remove(); return; }
    const pop = document.createElement('div'); pop.className = 'rss-pop'; pop.setAttribute('role', 'dialog');
    pop.innerHTML = (en() ? '<p>Copy this address into your feed reader (Feedly, NetNewsWire, Inoreader…) to get the new posts.</p>' : '<p>Copiez cette adresse dans votre lecteur de flux (Feedly, NetNewsWire, Inoreader…) pour recevoir les nouveaux billets.</p>')
      + `<div class="row"><input type="text" readonly value="${FEED}" aria-label="RSS"><button type="button">${en() ? 'Copy' : 'Copier'}</button></div>`;
    host.appendChild(pop);
    const inp = pop.querySelector('input'), cb = pop.querySelector('button'); inp.addEventListener('focus', () => inp.select());
    cb.addEventListener('click', () => copy(FEED).then(() => { cb.textContent = en() ? 'Copied ✓' : 'Copié ✓'; }, () => inp.select()));
    const close = (e) => { if (e.type === 'keydown' ? e.key === 'Escape' : !pop.contains(e.target)) { pop.remove(); document.removeEventListener('click', close); document.removeEventListener('keydown', close); } };
    setTimeout(() => { document.addEventListener('click', close); document.addEventListener('keydown', close); });
  }));

  // ---- the shelf's cat: the street's black cat, sitting at the end of the books, its eyes lit (they blink)
  document.querySelectorAll('canvas.shelf-cat').forEach((cv) => {
    const g = cv.getContext('2d'), CAT = ['.#...#........', '.##.##........', '.#####........', '.#o#o#........', '.#####......#.', '..####......#.', '..#####....#..', '..########.#..', '..#########...', '..#########...', '..#########...', '..##.##.##....'];
    const draw = (open) => { g.clearRect(0, 0, 14, 12); CAT.forEach((row, y) => [...row].forEach((c, x) => { if (c === '.') return; g.fillStyle = c === 'o' ? (open ? '#ffc36b' : '#07060f') : '#07060f'; g.fillRect(x, y, 1, 1); })); };
    draw(true);
    if (!still) (function blink() { setTimeout(() => { draw(false); setTimeout(() => { draw(true); blink(); }, 160); }, 2500 + Math.random() * 4000); })();
  });

  // ---- the library: a book under the pointer (or focus) gives its title, authors, year, venue, theme beneath the shelf
  document.querySelectorAll('.library').forEach((lib) => {
    const cap = lib.querySelector('.shelf-caption'), books = [...lib.querySelectorAll('.book')];
    const esc = (t) => t.replace(/[&<>"]/g, (c) => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c]));
    const touch = matchMedia('(hover: none)').matches;
    const hint = () => { cap.innerHTML = touch ? (en() ? 'Tap a book to open it · a star: a classic, or most followed' : 'Touchez un livre pour l’ouvrir · une étoile : un classique, ou le plus suivi')
      : (en() ? 'Point at a book to see it · a star: a classic, or most followed' : 'Survolez un livre pour le voir · une étoile : un classique, ou le plus suivi'); books.forEach((b) => b.classList.remove('on')); };
    const show = (b) => { books.forEach((x) => x.classList.toggle('on', x === b)); const d = b.dataset;
      const bits = [esc(d.authors), d.year ? `<span class="yr">${d.year}</span>` : '', d.venue && d.venue !== 'YouTube' ? esc(d.venue) : '', d.n ? `${d.n} ${en() ? 'videos' : 'vidéos'}` : '', en() ? d.themeEn : d.themeFr].filter(Boolean);
      cap.innerHTML = `<b>${d.title}</b><br>${bits.join(' · ')}`; };
    books.forEach((b) => { b.addEventListener('mouseenter', () => show(b)); b.addEventListener('focus', () => show(b)); });
    lib.addEventListener('mouseleave', hint); lib.addEventListener('focusout', (e) => { if (!lib.contains(e.relatedTarget)) hint(); });
    document.querySelectorAll('button.lang').forEach((x) => x.addEventListener('click', () => setTimeout(hint)));
    hint();
  });
})();
