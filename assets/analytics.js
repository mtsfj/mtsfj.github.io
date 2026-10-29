/* mtsfj.github.io · analytics, in one place. Off until PROVIDER and ID are set below.
   The providers here are cookieless (no consent banner needed under the GDPR / CNIL rules for audience measurement):
     'goatcounter'  ID = the site code (the CODE in https://CODE.goatcounter.com), free for a personal site
     'plausible'    ID = the domain as declared in Plausible (mtsfj.github.io)
     'umami'        ID = the website id (Umami Cloud, or SRC below for a self-hosted instance)
     'cloudflare'   ID = the Web Analytics beacon token
   Besides the page views, a few clicks are counted as events: the email shown, the CV, the language switch, every
   link out of the site (GitHub, arXiv, Scholar, LinkedIn…). Nothing is sent from localhost or a file. */
(function () {
  const PROVIDER = 'goatcounter';   // 'goatcounter' | 'plausible' | 'umami' | 'cloudflare'
  const ID = 'mtsfj';               // https://mtsfj.goatcounter.com (private dashboard)
  const SRC = '';               // (umami only: a self-hosted script's URL; empty for Umami Cloud)
  if (!PROVIDER || !ID || /^(localhost|127\.|0\.0\.0\.0)/.test(location.hostname) || location.protocol === 'file:') return;

  const load = (src, attrs) => { const s = document.createElement('script'); s.async = true; s.src = src; for (const k in attrs) s.setAttribute(k, attrs[k]); document.head.appendChild(s); };
  if (PROVIDER === 'goatcounter') load('https://gc.zgo.at/count.js', { 'data-goatcounter': `https://${ID}.goatcounter.com/count` });
  else if (PROVIDER === 'plausible') load('https://plausible.io/js/script.js', { 'data-domain': ID, defer: '' });
  else if (PROVIDER === 'umami') load(SRC || 'https://cloud.umami.is/script.js', { 'data-website-id': ID, defer: '' });
  else if (PROVIDER === 'cloudflare') load('https://static.cloudflareinsights.com/beacon.min.js', { 'data-cf-beacon': JSON.stringify({ token: ID }), defer: '' });

  function track(name) {
    try {
      if (PROVIDER === 'goatcounter' && window.goatcounter && window.goatcounter.count) window.goatcounter.count({ path: name, title: name, event: true });
      else if (PROVIDER === 'plausible' && window.plausible) window.plausible(name);
      else if (PROVIDER === 'umami' && window.umami) window.umami.track(name);
    } catch (e) { /* a lost event is not worth an error */ }
  }
  document.addEventListener('click', (e) => {
    const el = e.target.closest && e.target.closest('a, button'); if (!el) return;
    if (el.classList.contains('mail-reveal')) return track('email');
    if (el.classList.contains('lang')) return track('lang');
    if (el.classList.contains('bib-copy')) return track('cite');
    if (el.classList.contains('rss-btn')) return track('rss');
    const href = el.getAttribute && el.getAttribute('href'); if (!href) return;
    if (/\.pdf(\?|$)/.test(href) && !/^https?:/.test(href)) return track('cv');
    try { const u = new URL(href, location.href); if (u.hostname && u.hostname !== location.hostname) track('out: ' + u.hostname.replace(/^www\./, '')); } catch (err) {}
  }, { capture: true, passive: true });
})();
