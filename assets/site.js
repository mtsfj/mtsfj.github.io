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
})();
