// ==== the arcade's games: the three cabinets and the claw machine of the room behind the arcade's door (assets/street.js, its
// section "arcade entrance on the right"), each playing the game its screen shows in the owner's drawing (tools/src/arcade_wall.webp).
// Loaded by street.js at the first click on a machine (never with the page): window.ARCADE.open(machine, { kb, onPlay }).
//   0, the first cabinet: HOSHIKUZU (ホシクズ, stardust), a fixed shooter on its teal screen: the lone big alien at the top, the
//      rows of small ones under it, the cannon at the bottom, mint on teal
//   1, the second: YUHI DRIVE (ユウヒ ドライブ, sunset drive), a road racer into the pink sunset, the striped sun, the purple city
//   2, the third (cut by the picture's edge; the room tool gives it the first one's face): HOSHIKUZU again, its own high scores
//   3, the claw machine: KUMA SUKUI (クマスクイ, bear scooping), its pink-lit glass, its claw and its plush bears
// Each game its own small canvas at its own low resolution (the screen's shape in the drawing), its sprites drawn here pixel by
// pixel in a handful of colours taken from that screen; the machine's face around it (marquee, bezel, control deck, coin door)
// drawn the same way, one canvas shown at a whole number of device pixels per pixel (crisp at any zoom). The deck's joystick
// and buttons are the touch controls, and light up under the keyboard's keys. Original games, names and sprites (genres only:
// a fixed shooter, a pseudo-3D road racer, a crane game). No sound, as the rest of the site ----
(function () {
  'use strict';
  if (window.ARCADE) return;
  const reduced = window.matchMedia('(prefers-reduced-motion: reduce)').matches;   // (still playable: no shake, no flashing)
  const coarse = window.matchMedia('(pointer: coarse)').matches;
  const STEP = 1 / 60;                          // the games' fixed step
  const lang = () => (document.documentElement.lang === 'en' ? 'en' : 'fr');
  const rnd = (a, b) => a + Math.random() * (b - a), clamp = (v, a, b) => (v < a ? a : v > b ? b : v);
  const pick = (a) => a[Math.floor(Math.random() * a.length)];

  // ---- the texts: on the screens (the 3 x 5 font below: capitals, digits, a few accents) and around them, in the page's
  // language at the moment (read each frame: a language switch shows at once) ----
  const TX = {
    fr: { coin: 'INSÉREZ UNE PIÈCE', start: 'APPUYEZ SUR START', credit: 'CRÉDIT', over: 'FIN DE PARTIE', hs: 'MEILLEURS SCORES',
      rec: 'NOUVEAU RECORD !', ini: 'VOS INITIALES', pause: 'PAUSE', resume: 'START OU P : REPRENDRE', ranks: ['1ER', '2E', '3E', '4E', '5E'],
      keysIni: '↑↓ LETTRE  ← → A : OK', free: 'PARTIE GRATUITE',
      wave: 'VAGUE', bonus: 'BONUS', p1: 'JOUEUR 1', pts: 'PTS', extra: 'VIE EN PLUS', hInfo: ['← → BOUGER', 'A OU B TIRER', 'ABATTEZ LE GRAND', 'POUR UN BONUS'],
      time: 'TEMPS', cp: 'ÉTAPE !', timeup: 'TEMPS ÉCOULÉ', go: 'PARTEZ !', kmh: 'KM/H', dist: 'KM', yInfo: ['← → VOLANT', 'A OU ↑ GAZ', 'B OU ↓ FREIN', 'CHAQUE ÉTAPE', 'DONNE DU TEMPS'],
      tries: 'ESSAIS', win: 'GAGNÉ !', miss: 'RATÉ', slip: 'TOMBÉ !', kInfo: ['← → PUIS A', '↑ ↓ PUIS A', 'LA PINCE DESCEND', 'LES PELUCHES', 'DANS LA TRAPPE'],
      close: 'Fermer', prev: 'machine précédente', next: 'machine suivante', kb: "Jouer à l'arcade",
      mach: ['borne 1', 'borne 2', 'borne 3', 'machine à pinces'],
      help: 'flèches · espace · entrée : pièce, start · P : pause · échap',
      helpK: ['A', 'B', 'START', 'PIÈCE', 'PINCE'],
      face: (n, g) => n + ', ' + g + '. Flèches ou WASD, espace, Z et X pour jouer ; entrée ou 5 pour une pièce, puis start ; P pour la pause ; échap pour quitter.',
      said: { start: 'partie commencée', over: 'fin de partie : ', pts: ' points', rec: 'nouveau record, entrez vos initiales', paused: 'en pause', coin: 'crédit ' } },
    en: { coin: 'INSERT COIN', start: 'PRESS START', credit: 'CREDIT', over: 'GAME OVER', hs: 'HIGH SCORES',
      rec: 'NEW HIGH SCORE!', ini: 'ENTER YOUR INITIALS', pause: 'PAUSED', resume: 'START OR P: RESUME', ranks: ['1ST', '2ND', '3RD', '4TH', '5TH'],
      keysIni: '↑↓ LETTER  ← → A: OK', free: 'FREE PLAY',
      wave: 'WAVE', bonus: 'BONUS', p1: 'PLAYER 1', pts: 'PTS', extra: 'EXTRA LIFE', hInfo: ['← → MOVE', 'A OR B FIRE', 'DOWN THE BIG ONE', 'FOR A BONUS'],
      time: 'TIME', cp: 'CHECKPOINT!', timeup: 'TIME UP', go: 'GO!', kmh: 'KM/H', dist: 'KM', yInfo: ['← → STEER', 'A OR ↑ GAS', 'B OR ↓ BRAKE', 'EACH CHECKPOINT', 'GIVES MORE TIME'],
      tries: 'TRIES', win: 'WIN!', miss: 'MISSED', slip: 'DROPPED!', kInfo: ['← → THEN A', '↑ ↓ THEN A', 'THE CLAW DROPS', 'GET THE PLUSHIES', 'INTO THE CHUTE'],
      close: 'Close', prev: 'previous machine', next: 'next machine', kb: 'Play the arcade',
      mach: ['cabinet 1', 'cabinet 2', 'cabinet 3', 'claw machine'],
      help: 'arrows · space · enter: coin, start · P: pause · esc',
      helpK: ['A', 'B', 'START', 'COIN', 'CLAW'],
      face: (n, g) => n + ', ' + g + '. Arrows or WASD, space, Z and X to play; enter or 5 for a coin, then start; P to pause; escape to leave.',
      said: { start: 'game started', over: 'game over: ', pts: ' points', rec: 'new high score, enter your initials', paused: 'paused', coin: 'credit ' } } };
  const T = () => TX[lang()];

  // ---- pixels. A sprite: rows of characters, '.' clear and each other one a key into its palette; made once into a canvas at 1:1
  // (drawn with drawImage, smoothing off: never scaled but by the racer's nearest-neighbour depth, as the old sprite chips did) ----
  function R(g, x, y, w, h, c) { g.fillStyle = c; g.fillRect(x, y, w, h); }
  function sprite(rows, pal) {
    const c = document.createElement('canvas'); c.width = rows[0].length; c.height = rows.length;
    const g = c.getContext('2d');
    for (let y = 0; y < rows.length; y++) for (let x = 0; x < rows[y].length; x++) { const k = rows[y][x]; if (k !== '.' && pal[k]) R(g, x, y, 1, 1, pal[k]); }
    return c;
  }
  function canvas(w, h) { const c = document.createElement('canvas'); c.width = w; c.height = h; const g = c.getContext('2d'); g.imageSmoothingEnabled = false; return [c, g]; }
  function ellipse(g, cx, cy, rx, ry, col) {   // a filled ellipse of whole pixels, row by row (its centre between pixels: cx, cy at a pixel's corner)
    for (let y = -ry; y < ry; y++) { const v = (y + 0.5) / ry, hw = Math.round(rx * Math.sqrt(Math.max(0, 1 - v * v))); if (hw > 0) R(g, cx - hw, cy + y, hw * 2, 1, col); }
  }

  // ---- the font: 3 x 5 capitals (M, N, W wider), digits, punctuation, arrows; É È À as their letter with a dot two rows
  // above (the lines are 8 rows apart), Ç with a dot under. Each glyph its rows, '/' between them ----
  const FONT = { A: '.X./X.X/XXX/X.X/X.X', B: 'XX./X.X/XX./X.X/XX.', C: '.XX/X../X../X../.XX', D: 'XX./X.X/X.X/X.X/XX.', E: 'XXX/X../XX./X../XXX',
    F: 'XXX/X../XX./X../X..', G: '.XX/X../X.X/X.X/.XX', H: 'X.X/X.X/XXX/X.X/X.X', I: 'XXX/.X./.X./.X./XXX', J: '..X/..X/..X/X.X/.X.',
    K: 'X.X/X.X/XX./X.X/X.X', L: 'X../X../X../X../XXX', M: 'X...X/XX.XX/X.X.X/X...X/X...X', N: 'X..X/XX.X/X.XX/X..X/X..X',
    O: '.X./X.X/X.X/X.X/.X.', P: 'XX./X.X/XX./X../X..', Q: '.X./X.X/X.X/XX./.XX', R: 'XX./X.X/XX./X.X/X.X', S: '.XX/X../.X./..X/XX.',
    T: 'XXX/.X./.X./.X./.X.', U: 'X.X/X.X/X.X/X.X/XXX', V: 'X.X/X.X/X.X/X.X/.X.', W: 'X...X/X...X/X.X.X/XX.XX/X...X', X: 'X.X/X.X/.X./X.X/X.X',
    Y: 'X.X/X.X/.X./.X./.X.', Z: 'XXX/..X/.X./X../XXX',
    0: 'XXX/X.X/X.X/X.X/XXX', 1: '.X./XX./.X./.X./XXX', 2: 'XX./..X/.X./X../XXX', 3: 'XX./..X/.X./..X/XX.', 4: 'X.X/X.X/XXX/..X/..X',
    5: 'XXX/X../XX./..X/XX.', 6: '.XX/X../XXX/X.X/XXX', 7: 'XXX/..X/.X./.X./.X.', 8: 'XXX/X.X/XXX/X.X/XXX', 9: 'XXX/X.X/XXX/..X/XX.',
    ' ': '../../../../..', '.': '././././X', ',': '../../../.X/X.', ':': './X/./X/.', '!': 'X/X/X/./X', '?': 'XX./..X/.X./.../.X.',
    '-': '.../.../XXX/.../...', '+': '.../.X./XXX/.X./...', '/': '..X/..X/.X./X../X..', "'": 'X/X/././.', '(': '.X/X./X./X./.X', ')': 'X./.X/.X/.X/X.',
    '←': '..../.X../XXXX/.X../....', '→': '..../..X./XXXX/..X./....', '↑': '.X./XXX/.X./.X./.X.', '↓': '.X./.X./.X./XXX/.X.', '·': '././X/./.',
    '=': '.../XXX/.../XXX/...', '%': 'X.X/..X/.X./X../X.X' };
  const ACC = { 'É': ['E', 2, -2], 'È': ['E', 0, -2], 'À': ['A', 0, -2], 'Ç': ['C', 1, 5], 'Ê': ['E', 1, -2] };
  const GLY = {};                               // char -> { w, px: [[x, y], ...] }
  function glyph(ch) {
    if (GLY[ch]) return GLY[ch];
    let src = FONT[ch], dot = null;
    if (!src && ACC[ch]) { src = FONT[ACC[ch][0]]; dot = [ACC[ch][1], ACC[ch][2]]; }
    if (!src) src = FONT['?'];
    const rows = src.split('/'), px = [];
    rows.forEach((r, y) => { for (let x = 0; x < r.length; x++) if (r[x] === 'X') px.push([x, y]); });
    if (dot) px.push(dot);
    return (GLY[ch] = { w: rows[0].length, px });
  }
  function textW(s, k) { k = k || 1; let w = 0; for (const ch of s) w += glyph(ch).w + 1; return Math.max(0, w - 1) * k; }
  // a string at (x, y) (its top-left; 'c' centres it on x, 'r' ends it at x), k pixels a dot; sh: a shadow colour, a pixel down-right
  function text(g, s, x, y, col, k, al, sh) {
    k = k || 1; s = String(s);
    if (al === 'c') x = Math.round(x - textW(s, k) / 2); else if (al === 'r') x -= textW(s, k);
    if (sh) text(g, s, x + k, y + k, sh, k);
    g.fillStyle = col;
    for (const ch of s) { const G = glyph(ch); for (const [px, py] of G.px) g.fillRect(x + px * k, y + py * k, k, k); x += (G.w + 1) * k; }
  }
  // ---- katakana for the titles (7 rows; those with the voicing marks wider), drawn as the marquees and the title screens show them
  const KANA = {
    'ホ': ['...X...', 'XXXXXXX', '...X...', '.X.X.X.', 'X..X..X', '...X...', '..XX...'],
    'シ': ['XX.....', '......X', 'XX...X.', '....X..', '...X...', '.XX....', 'X......'],
    'ク': ['..X....', '.XXXXXX', 'X.....X', '.....X.', '....X..', '..XX...', 'XX.....'],
    'ズ': ['XXXXX.X.X', '....X.X.X', '...X.....', '..X......', '.X.X.....', 'X...X....', '.....X...'],
    'ユ': ['.......', 'XXXXX..', '....X..', '....X..', '....X..', 'XXXXXXX', '.......'],
    'ウ': ['...X...', 'XXXXXXX', 'X.....X', 'X....X.', '....X..', '...X...', 'XX.....'],
    'ヒ': ['X......', 'X....XX', 'XXXXX..', 'X......', 'X......', 'X......', '.XXXXXX'],
    'ド': ['.X..X.X', '.X..X.X', '.XXX...', '.X..X..', '.X.....', '.X.....', '.X.....'],
    'ラ': ['.XXXXX.', '.......', 'XXXXXXX', '......X', '.....X.', '...XX..', 'XX.....'],
    'イ': ['......X', '....XX.', '..XX...', 'XX.X...', '...X...', '...X...', '...X...'],
    'ブ': ['XXXXX.X.X', '....X.X.X', '....X....', '...X.....', '..X......', '.X.......', 'X........'],
    'マ': ['XXXXXXX', '......X', '.....X.', '.X..X..', '..XX...', '...X...', '....X..'],
    'ス': ['XXXXX..', '....X..', '...X...', '..X....', '.X.X...', 'X...X..', '.....X.'] };
  function kanaW(s) { let w = 0; for (const ch of s) w += ch === ' ' ? 4 : KANA[ch][0].length + 1; return Math.max(0, w - 1); }
  function kana(g, s, x, y, col, al) {
    if (al === 'c') x = Math.round(x - kanaW(s) / 2);
    g.fillStyle = col;
    for (const ch of s) {
      if (ch === ' ') { x += 4; continue; }
      const rows = KANA[ch];
      rows.forEach((r, yy) => { for (let xx = 0; xx < r.length; xx++) if (r[xx] === 'X') g.fillRect(x + xx, y + yy, 1, 1); });
      x += rows[0].length + 1;
    }
  }
  const pad = (n, w) => String(Math.max(0, Math.floor(n))).padStart(w, '0');

  // ---- the high scores: one table of five a machine (the third cabinet its own: another machine), seeded as the fuse box's
  // display (MTF 160303, AAA, CPU), in localStorage; every access in a try (a private window, blocked storage: the seeds) ----
  const HS_SEED = [['MTF', 160303], ['AAA', 100000], ['CPU', 64000], ['AAA', 32000], ['CPU', 16000]];
  function hsLoad(key) {
    try { const v = JSON.parse(localStorage.getItem(key)); if (Array.isArray(v) && v.length === 5 && v.every((e) => Array.isArray(e) && typeof e[0] === 'string' && Number.isFinite(e[1]))) return v.map((e) => [e[0].slice(0, 3), Math.floor(e[1])]); } catch (e) {}
    return HS_SEED.map((e) => e.slice());
  }
  function hsSave(key, tab) { try { localStorage.setItem(key, JSON.stringify(tab)); } catch (e) {} }
  function iniLoad() { try { const v = localStorage.getItem('mtsfj-arcade-ini'); if (v && /^[A-Z.]{3}$/.test(v)) return v; } catch (e) {} return 'AAA'; }
  function iniSave(v) { try { localStorage.setItem('mtsfj-arcade-ini', v); } catch (e) {} }

  // ==== HOSHIKUZU (ホシクズ, stardust): the teal cabinets' fixed shooter. As the drawing's screen: a big lone alien near the
  // top, rows of small ones under it, the cannon at the bottom; mint on teal, five colours. The rows march across and step
  // down at each edge, faster as they thin out, and drop their twinkling stardust; the lone one sways over them, drops its
  // own heavier bomb and takes a few shots (a bonus: it leaves when its rows are gone); three low mounds of cover wear away
  // under the shots; three lives, an extra one at 20000; each wave starts lower, with more rows. Its own designs: a
  // five-pointed star, a round eared blob, a three-eyed jelly, a crowned king with fangs ====
  const HK = { W: 128, H: 124, bg: '#0592ad', deep: '#04718a', dim: '#3dcbb8', mint: '#74f5d6', pale: '#dcfff4' };
  const HKP = { m: HK.mint, w: HK.pale, d: HK.dim, t: HK.deep };
  const HK_S = {
    star: [['.....m.....', '....mmm....', 'mmmmmmmmmmm', '.mm.mmm.mm.', '..mmmmmmm..', '..mm.m.mm..', '.mm.....mm.', 'mm.......mm'],
      ['.....m.....', '....mmm....', 'mmmmmmmmmmm', '.mm.mmm.mm.', '..mmmmmmm..', '..mm.m.mm..', '..mm...mm..', '...mm.mm...']],
    mochi: [['.mm.....mm.', '.mmmmmmmmm.', 'mmmmmmmmmmm', 'mm..mmm..mm', 'mmmmmmmmmmm', 'mmmm...mmmm', '.mmmmmmmmm.', '..m.m.m.m..'],
      ['.mm.....mm.', '.mmmmmmmmm.', 'mmmmmmmmmmm', 'mm..mmm..mm', 'mmmmmmmmmmm', 'mmmmm.mmmmm', '.mmmmmmmmm.', '.m.m...m.m.']],
    jelly: [['...mmmmm...', '.mmmmmmmmm.', 'mm.mm.mm.mm', 'mmmmmmmmmmm', '.mmmmmmmmm.', '.m.m.m.m.m.', 'm..m...m..m', '.m...m...m.'],
      ['...mmmmm...', '.mmmmmmmmm.', 'mm.mm.mm.mm', 'mmmmmmmmmmm', '.mmmmmmmmm.', '.m.m.m.m.m.', '.m..m.m..m.', 'm...m.m...m']],
    king: [['.w....w....w.', '..m...m...m..', '...m..m..m...', '...mmmmmmm...', '.mmmmmmmmmmm.', 'mmm..mmm..mmm', 'mmm..mmm..mmm', 'mmmmmmmmmmmmm', 'mm.m.m.m.m.mm', '.m..m...m..m.'],
      ['.w....w....w.', '..m...m...m..', '...m..m..m...', '...mmmmmmm...', '.mmmmmmmmmmm.', 'mmm..mmm..mmm', 'mmm..mmm..mmm', 'mmmmmmmmmmmmm', 'mm.m.m.m.m.mm', 'm..m.....m..m'],
      ['.............', '...........m.', '...m.....m...', '...mmmmmmm...', '.mmmmmmmmmmm.', 'mmm..mmm..mmm', 'mmmw.mmm.wmmm', 'mmmmmmmmmmmmm', 'mm.m.m.m.m.mm', '.m..m...m..m.']],
    gun: [['......w......', '.....mmm.....', '.....mmm.....', '..mmmmmmmmm..', '.mmmtmmmtmmm.', 'mmmmmmmmmmmmm', 'mmmmmmmmmmmmm']],
    gunDim: [['......d......', '.....ddd.....', '.....ddd.....', '..ddddddddd..', '.dddtdddtddd.', 'ddddddddddddd', 'ddddddddddddd']],
    mini: [['...m...', '.mmmmm.', 'mmmmmmm']],
    boom: [['w....m....w', '.w...m...w.', '..w.....w..', 'mm...w...mm', '..w.....w..', '.w...m...w.', 'w....m....w']],
    bigBoom: [['m......w......m', '.m.....w.....m.', '..m.........m..', '...w...m...w...', '.......w.......', 'www..wwmww..www', '.......w.......', '...w...m...w...', '..m.........m..', '.m.....w.....m.']],
    die: [['.....w.......', '..m.....w..m.', '.....m.......', '.m..mm.mm..w.', '..mmm.mmm.m..', 'm.mmmmmmmmm.m', '.mm.mmmmm.mm.'],
      ['..w.......m..', 'm.....w......', '...m.....m..w', '.....m.m.....', '.m.m.....m.m.', '..m..m.m..m..', 'm..m..m..m..m']],
    dust: [['.w.', 'www', '.w.'], ['w.w', '.w.', 'w.w']],
    bomb: [['.m.', 'mwm', 'mwm', '.m.']] };
  let HKC = null;                               // the sprites as canvases, made at the first use
  function hkSprites() {
    if (HKC) return HKC;
    HKC = {};
    for (const k in HK_S) HKC[k] = HK_S[k].map((r) => sprite(r, HKP));
    HKC.kingPale = HK_S.king.map((r) => sprite(r, { m: HK.pale, w: HK.pale }));
    return HKC;
  }
  const HK_MOUND = ['......dddddd......', '...dddddddddddd...', '.dddddddddddddddd.', 'dddddddddddddddddd', 'dddddddddddddddddd', 'dddddddddddddddddd', 'dddddddddddddddddd'];
  // the waves: [rows (their kinds, top first), columns]; then as the last, faster each time
  const HK_WAVES = [[['star', 'star'], 4], [['jelly', 'star', 'mochi'], 4], [['jelly', 'star', 'mochi'], 5], [['jelly', 'star', 'star', 'mochi'], 5], [['jelly', 'jelly', 'star', 'mochi'], 6]];
  const HK_PTS = { jelly: 300, star: 200, mochi: 100 };
  const HK_GROUND = 113, HK_PY = 105;
  function hoshiGame() {
    const G = { W: HK.W, H: HK.H, title: 'HOSHIKUZU', kana: 'ホシクズ', ink: { bg: HK.bg, ink: HK.pale, dim: HK.dim, hi: HK.mint, plate: HK.deep, sh: HK.deep } };
    let S = null;
    G.reset = (demo) => {
      S = { demo, score: 0, lives: 3, wave: 0, extra: false, px: 57, dead: 0, inv: 0, shot: null, bombs: [], fx: [], t: 0, msg: '', msgT: 0, shake: 0, over: false, clear: 0, invaded: false };
      hkWave();
    };
    G.score = () => (S ? S.score : 0);
    G.over = () => !!(S && S.over);
    G.st = () => S;                             // (its state, for a test page)
    function hkWave() {
      S.wave++;
      const [kinds, cols] = HK_WAVES[Math.min(S.wave, HK_WAVES.length) - 1], w = cols * 15 - 4;
      S.fm = { x: Math.round((HK.W - w) / 2), y: 26 + Math.min(16, 4 * (S.wave - 1)), dir: 1, acc: 0, fr: 0, cols, kinds, n: kinds.length * cols, total: kinds.length * cols,
        cell: kinds.map(() => new Array(cols).fill(true)), hold: 1.2 };
      S.lone = { on: true, hp: S.wave >= 3 ? 3 : 2, t: 0, x: 57, y: Math.max(9, S.fm.y - 16), leave: false, fire: rnd(2.5, 4), flash: 0 };
      S.mounds = [14, 55, 96].map((x) => ({ x, y: 93, m: HK_MOUND.map((r) => [...r].map((c) => (c === 'd' ? 1 : 0))) }));
      S.bombs = []; S.shot = null; S.fireT = 1.6; S.clear = 0;
      if (!S.demo) { S.msg = T().wave + ' ' + S.wave; S.msgT = 1.6; }
    }
    const speedK = () => 1 + 0.2 * (S.wave - 1);
    function cellXY(r, c) { return [S.fm.x + c * 15, S.fm.y + r * 11]; }
    function edges() {                          // the alive columns' extent, the lowest alive row's bottom
      let c0 = 99, c1 = -1, bot = -1;
      S.fm.cell.forEach((row, r) => row.forEach((on, c) => { if (on) { c0 = Math.min(c0, c); c1 = Math.max(c1, c); bot = Math.max(bot, r); } }));
      return [S.fm.x + c0 * 15, S.fm.x + c1 * 15 + 11, S.fm.y + bot * 11 + 8];
    }
    function addFx(k, x, y, life, s) { S.fx.push({ k, x, y, t: 0, life, s }); }
    function score(n) {
      if (S.demo) return;
      S.score += n;
      if (!S.extra && S.score >= 20000) { S.extra = true; S.lives++; S.msg = T().extra; S.msgT = 1.6; }
    }
    function erode(M, x, y, r) {               // a shot's bite out of a mound: a little ragged blob
      for (let dy = -r; dy <= r; dy++) for (let dx = -r; dx <= r; dx++) {
        const u = x - M.x + dx, v = y - M.y + dy;
        if (v < 0 || v >= M.m.length || u < 0 || u >= M.m[0].length) continue;
        if (dx * dx + dy * dy <= r * r + (Math.random() < 0.5 ? 1 : 0)) M.m[v][u] = 0;
      }
    }
    function moundAt(x, y) {
      for (const M of S.mounds) { const u = x - M.x, v = y - M.y; if (v >= 0 && v < M.m.length && u >= 0 && u < M.m[0].length && M.m[v][u]) return M; }
      return null;
    }
    function killPlayer() {                     // (the bombs in the air are cleared by the caller, after its own loop over them)
      if (S.dead > 0 || S.inv > 0) return;
      S.dead = 1.5; S.shot = null; if (!reduced) S.shake = 0.35;
    }
    // the demo's player (attract): under the nearest column, away from a bomb overhead, firing when lined up
    function auto() {
      const I = { held: {}, hit: {} }, cx = S.px + 6;
      if (S.dead > 0) return I;
      let tx = 64, best = 1e9;
      S.fm.cell.forEach((row, r) => row.forEach((on, c) => { if (on) { const x = cellXY(r, c)[0] + 5, d = Math.abs(x - cx) + r * 3; if (d < best) { best = d; tx = x; } } }));
      for (const b of S.bombs) if (b.y > 70 && Math.abs(b.x - cx) < 9) tx = cx + (b.x < cx ? 18 : -18);
      if (tx < cx - 2) I.held.l = 1; else if (tx > cx + 2) I.held.r = 1;
      if (Math.abs(tx - cx) < 4 && Math.random() < 0.2 && S.t > 2.5) I.held.a = 1;   // (its first seconds: the drawing's tableau, whole)
      return I;
    }
    G.update = (dt, I) => {
      if (!S) G.reset(true);
      if (S.demo) I = auto();
      S.t += dt; S.shake = Math.max(0, S.shake - dt); S.msgT = Math.max(0, S.msgT - dt);
      for (const f of S.fx) f.t += dt;
      S.fx = S.fx.filter((f) => f.t < f.life);
      if (S.over) return;
      const F = S.fm, L1 = S.lone;
      // the player, or its wreck
      if (S.dead > 0) {
        S.dead -= dt;
        if (S.dead <= 0) {
          if (S.invaded || --S.lives <= 0) { S.lives = Math.max(0, S.lives); if (S.demo) G.reset(true); else S.over = true; return; }
          S.px = 57; S.inv = 1.6;
        }
        return;                                 // (all hold still while it burns)
      }
      S.inv = Math.max(0, S.inv - dt);
      if (I.held.l) S.px -= 56 * dt;
      if (I.held.r) S.px += 56 * dt;
      S.px = clamp(S.px, 2, HK.W - 15);
      if (!S.shot && S.clear <= 0 && (I.held.a || I.held.b || I.hit.a || I.hit.b)) S.shot = { x: Math.round(S.px) + 6, y: HK_PY - 4, acc: 0 };
      // the shot, a pixel at a time (nothing slips between; its speed kept to the fraction of a pixel)
      if (S.shot) {
        S.shot.acc += 170 * dt; const n = Math.floor(S.shot.acc); S.shot.acc -= n;
        for (let k = 0; k < n && S.shot; k++) {
          const s = S.shot; s.y -= 1;
          if (s.y < 8) { addFx('pop', s.x - 1, 8, 0.15); S.shot = null; break; }
          const M = moundAt(s.x, s.y); if (M) { erode(M, s.x, s.y, 2); S.shot = null; break; }
          for (let i = 0; i < S.bombs.length; i++) { const b = S.bombs[i]; if (Math.abs(b.x - s.x) <= 1 && s.y >= b.y - 1 && s.y <= b.y + 3) { S.bombs.splice(i, 1); addFx('pop', s.x - 1, s.y, 0.15); S.shot = null; break; } }
          if (!S.shot) break;
          let hit = false;
          F.cell.forEach((row, r) => row.forEach((on, c) => {
            if (!on || hit) return; const [ax, ay] = cellXY(r, c);
            if (s.x >= ax && s.x < ax + 11 && s.y >= ay && s.y < ay + 8) {
              hit = true; row[c] = false; F.n--; addFx('boom', ax, ay, 0.28);
              score(Math.round(HK_PTS[F.kinds[r]] * (1 + 0.5 * (S.wave - 1)) / 10) * 10);
            }
          }));
          if (hit) { S.shot = null; break; }
          if (L1.on && s.x >= L1.x && s.x < L1.x + 13 && s.y >= L1.y && s.y < L1.y + 10) {
            S.shot = null; L1.hp--; L1.flash = reduced ? 0 : 0.12;
            if (L1.hp <= 0) { L1.on = false; addFx('big', L1.x - 1, L1.y, 0.5); const p = 1500 * S.wave; score(p); addFx('txt', L1.x + 6, L1.y + 2, 1.2, String(p)); }
            break;
          }
        }
      }
      // the wave cleared: its bonus, the lone one away, the next
      if (F.n <= 0 && S.clear <= 0) { S.clear = 2.2; const b = 1000 * S.wave; score(b); if (!S.demo) { S.msg = T().bonus + ' ' + b; S.msgT = 2; } if (L1.on) L1.leave = true; S.bombs = []; }
      if (S.clear > 0) { S.clear -= dt; if (L1.on && L1.leave) { L1.y -= 40 * dt; if (L1.y < -12) L1.on = false; } if (S.clear <= 0) hkWave(); return; }
      // the formation's march: one step at a time, quicker as it thins out; at an edge, a step down instead
      if (F.hold > 0) F.hold -= dt;
      else {
        F.acc += dt;
        const stepT = Math.max(0.035, (0.04 + 0.42 * F.n / F.total) / speedK());
        while (F.acc >= stepT) {
          F.acc -= stepT; F.fr ^= 1;
          const [l, r] = edges();
          if ((F.dir > 0 && r + 2 > HK.W - 2) || (F.dir < 0 && l - 2 < 2)) { F.y += 4; F.dir = -F.dir; }
          else F.x += 2 * F.dir;
        }
        const bot = edges()[2];
        for (const M of S.mounds) F.cell.forEach((row, r) => row.forEach((on, c) => {   // (the rows wipe the mounds they walk through)
          if (!on) return; const [ax, ay] = cellXY(r, c);
          for (let v = 0; v < M.m.length; v++) for (let u = 0; u < M.m[0].length; u++) { const x = M.x + u, y = M.y + v; if (x >= ax && x < ax + 11 && y >= ay && y < ay + 8) M.m[v][u] = 0; }
        }));
        if (bot >= HK_PY) { S.invaded = true; killPlayer(); S.dead = Math.max(S.dead, 1.5); S.bombs = []; }
      }
      // the lone one: sways over its rows, drops its bomb
      if (L1.on) {
        L1.t += dt; L1.flash = Math.max(0, L1.flash - dt);
        L1.x = Math.round(57 + 34 * Math.sin(L1.t * 0.7 * speedK())); L1.y = Math.max(9, F.y - 16);
        L1.fire -= dt;
        if (L1.fire <= 0 && F.hold <= 0) { L1.fire = rnd(2.2, 3.8) / speedK(); S.bombs.push({ x: L1.x + 6, y: L1.y + 10, v: 42 + 4 * S.wave, big: true, acc: 0 }); }
      }
      // the rows' stardust: from the lowest of a column, often the one over the player
      S.fireT -= dt;
      const maxB = 2 + Math.floor(S.wave / 2);
      if (S.fireT <= 0 && F.hold <= 0) {
        S.fireT = rnd(0.5, 1.3) / speedK();
        if (S.bombs.filter((b) => !b.big).length < maxB) {
          const cols = []; for (let c = 0; c < F.cols; c++) for (let r = F.kinds.length - 1; r >= 0; r--) if (F.cell[r][c]) { cols.push([c, r]); break; }
          if (cols.length) {
            let ch = pick(cols);
            if (Math.random() < 0.5) ch = cols.reduce((a, b) => (Math.abs(cellXY(b[1], b[0])[0] + 5 - S.px - 6) < Math.abs(cellXY(a[1], a[0])[0] + 5 - S.px - 6) ? b : a));
            const [ax, ay] = cellXY(ch[1], ch[0]); S.bombs.push({ x: ax + 5, y: ay + 8, v: 46 + 6 * S.wave, big: false, acc: 0 });
          }
        }
      }
      // the bombs: into the mounds, the cannon, the ground
      for (let i = S.bombs.length - 1; i >= 0; i--) {
        const b = S.bombs[i]; let gone = false;
        b.acc += b.v * dt; const n = Math.floor(b.acc); b.acc -= n;
        for (let k = 0; k < n && !gone; k++) {
          b.y += 1; const y = b.y + (b.big ? 3 : 2);
          const M = moundAt(b.x, y); if (M) { erode(M, b.x, y, b.big ? 3 : 2); gone = true; break; }
          if (y >= HK_PY + 1 && y < HK_PY + 7 && b.x >= S.px + 1 && b.x < S.px + 12) { gone = true; killPlayer(); break; }
          if (y >= HK_GROUND) { addFx('pop', b.x - 1, HK_GROUND - 2, 0.2); gone = true; }
        }
        if (gone) S.bombs.splice(i, 1);
      }
      if (S.dead > 0) S.bombs = [];             // (hit: the sky clears while it burns)
    };
    G.draw = (g) => {
      const C = hkSprites(), sh = S && S.shake > 0 ? (Math.floor(S.t * 30) % 2 ? 1 : -1) : 0;
      R(g, 0, 0, HK.W, HK.H, HK.bg);
      if (!S) return;
      g.save(); g.translate(sh, 0);
      R(g, 0, HK_GROUND, HK.W, 1, HK.deep);
      for (const M of S.mounds) M.m.forEach((row, v) => row.forEach((on, u) => { if (on) R(g, M.x + u, M.y + v, 1, 1, HK.dim); }));
      const F = S.fm;
      F.cell.forEach((row, r) => row.forEach((on, c) => { if (on) { const [x, y] = cellXY(r, c); g.drawImage(C[F.kinds[r]][F.fr], x, y); } }));
      const L1 = S.lone;
      if (L1.on) g.drawImage((L1.flash > 0 ? C.kingPale : C.king)[L1.hp < (S.wave >= 3 ? 3 : 2) ? 2 : Math.floor(L1.t * 2.5) % 2], L1.x, L1.y);
      if (S.dead > 0) { if (S.dead > 0.6) g.drawImage(C.die[Math.floor(S.t * 8) % 2], Math.round(S.px), HK_PY); }
      else if (!(S.inv > 0 && !reduced && Math.floor(S.inv * 8) % 2)) g.drawImage(S.inv > 0 && reduced ? C.gunDim[0] : C.gun[0], Math.round(S.px), HK_PY);
      if (S.shot) R(g, S.shot.x, S.shot.y, 1, 4, HK.pale);
      for (const b of S.bombs) g.drawImage(b.big ? C.bomb[0] : C.dust[Math.floor((S.t + b.x) * 8) % 2], b.x - 1, b.y);
      for (const f of S.fx) {
        if (f.k === 'boom') g.drawImage(C.boom[0], f.x, f.y);
        else if (f.k === 'big') g.drawImage(C.bigBoom[0], f.x, f.y);
        else if (f.k === 'pop') { R(g, f.x, f.y, 1, 1, HK.pale); R(g, f.x + 2, f.y, 1, 1, HK.pale); R(g, f.x + 1, f.y - 1, 1, 1, HK.mint); }
        else if (f.k === 'txt') text(g, f.s, f.x, f.y, HK.pale, 1, 'c');
      }
      g.restore();
      // the HUD: score and the best at the top, the spare cannons and the wave at the bottom (dim: the drawing's screen first)
      text(g, '1UP', 2, 1, HK.dim); text(g, pad(S.score, 6), 16, 1, HK.pale);
      text(g, 'HI', 92, 1, HK.dim); text(g, pad(Math.max(G.hi || 0, S.score), 6), HK.W - 2, 1, HK.pale, 1, 'r');
      for (let i = 0; i < Math.min(5, S.lives - (S.dead > 0 ? 1 : 0) - 1); i++) g.drawImage(C.mini[0], 2 + i * 9, 117);
      if (!S.demo) text(g, T().wave + ' ' + S.wave, HK.W - 2, 117, HK.dim, 1, 'r');
      if (S.msgT > 0) text(g, S.msg, 64, 70, HK.pale, 1, 'c', HK.deep);
    };
    // the attract's pages over the demo: the title (as the drawing: its tableau stays in view), the points
    G.drawTitle = (g, k) => {
      R(g, 22, 58, 84, 30, HK.bg);
      text(g, 'HOSHIKUZU', 64, 60, HK.pale, 2, 'c', HK.deep);
      kana(g, 'ホシクズ', 64, 74, HK.mint, 'c');
      if (k) text(g, k, 64, 84, HK.pale, 1, 'c', HK.deep);
    };
    G.drawInfo = (g) => {
      const C = hkSprites(), t = T();
      R(g, 6, 22, 116, 82, HK.bg); R(g, 6, 22, 116, 1, HK.dim); R(g, 6, 103, 116, 1, HK.dim);
      g.drawImage(C.king[0], 24, 28); text(g, '= ' + T().bonus, 44, 31, HK.pale);
      [['jelly', 300], ['star', 200], ['mochi', 100]].forEach(([k, p], i) => { g.drawImage(C[k][0], 25, 42 + i * 11); text(g, '= ' + p + ' ' + t.pts, 44, 43 + i * 11, HK.pale); });
      t.hInfo.forEach((s, i) => text(g, s, 64, 76 + i * 7, i < 2 ? HK.mint : HK.dim, 1, 'c'));
    };
    G.reset(true);
    return G;
  }

  // ==== YUHI DRIVE (ユウヒ ドライブ, sunset drive): the pink cabinet's road racer. As the drawing's screen: a pink sky in solid
  // bands, the striped sun on the horizon, two stepped clouds, the purple city, the road running to the horizon between
  // pink and violet bands, the pink car seen from behind. The road is drawn the classic pseudo-3D way: a looped track of
  // short segments, each with its curve and its height, projected from a camera over the car; the curves throw the car
  // outward (brake for the hard ones), the hills hide what is behind them; traffic to overtake in three lanes, lamps,
  // palms and signs along the road, a checkered gate at each checkpoint that gives time back. 30 s to start ====
  const YD = { W: 128, H: 124, HOR: 62, SEG: 200, RW: 860, CH: 1000, DEPTH: 0.84, DRAW: 110, MAX: 12000, CAR: 469, CPN: 1300 };
  YD.PZ = YD.CH * YD.DEPTH;
  const YC = { g0: '#4c18b0', g1: '#a21cae', r0: '#3a18a6', r1: '#4218ac', rum: '#f048b0', lane: '#7a44d4', ink: '#fff0f8', dim: '#f8b0d0', sh: '#2a0a6a', glow: '#f66abd' };
  const YD_CAR = ['........oooooooooooooo........', '.......ohhhhhhhhhhhhhho.......', '......okbbbbbbbbbbbbbbko......', '.....okbgbbbbbbbbbbbbbbko.....',
    '.....okbbbbbbbbbbbbbbbbko.....', '....oknnnnnnnnnnnnnnnnnnko....', '..ooohhhhhhhhhhhhhhhhhhhhhooo..', '.ohhkkkkkkkkkkkkkkkkkkkkkkhho.',
    'okkkkkkkkkkkkkkkkkkkkkkkkkkkko', 'orrrrrkkkkkkkkkkkkkkkkkkrrrrro', 'orllllrkkkkkkppppkkkkkkrllllro', 'orrrrrkkkkkkkppppkkkkkkkrrrrro',
    'osssssssssssssssssssssssssssso', '.osssxxssssssssssssssssxxssso.', '.ttttt.oooooooooooooooo.ttttt.', '.ttttt..................ttttt.', '..ttt....................ttt..'];
  const YD_BASE = { o: '#2a0848', n: '#101878', b: '#1838a8', g: '#3a5ad0', l: '#ff9ccc', r: '#c0186a', p: '#f8b0d0', t: '#0c0a30', x: '#4a1060' };
  const YD_PAINT = { player: { k: '#e828a8', h: '#f878c0', s: '#a8188e' }, violet: { k: '#7a1cb8', h: '#a050e0', s: '#4a1090' },
    navy: { k: '#1a2a98', h: '#3a50d0', s: '#0e1468' }, pale: { k: '#f8a8c8', h: '#ffd2e2', s: '#c070a0' }, deep: { k: '#9a188a', h: '#d040b0', s: '#600e60' } };
  let YDC = null;
  function ydSprites() {
    if (YDC) return YDC;
    YDC = {};
    const shift = (rows, d) => rows.map((r, i) => (i < 7 ? (d < 0 ? r.slice(1) + '.' : '.' + r.slice(0, -1)) : r));   // (the cabin a pixel over in a turn)
    for (const k in YD_PAINT) YDC[k] = sprite(YD_CAR, Object.assign({}, YD_BASE, YD_PAINT[k]));
    const P = Object.assign({}, YD_BASE, YD_PAINT.player);
    YDC.left = sprite(shift(YD_CAR, -1), P); YDC.right = sprite(shift(YD_CAR, 1), P);
    const Pb = Object.assign({}, P, { l: '#ffffff', r: '#ff5ab0' });   // (braking: the tail lights full)
    YDC.brake = sprite(YD_CAR, Pb); YDC.brakeL = sprite(shift(YD_CAR, -1), Pb); YDC.brakeR = sprite(shift(YD_CAR, 1), Pb);
    YDC.lamp = sprite(['.ppp.', 'pwwwp', '.ppp.'].concat(new Array(19).fill('..o..'), ['.ooo.']), { p: '#f048b0', w: '#ffe6f2', o: '#2a0a6a' });
    YDC.palm = sprite(['..ff......ff...', '.ffff....ffff..', 'ffffff.ffffff..', 'f..fffffffff.ff', '..ff..ttff...f.', '.f....t...f....', '......t........', '......t........',
      '.....t.........', '.....t.........', '.....t.........', '.....t.........', '.....t.........', '.....t.........', '......t........', '......t........', '......t........', '.....ttt.......'],
      { f: '#3a1494', t: '#2a0a6a' });
    const [bc, bg] = canvas(25, 18);            // a sign: its name in katakana on pink
    R(bg, 0, 0, 25, 11, '#2a0a6a'); R(bg, 1, 1, 23, 9, '#f048b0'); kana(bg, 'ユウヒ', 1, 2, '#ffe6f2'); R(bg, 4, 11, 2, 7, '#2a0a6a'); R(bg, 19, 11, 2, 7, '#2a0a6a');
    YDC.sign = bc;
    // the backdrop: the sky in bands, the sun striped by the sky's own colour; the clouds and the city as strips that turn
    const [sc, sg] = canvas(YD.W, YD.HOR);
    [[0, 10, '#d01e9e'], [10, 22, '#e828a8'], [32, 16, '#ee34ac'], [48, 10, '#f24cb4'], [58, 4, '#f66abd']].forEach(([y, h, c]) => R(sg, 0, y, YD.W, h, c));
    const cut = [47, 51, 54, 57, 59, 61];
    for (let y = 31; y < YD.HOR; y++) {
      if (cut.includes(y)) continue;
      const v = (y + 0.5 - 48) / 17, hw = Math.round(17 * Math.sqrt(Math.max(0, 1 - v * v)));
      R(sg, 64 - hw, y, 2 * hw, 1, y < 37 ? '#ffd8e6' : y < 43 ? '#fcb2cf' : y < 50 ? '#f994c0' : '#f777b6');
    }
    YDC.sky = sc;
    const [cc, cg] = canvas(256, 14);
    [[14, 2], [98, 4], [150, 1], [212, 3]].forEach(([x, y]) => { [[5, 4, '#ff9ccc'], [3, 8, '#f868b8'], [0, 14, '#f868b8']].forEach(([dx, w, c], i) => R(cg, x + dx, y + i * 2, w, 2, c)); });
    YDC.clouds = cc;
    const [kc, kg] = canvas(256, 26);           // the city: two rows of blocks, a few lit windows
    let s0 = 7; const r = () => ((s0 = (s0 * 16807) % 2147483647) / 2147483647);
    for (const [col, hmin, hmax, win] of [['#4818ac', 10, 25, '#6a2cc4'], ['#5c1cb8', 4, 15, '#f04cb4']]) {
      for (let x = 0; x < 256;) {
        const w = 5 + Math.floor(r() * 8), h = hmin + Math.floor(r() * (hmax - hmin));
        R(kg, x, 26 - h, w, h, col);
        if (r() < 0.3 && h > 12) R(kg, x + (w >> 1), 26 - h - 3, 1, 3, col);
        for (let wy = 26 - h + 2; wy < 24; wy += 3) for (let wx = x + 1; wx < x + w - 1; wx += 2) if (r() < 0.22) R(kg, wx, wy, 1, 1, win);
        x += w + (r() < 0.3 ? 1 : 0);
      }
    }
    YDC.city = kc;
    return YDC;
  }
  // the track, built once: segments [curve, height], their sprites, the checkpoints every CPN segments; a loop
  let YT = null;
  function ydTrack() {
    if (YT) return YT;
    const segs = [], lastY = () => (segs.length ? segs[segs.length - 1].p2.w.y : 0);
    const add = (curve, y) => { const n = segs.length; segs.push({ i: n, p1: { w: { y: lastY(), z: n * YD.SEG }, c: {}, s: {} }, p2: { w: { y, z: (n + 1) * YD.SEG }, c: {}, s: {} }, curve, band: Math.floor(n / 3) % 2, spr: [], cars: [], clip: 0, cp: false }); };
    const eIn = (a, b, p) => a + (b - a) * p * p, eIO = (a, b, p) => a + (b - a) * (-Math.cos(p * Math.PI) / 2 + 0.5);
    function road(e, h, l, curve, hill) {
      const y0 = lastY(), y1 = y0 + hill * YD.SEG, n = e + h + l;
      for (let i = 0; i < e; i++) add(eIn(0, curve, i / e), eIO(y0, y1, i / n));
      for (let i = 0; i < h; i++) add(curve, eIO(y0, y1, (e + i) / n));
      for (let i = 0; i < l; i++) add(eIO(curve, 0, i / l), eIO(y0, y1, (e + h + i) / n));
    }
    const S = 25, M = 50, Lg = 100;
    road(M, M, M, 0, 0);
    for (let lap = 0; lap < 4; lap++) {
      const d = lap % 2 ? -1 : 1;
      road(S, S, S, 0, 10); road(S, S, S, 0, -20); road(S, S, S, 2 * d, 20); road(S, S, S, 0, 0); road(S, S, S, -2 * d, 10); road(S, S, S, 0, -20);
      road(M, M, M, 4 * d, 20); road(Lg, Lg, Lg, 0, 0);
      road(M, M, M, -2 * d, 0); road(M, M, M, 4 * d, 40); road(M, M, M, 2 * d, -20); road(M, M, M, -2 * d, 40); road(M, M, M, -4 * d, -40);
      road(M, M, M, 0, 60); road(Lg, M, Lg, -4 * d, 0); road(S, S, S, 0, 10); road(S, S, S, 0, -10); road(S, S, S, 0, 5); road(S, S, S, 0, -5);
      road(Lg, Lg, Lg, 6 * d, 0); road(M, S, M, -3 * d, -30); road(Lg, M, M, 0, 0);
    }
    road(Lg, Lg, Lg, 0, -lastY() / YD.SEG);     // (down to where it began: the loop closes)
    const N = segs.length;
    for (let i = 20; i < N; i += 10) { segs[i].spr.push({ k: 'lamp', off: -1.35, solid: 1 }); segs[(i + 5) % N].spr.push({ k: 'lamp', off: 1.35, solid: 1 }); }
    let s0 = 11; const r = () => ((s0 = (s0 * 16807) % 2147483647) / 2147483647);
    for (let i = 30; i < N; i += 7 + Math.floor(r() * 9)) segs[i].spr.push({ k: 'palm', off: (r() < 0.5 ? -1 : 1) * (1.7 + r() * 0.9), solid: 1 });
    for (let i = 160; i < N; i += 260 + Math.floor(r() * 200)) segs[i].spr.push({ k: 'sign', off: (r() < 0.5 ? -1 : 1) * 1.9, solid: 1 });
    const cps = []; for (let i = YD.CPN; i < N - 200; i += YD.CPN) { segs[i].cp = true; cps.push(i); }
    YT = { segs, N, len: N * YD.SEG, cps };
    return YT;
  }
  function yuhiGame() {
    const G = { W: YD.W, H: YD.H, title: 'YUHI DRIVE', kana: 'ユウヒ ドライブ', ink: { bg: '#e828a8', ink: YC.ink, dim: YC.dim, hi: '#ffd8e6', plate: '#2a0a6a', sh: '#2a0a6a' } };
    const TK = ydTrack(), segs = TK.segs, N = TK.N, LEN = TK.len;
    const segAt = (z) => segs[Math.floor(((z % LEN) + LEN) % LEN / YD.SEG) % N];
    const wrap = (z) => ((z % LEN) + LEN) % LEN;
    let S = null;
    G.reset = (demo) => {
      for (const s of segs) s.cars.length = 0;
      const cars = [], paints = ['violet', 'navy', 'pale', 'deep'];
      for (let i = 0; i < 72; i++) {
        const z = wrap((i + 0.5) / 72 * LEN + rnd(0, 2000) + 4000), off = pick([-0.62, 0, 0.62]);
        const c = { z, off, tgt: off, lt: rnd(5, 14), speed: YD.MAX * rnd(0.22, 0.5), paint: pick(paints), rel: 0 };
        cars.push(c); segAt(c.z).cars.push(c);
      }
      S = { demo, pos: 0, x: 0, speed: 0, trav: 0, time: 30, cpN: 0, bonus: 0, passed: 0, cars, cityX: 0, cloudX: 0, steer: 0, brake: false, cd: demo ? 0 : 3.2,
        msg: '', msgT: 0, up: false, upT: 0, over: false, shake: 0, t: 0 };
      for (const c of cars) c.rel = relZ(c);
    };
    const relZ = (c) => { let d = c.z - wrap(S.pos + YD.PZ); if (d > LEN / 2) d -= LEN; if (d < -LEN / 2) d += LEN; return d; };
    G.score = () => (S ? Math.floor(S.trav / YD.SEG * 1.3) * 10 + S.bonus : 0);
    G.over = () => !!(S && S.over);
    G.st = () => S;
    const overlap = (x1, w1, x2, w2) => !(x1 + w1 / 2 < x2 - w2 / 2 || x1 - w1 / 2 > x2 + w2 / 2);
    function auto() {                           // the demo's driver: the lane with no slow car ahead, a little off the gas in hard curves
      const I = { held: {}, hit: {} }, ps = segAt(S.pos + YD.PZ);
      let lane = [-0.62, 0, 0.62].sort((a, b) => Math.abs(a - S.x) - Math.abs(b - S.x)).find((L) => !S.cars.some((c) => { const d = relZ(c); return d > 0 && d < 30 * YD.SEG && Math.abs(c.off - L) < 0.5; }));
      if (lane === undefined) lane = S.x;
      const want = lane - ps.curve * 0.06 * (S.speed / YD.MAX);
      if (S.x < want - 0.06) I.held.r = 1; else if (S.x > want + 0.06) I.held.l = 1;
      let hard = 0; for (let n = 0; n < 40; n++) hard = Math.max(hard, Math.abs(segs[(ps.i + n) % N].curve));
      if (S.speed < YD.MAX * (hard >= 5 ? 0.62 : hard >= 3.5 ? 0.82 : 0.95)) I.held.a = 1; else if (hard >= 5 && S.speed > YD.MAX * 0.7) I.held.b = 1;
      return I;
    }
    G.update = (dt, I) => {
      if (!S) G.reset(true);
      if (S.demo) I = auto();
      S.t += dt; S.msgT = Math.max(0, S.msgT - dt); S.shake = Math.max(0, S.shake - dt);
      if (S.over) return;
      const ps = segAt(S.pos + YD.PZ), sp = S.speed / YD.MAX, dx = dt * 2 * sp, z0 = S.pos;
      if (S.cd > 0) { const c0 = Math.ceil(S.cd - 0.2); S.cd -= dt; const c1 = Math.ceil(S.cd - 0.2); if (c1 !== c0 && c1 <= 0) { S.msg = T().go; S.msgT = 1; } }
      const go = S.cd <= 0.2 && !S.up;
      const gas = go && (I.held.a || I.held.u), brake = !!(I.held.b || I.held.d);
      S.brake = brake && S.speed > 0;
      S.pos = wrap(S.pos + dt * S.speed); S.trav += dt * S.speed;
      S.steer = 0;
      if (S.speed > 0) { if (I.held.l) { S.x -= dx; S.steer = -1; } else if (I.held.r) { S.x += dx; S.steer = 1; } }
      S.x -= dx * sp * ps.curve * 0.3;
      if (gas) S.speed += YD.MAX / 5 * dt; else if (brake) S.speed -= YD.MAX * dt; else S.speed -= YD.MAX / 5 * dt;
      if (Math.abs(S.x) > 1 && S.speed > YD.MAX / 4) S.speed -= YD.MAX / 2 * dt;   // (off the road: the dirt)
      const PW = YD.CAR / YD.RW;
      if (Math.abs(S.x) > 1) for (const s of ps.spr) {                            // (into a lamp, a palm, a sign)
        const w = (s.k === 'palm' ? 6 : s.k === 'sign' ? 25 : 5) * YD.CH / YD.RW / 64 * 0.9;
        if (overlap(S.x, PW, s.off, w)) { S.speed = YD.MAX / 6; S.pos = wrap(ps.p1.w.z - YD.PZ); S.x += S.x > 0 ? -0.15 : 0.15; if (!reduced) S.shake = 0.3; break; }
      }
      for (const c of ps.cars) if (S.speed > c.speed && overlap(S.x, PW * 0.9, c.off, PW * 0.9)) {   // (into a car: down to its pace, behind it)
        S.speed = c.speed * (c.speed / S.speed); S.pos = wrap(c.z - YD.PZ - 40); if (!reduced) S.shake = 0.25; break;
      }
      S.x = clamp(S.x, -2.4, 2.4); S.speed = clamp(S.speed, 0, YD.MAX);
      const dSeg = (S.pos - z0 + LEN) % LEN / YD.SEG;
      S.cityX += ps.curve * dSeg * 0.32; S.cloudX += ps.curve * dSeg * 0.12;
      // the traffic: on in its lane, now and then to another; out of the way of a slower one ahead, and of our car when it
      // comes up behind it faster (it would drive through); the ones we pass are points
      const lanes = [-0.62, 0, 0.62];
      for (const c of S.cars) {
        const s0 = segAt(c.z); c.z = wrap(c.z + c.speed * dt); const s1 = segAt(c.z);
        if (s1 !== s0) { const k = s0.cars.indexOf(c); if (k >= 0) s0.cars.splice(k, 1); s1.cars.push(c); }
        if ((c.lt -= dt) <= 0) { c.lt = rnd(6, 14); c.tgt = pick(lanes); }
        let dodge = false;
        for (let n = 1; n <= 6 && !dodge; n++) for (const o of segs[(s1.i + n) % N].cars) if (o !== c && o.speed < c.speed && Math.abs(o.off - c.off) < 0.5) { dodge = true; break; }
        const r0 = relZ(c);
        if (r0 < 0 && r0 > -16 * YD.SEG && c.speed > S.speed && Math.abs(c.off - S.x) < 0.6) dodge = true;
        if (dodge && Math.abs(c.tgt - c.off) < 0.1) { const free = lanes.filter((L) => Math.abs(L - c.off) > 0.3 && Math.abs(L - S.x) > 0.5); c.tgt = free.length ? free.sort((a, b) => Math.abs(a - c.off) - Math.abs(b - c.off))[0] : c.tgt; }
        c.off += clamp(c.tgt - c.off, -(dodge ? 1.2 : 0.35) * dt, (dodge ? 1.2 : 0.35) * dt);
        const rel = relZ(c);
        if (c.rel > 0 && rel <= 0 && rel > -20 * YD.SEG && !S.demo) { S.passed++; S.bonus += 250; }
        c.rel = rel;
      }
      // the checkpoints: their gate passed, time back
      if (!S.demo) {
        const k = S.cpN, lap = Math.floor(k / TK.cps.length), at = lap * LEN + TK.cps[k % TK.cps.length] * YD.SEG;
        if (S.trav + YD.PZ >= at) { S.cpN++; const ext = Math.max(16, 27 - S.cpN); S.time += ext; S.bonus += 2000; S.msg = T().cp + ' +' + ext; S.msgT = 2; }
        if (go) S.time -= dt;
        if (S.time <= 0 && !S.up) { S.time = 0; S.up = true; S.msg = T().timeup; S.msgT = 99; }
        if (S.up) { S.upT += dt; if (S.speed < 200 || S.upT > 5) S.over = true; }
      }
    };
    function project(p, cx, cy, cz) {
      p.c.x = -cx; p.c.y = p.w.y - cy; p.c.z = p.w.z - cz;
      const sc = YD.DEPTH / p.c.z; p.s.scale = sc;
      p.s.x = YD.W / 2 + sc * p.c.x * YD.W / 2; p.s.y = YD.HOR - sc * p.c.y * YD.H / 2; p.s.w = sc * YD.RW * YD.W / 2;
    }
    function rows(g, s, maxy) {                 // a segment's trapezoid, row by row in whole pixels: the bands, the dotted edges, the road, its lanes
      const y2 = s.p2.s.y, y1 = s.p1.s.y, top = Math.max(0, Math.round(y2)), bot = Math.min(YD.H, Math.round(y1), Math.round(maxy));
      for (let y = top; y < bot; y++) {
        const t = clamp((y + 0.5 - y2) / (y1 - y2), 0, 1), cx = s.p2.s.x + (s.p1.s.x - s.p2.s.x) * t, w = s.p2.s.w + (s.p1.s.w - s.p2.s.w) * t;
        R(g, 0, y, YD.W, 1, s.band ? YC.g1 : YC.g0);
        const rw = Math.max(1, w * 0.1), a = Math.round(cx - w - rw), b = Math.round(cx - w), c = Math.round(cx + w), d = Math.round(cx + w + rw);
        R(g, a, y, Math.max(1, b - a), 1, s.band ? YC.r0 : YC.rum); R(g, c, y, Math.max(1, d - c), 1, s.band ? YC.r0 : YC.rum);
        R(g, b, y, c - b, 1, s.band ? YC.r1 : YC.r0);
        if (!s.band && w > 8) { const lw = Math.max(1, Math.round(w * 0.03)); for (const k of [-1, 1]) R(g, Math.round(cx + k * w / 3 - lw / 2), y, lw, 1, YC.lane); }
      }
    }
    function spr(g, img, sc, x, y, clip) {      // a sprite at its depth: nearest-neighbour, its feet on (x, y), cut under the hill in front
      const dw = Math.round(img.width * sc * YD.CH), dh = Math.round(img.height * sc * YD.CH);
      if (dw < 1 || dh < 1) return;
      const dx = Math.round(x - dw / 2), dy = Math.round(y - dh), vis = Math.min(dh, Math.round(clip) - dy);
      if (vis <= 0) return;
      g.drawImage(img, 0, 0, img.width, Math.max(1, Math.round(img.height * vis / dh)), dx, dy, dw, vis);
    }
    function gate(g, s, clip) {                 // the checkpoint: two posts and a checkered banner over the road
      const sc = s.p1.s.scale, cx = s.p1.s.x, y = s.p1.s.y, hw = sc * YD.RW * YD.W / 2 * 1.2, H = Math.round(sc * YD.CH * 34), bw = Math.max(1, Math.round(sc * YD.CH * 4));
      if (H < 2) return;
      const top = Math.round(y - H), bh = Math.max(1, Math.round(H * 0.28)), x0 = Math.round(cx - hw), x1 = Math.round(cx + hw);
      const cl = (yy, h) => Math.max(0, Math.min(h, Math.round(clip) - yy));
      for (const px of [x0 - bw, x1]) R(g, px, top, bw, cl(top, H), YC.sh);
      const n = 16, cw = (x1 - x0) / n, ch = Math.max(1, bh >> 1);
      for (let r = 0; r < 2; r++) for (let i = 0; i < n; i++) {
        const xa = Math.round(x0 + i * cw), xb = Math.round(x0 + (i + 1) * cw), yy = top + r * ch, h = cl(yy, r ? bh - ch : ch);
        if (h > 0) R(g, xa, yy, xb - xa, h, (i + r) % 2 ? '#2a0a6a' : '#ffe6f2');
      }
    }
    G.draw = (g) => {
      const C = ydSprites();
      g.drawImage(C.sky, 0, 0);
      const strip = (img, ox, y) => { const o = ((Math.round(ox) % 256) + 256) % 256; g.drawImage(img, -o, y); g.drawImage(img, 256 - o, y); };
      strip(C.clouds, S ? S.cloudX : 0, 4); strip(C.city, S ? S.cityX : 0, YD.HOR - 26);
      R(g, 0, YD.HOR, YD.W, YD.H - YD.HOR, YC.g0); R(g, 0, YD.HOR, YD.W, 1, YC.glow);
      if (!S) return;
      const sh = S.shake > 0 ? (Math.floor(S.t * 30) % 2 ? 1 : -1) : 0;
      g.save(); g.translate(0, sh);
      const base = segAt(S.pos), bp = (S.pos % YD.SEG) / YD.SEG, ps = segAt(S.pos + YD.PZ), pp = ((S.pos + YD.PZ) % YD.SEG) / YD.SEG;
      const py = ps.p1.w.y + (ps.p2.w.y - ps.p1.w.y) * pp;
      let maxy = YD.H, x = 0, dx = -(base.curve * bp);
      for (let n = 0; n < YD.DRAW; n++) {
        const s = segs[(base.i + n) % N], cz = S.pos - (s.i < base.i ? LEN : 0);
        project(s.p1, S.x * YD.RW - x, py + YD.CH, cz); project(s.p2, S.x * YD.RW - x - dx, py + YD.CH, cz);
        x += dx; dx += s.curve; s.clip = maxy;
        if (s.p1.c.z <= YD.DEPTH || s.p2.s.y >= s.p1.s.y || s.p2.s.y >= maxy) continue;
        rows(g, s, maxy); maxy = s.p2.s.y;
      }
      for (let n = YD.DRAW - 1; n > 0; n--) {   // far to near: the gates, the roadside, the traffic, our car in its place among them
        const s = segs[(base.i + n) % N];
        if (s.p1.c.z <= YD.DEPTH) continue;
        if (s.cp) gate(g, s, s.clip);
        for (const o of s.spr) spr(g, C[o.k], s.p1.s.scale, s.p1.s.x + s.p1.s.scale * o.off * YD.RW * YD.W / 2, s.p1.s.y, s.clip);
        for (const c of s.cars) {
          const u = (c.z % YD.SEG) / YD.SEG, sc = s.p1.s.scale + (s.p2.s.scale - s.p1.s.scale) * u;
          const cx = s.p1.s.x + (s.p2.s.x - s.p1.s.x) * u + sc * c.off * YD.RW * YD.W / 2, cy = s.p1.s.y + (s.p2.s.y - s.p1.s.y) * u;
          spr(g, C[c.paint], sc, cx, cy, s.clip);
        }
        if (s === ps) {
          const b = !reduced && S.speed > YD.MAX * 0.3 && Math.floor(S.t * 12) % 2 ? 1 : 0;
          const img = S.brake ? (S.steer < 0 ? C.brakeL : S.steer > 0 ? C.brakeR : C.brake) : (S.steer < 0 ? C.left : S.steer > 0 ? C.right : C.player);
          g.drawImage(img, YD.W / 2 - 15, YD.H - 18 - b);
        }
      }
      g.restore();
      if (S.demo) return;
      // the HUD: the score, the time (large), the checkpoints; the speed under
      const t = T(), ink = YC.ink, shc = YC.sh;
      text(g, t.time, 64, 2, YC.dim, 1, 'c', shc); text(g, pad(Math.ceil(S.time), 2), 64, 8, S.time < 6 && !reduced && Math.floor(S.t * 4) % 2 ? YC.dim : ink, 2, 'c', shc);
      text(g, 'SCORE', 2, 2, YC.dim, 1, '', shc); text(g, pad(G.score(), 6), 2, 8, ink, 1, '', shc);
      text(g, 'HI', YD.W - 2, 2, YC.dim, 1, 'r', shc); text(g, pad(Math.max(G.hi || 0, G.score()), 6), YD.W - 2, 8, ink, 1, 'r', shc);
      text(g, pad(Math.round(S.speed / YD.MAX * 280), 3) + ' ' + t.kmh, 2, YD.H - 7, ink, 1, '', shc);
      text(g, (S.trav / YD.SEG * 1.3 / 1000).toFixed(1) + ' ' + t.dist, YD.W - 2, YD.H - 7, ink, 1, 'r', shc);
      if (S.cd > 0.2) text(g, String(Math.ceil(S.cd - 0.2)), 64, 40, ink, 3, 'c', shc);
      else if (S.msgT > 0) text(g, S.msg, 64, 44, ink, 1, 'c', shc);
    };
    G.drawTitle = (g, k) => {
      R(g, 20, 70, 88, 34, '#2a0a6a'); R(g, 20, 70, 88, 1, YC.rum); R(g, 20, 103, 88, 1, YC.rum);
      text(g, 'YUHI DRIVE', 64, 73, YC.ink, 2, 'c'); kana(g, 'ユウヒ ドライブ', 64, 85, '#f994c0', 'c');
      if (k) text(g, k, 64, 96, YC.ink, 1, 'c');
    };
    G.drawInfo = (g) => {
      R(g, 10, 66, 108, 40, '#2a0a6a'); R(g, 10, 66, 108, 1, YC.rum); R(g, 10, 105, 108, 1, YC.rum);
      T().yInfo.forEach((s, i) => text(g, s, 64, 69 + i * 7, i < 3 ? YC.ink : YC.dim, 1, 'c'));
    };
    G.reset(true);
    return G;
  }

  // ==== KUMA SUKUI (クマスクイ, bear scooping, as goldfish are scooped at a summer fair): the claw machine. Its glass seen from
  // the front, the box behind it in a little perspective (the back wall higher, narrower); plush bears in a pile, orange,
  // pink and purple as in the drawing, and one mint star from the next cabinet. As real cranes: the claw moves left and right
  // first (A to stop it), then to the back and the front (A again, or the time runs out), then drops, closes and rises by
  // itself; its grip is weak and a matter of luck (better centred, better held: it can let go as it closes, at the jolt at
  // the top, or on the way back), and it brings what it holds to the chute at the front left. A prize that falls over the
  // chute is won all the same. A light spot under the claw shows where it will land (as some cranes have). Six tries a coin ====
  const KS = { W: 104, H: 144, GH: 128, FRONT: 121, BACK: 89, C0: 6, C1: 15, CX: 52, SHR: 0.18, HX: 17, HZ: 0.14, CH0: 3, CH1: 31, CZ: 0.31 };
  const ksx = (x, z) => KS.CX + (x - KS.CX) * (1 - KS.SHR * z), kfy = (z) => KS.FRONT - (KS.FRONT - KS.BACK) * z, kcy = (z) => KS.C0 + (KS.C1 - KS.C0) * z;
  const KC = { wall: '#f8b0d0', wallLo: '#f2a0c8', ceil: '#ffd6e8', led: '#fff0f8', side: '#ee86bc', floor: '#e45aa4', lip: '#c83898', hole: '#5a1050',
    acr: '#fff4fa', k: '#3a1048', c: '#8a3a98', h: '#e6a0e0', bar: '#682878', ink: '#ffd0e4', hi: '#fff4fa', dim: '#d070a8', plate: '#5a1050', panel: '#2a0c3a', led2: '#12040e', pink: '#e83898' };
  const KS_KIND = {                              // a prize: its sprite, its value, how well it can be held
    o: { pal: { o: '#f8a070', l: '#ffcca0', s: '#d06858' }, big: false, val: 6000, grip: 0.7 },
    p: { pal: { o: '#f890b4', l: '#ffc4d8', s: '#d05a8c' }, big: false, val: 9000, grip: 0.62 },
    v: { pal: { o: '#9070d0', l: '#c0a8f0', s: '#6448a8' }, big: true, val: 16000, grip: 0.48 },
    a: { pal: null, big: false, val: 32000, grip: 0.4 } };
  const KS_BEAR = ['.oo......oo.', 'ossoooooosso', '.oooooooooo.', 'ooloooooooso', 'ooeooooooeso', 'oooowwwwooso', 'ooowwnnwwoso', '.oowwwwwwos.', '..oooooooo..', '.lloooooooo.', 'olooo..oooos', '.ooo....sss.'];
  const KS_BIG = ['..oo........oo..', '.osso......osso.', '.ossoooooooosso.', '..oooooooooooo..', '.oloooooooooooo.', 'oolooooooooooooo', 'oooeoooooooeooso', 'oooooowwwwooooso', 'ooooowwnnwwoooso',
    '.oooowwwwwwooos.', '..oooowwwwoooo..', '...oooooooooo...', '.lloooooooooooo.', 'olooooo..oooooos', 'oloooo....ooooos', '.ooo........sss.'];
  let KSC = null;
  function ksSprites() {
    if (KSC) return KSC;
    KSC = {};
    const base = { e: '#3a1030', n: '#5a1840', w: '#fff0e8' };
    for (const k of ['o', 'p', 'v']) KSC[k] = sprite(KS_KIND[k].big ? KS_BIG : KS_BEAR, Object.assign({}, base, KS_KIND[k].pal));
    KSC.a = sprite(HK_S.star[0], { m: '#74f5d6' });
    // the claw at four openings (3: wide open .. 0: shut); its hub, two side prongs (two pixels thick) and the middle one
    KSC.claw = [0, 1, 2, 3].map((o) => {
      const [c, g] = canvas(17, 13), cx = 8;
      const line = (x0, y0, x1, y1, col) => { const n = Math.max(Math.abs(x1 - x0), Math.abs(y1 - y0)); for (let i = 0; i <= n; i++) R(g, Math.round(x0 + (x1 - x0) * i / n), Math.round(y0 + (y1 - y0) * i / n), 1, 1, col); };
      const P = [[3, 4], [4 + o, 6], [4 + o, 9], [3 + o, 11], [1 + Math.round(o * 1.4), 12]];
      for (const s of [-1, 1]) for (let i = 0; i < P.length - 1; i++) { line(cx + s * (P[i][0] + 1), P[i][1], cx + s * (P[i + 1][0] + 1), P[i + 1][1], KC.k); line(cx + s * P[i][0], P[i][1], cx + s * P[i + 1][0], P[i + 1][1], KC.c); }
      R(g, cx, 4, 1, 6, KC.k); R(g, cx, 10, 1, 1, KC.c);
      R(g, cx - 1, 0, 3, 1, KC.k); R(g, cx - 3, 1, 7, 4, KC.k); R(g, cx - 2, 2, 5, 2, KC.c); R(g, cx - 2, 2, 2, 1, KC.h);
      return c;
    });
    // the box behind the glass: ceiling and its light, side walls, back wall, floor, the chute's hole and its clear walls
    const [bc, bg] = canvas(KS.W, KS.GH);
    const poly = (pts, col) => {               // a convex polygon, row by row, in whole pixels
      const y0 = Math.floor(Math.min(...pts.map((p) => p[1]))), y1 = Math.ceil(Math.max(...pts.map((p) => p[1])));
      for (let y = y0; y < y1; y++) {
        const yc = y + 0.5, xs = [];
        for (let i = 0; i < pts.length; i++) { const [ax, ay] = pts[i], [bx, by] = pts[(i + 1) % pts.length]; if ((ay <= yc && by > yc) || (by <= yc && ay > yc)) xs.push(ax + (yc - ay) / (by - ay) * (bx - ax)); }
        if (xs.length >= 2) { const a = Math.round(Math.min(...xs)), b = Math.round(Math.max(...xs)); if (b > a) R(bg, a, y, b - a, 1, col); }
      }
    };
    const P = (x, z, y) => [ksx(x, z), y === undefined ? kfy(z) : y];
    R(bg, 0, 0, KS.W, KS.GH, KC.lip);
    poly([[0, 0], [KS.W, 0], P(KS.W, 1, kcy(1)), P(0, 1, kcy(1))], KC.ceil);
    poly([[0, 0], P(0, 1, kcy(1)), P(0, 1), P(0, 0)], KC.side); poly([[KS.W, 0], P(KS.W, 1, kcy(1)), P(KS.W, 1), P(KS.W, 0)], KC.side);
    const bx0 = Math.round(ksx(0, 1)), bx1 = Math.round(ksx(KS.W, 1)), by0 = Math.round(kcy(1)), by1 = Math.round(kfy(1));
    R(bg, bx0, by0, bx1 - bx0, by1 - by0, KC.wall); R(bg, bx0, by1 - 10, bx1 - bx0, 10, KC.wallLo);
    [[3, 0, 3], [1, 1, 7], [0, 2, 9], [0, 3, 9], [1, 4, 7], [2, 5, 5], [3, 6, 3], [4, 7, 1]].forEach(([dx, dy, w]) => R(bg, 48 + dx, 34 + dy, w, 1, '#f490c0'));   // (a heart on the back wall)
    poly([P(0, 1), P(KS.W, 1), P(KS.W, 0), P(0, 0)], KC.floor);
    R(bg, 0, 0, KS.W, 2, KC.led); R(bg, 0, 2, KS.W, 1, '#ffe2ee');
    poly([P(KS.CH0 + 1, 0.03), P(KS.CH1 - 1, 0.03), P(KS.CH1 - 1, KS.CZ - 0.02), P(KS.CH0 + 1, KS.CZ - 0.02)], KC.hole);
    KSC.box = bc;
    return KSC;
  }
  function kumaGame() {
    const G = { W: KS.W, H: KS.H, title: 'KUMA SUKUI', kana: 'クマスクイ', ink: { bg: KC.wall, ink: KC.hi, dim: KC.ink, hi: '#ff86d6', plate: KC.plate, sh: KC.plate } };
    let S = null;
    const inChute = (x, z) => x > KS.CH0 + 2 && x < KS.CH1 - 2 && z < KS.CZ - 0.03;
    function pile() {                           // three rows of prizes back to front (the chute's corner kept clear), a few on top of others
      const P = [], kinds = () => (Math.random() < 0.45 ? 'o' : Math.random() < 0.7 ? 'p' : 'v');
      for (const [z, x0, x1] of [[0.84, 12, 94], [0.6, 10, 96], [0.37, 36, 98], [0.15, 38, 98]]) {
        for (let x = x0 + rnd(0, 4); x < x1;) {
          const k = kinds(), sp = ksSprites()[k], w = sp.width;
          if (x + w > x1) break;
          P.push({ k, x: x + w / 2, z: z + rnd(-0.04, 0.04), lift: 0, w, h: sp.height, st: 'pile', vy: 0 });
          x += w + rnd(-1, 2);
        }
      }
      const a = P[Math.floor(rnd(0, P.length * 0.5))]; a.k = 'a'; a.w = ksSprites().a.width; a.h = ksSprites().a.height;
      for (let n = 0; n < 7; n++) { const b = pick(P.filter((p) => p.lift === 0 && p.k !== 'a' && !P.some((q) => q.lift > 0 && Math.abs(q.x - p.x) < 8 && Math.abs(q.z - p.z) < 0.1)));
        if (!b) break; P.push({ k: Math.random() < 0.5 ? 'o' : 'p', x: b.x + rnd(-2, 2), z: b.z - 0.02, lift: b.h - 3, w: 12, h: 12, st: 'pile', vy: 0 }); }
      return P;
    }
    G.reset = (demo) => {
      S = { demo, prizes: pile(), tries: 6, score: 0, won: [], claw: { x: KS.HX, z: KS.HZ, L: 4, o: 0, st: 'idle', t: 0, held: null, q: 0 }, timer: 15, pity: 0,
        msg: '', msgT: 0, t: 0, over: false, demoT: 2 };
      if (!demo) S.claw.st = 'mx';
    };
    G.score = () => (S ? S.score : 0);
    G.over = () => !!(S && S.over);
    G.st = () => S;
    function topAt(x, z) {                      // the highest prize top under a point (px above the floor), and that prize
      let top = 0, who = null;
      for (const p of S.prizes) if (p.st === 'pile' && Math.abs(p.x - x) < p.w / 2 + 1 && Math.abs(p.z - z) < 0.11 && p.lift + p.h > top) { top = p.lift + p.h; who = p; }
      return [top, who];
    }
    function support(p) {                       // what a prize rests on: the floor (0) or the top of one under it (sunk 3 px into it)
      let h = 0;
      for (const q of S.prizes) if (q !== p && q.st === 'pile' && q.lift < p.lift && Math.abs(q.x - p.x) < (p.w + q.w) / 4 && Math.abs(q.z - p.z) < 0.1) h = Math.max(h, q.lift + q.h - 3);
      return h;
    }
    function settle(dt) {                       // gravity: a prize with nothing under it falls; over the chute, through its hole: won
      for (const p of S.prizes) {
        if (p.st !== 'pile' && p.st !== 'fall') continue;
        const chute = inChute(p.x, p.z), rest = chute ? -99 : support(p);
        if (p.lift > rest + 0.01) {
          p.st = 'fall'; p.vy += 260 * dt; p.lift = Math.max(rest, p.lift - p.vy * dt);
          if (chute) { if (p.lift < -p.h - 4) win(p); } else if (p.lift <= rest) { p.lift = rest; p.vy = 0; p.st = 'pile'; }
        } else if (p.st === 'fall') { p.st = 'pile'; p.vy = 0; }
      }
    }
    function win(p) {
      p.st = 'won'; S.won.push(p.k); S.pity = 0;
      if (!S.demo) { const v = KS_KIND[p.k].val; S.score += v; S.msg = T().win + ' +' + v; S.msgT = 1.6; }
    }
    function drop(C) { C.st = 'open'; C.t = 0; }
    function auto() {                           // the demo: wander, drop, come back (it never takes a prize)
      const I = { held: {}, hit: {} }, C = S.claw;
      if (C.st === 'mx' || C.st === 'mz') {
        if (C.tx === undefined) { C.tx = rnd(40, 92); C.tz = rnd(0.3, 0.85); }
        if (C.st === 'mx') { if (Math.abs(C.x - C.tx) > 1.5) I.held[C.x < C.tx ? 'r' : 'l'] = 1; else I.hit.a = 1; }
        else { if (Math.abs(C.z - C.tz) > 0.03) I.held[C.z < C.tz ? 'u' : 'd'] = 1; else I.hit.a = 1; }
      }
      return I;
    }
    G.update = (dt, I) => {
      if (!S) G.reset(true);
      S.t += dt; S.msgT = Math.max(0, S.msgT - dt);
      if (S.demo) { if (S.claw.st === 'idle' && (S.demoT -= dt) <= 0) { S.claw.st = 'mx'; S.claw.tx = undefined; S.timer = 15; } I = auto(); }
      settle(dt);
      if (S.over) return;
      const C = S.claw, sp = 30 * dt;
      C.t += dt;
      if (C.st === 'mx' || C.st === 'mz') {
        S.timer -= dt;
        if (C.st === 'mx') { if (I.held.l) C.x -= sp; if (I.held.r) C.x += sp; if (I.hit.a || I.hit.b) { C.st = 'mz'; } }
        else { if (I.held.u) C.z += 0.5 * dt; if (I.held.d) C.z -= 0.5 * dt; if (I.hit.a || I.hit.b) drop(C); }
        C.x = clamp(C.x, 9, KS.W - 9); C.z = clamp(C.z, 0.06, 0.92);
        if (S.timer <= 0) drop(C);
      } else if (C.st === 'open') { C.o = Math.min(3, Math.floor(C.t / 0.08)); if (C.t > 0.35) { C.st = 'down'; C.t = 0; } }
      else if (C.st === 'down') {
        C.L += 36 * dt;
        const [top] = topAt(C.x, C.z), stop = kfy(C.z) - top - kcy(C.z) - 13 + 3;
        if (C.L >= stop) { C.L = stop; C.st = 'grab'; C.t = 0; }
      } else if (C.st === 'grab') {
        C.o = Math.max(0, 3 - Math.floor(C.t / 0.12));
        if (C.t > 0.55) {
          C.st = 'up'; C.t = 0;
          let best = null, bq = 0;
          if (!S.demo) for (const p of S.prizes) {
            if (p.st !== 'pile') continue;
            const dx = Math.abs(p.x - C.x), dz = Math.abs(p.z - C.z), tip = kcy(C.z) + C.L + 12, ptop = kfy(p.z) - p.lift - p.h;
            if (dx > p.w / 2 + 2 || dz > 0.15 || tip < ptop - 2 || tip > ptop + 6) continue;
            const q = KS_KIND[p.k].grip * Math.pow(1 - dx / (p.w / 2 + 3), 0.6) * Math.pow(1 - dz / 0.16, 0.5) + S.pity;
            if (q > bq) { bq = q; best = p; }
          }
          if (best && Math.random() < Math.min(0.95, bq * 1.05)) { C.held = best; best.st = 'held'; C.q = Math.min(1, bq); }
          else if (best) { C.slip = true; }           // (it closed on it and it slid out)
        }
      } else if (C.st === 'up') {
        C.L -= 26 * dt;
        if (C.L <= 4) { C.L = 4; C.st = 'ret'; C.t = 0; if (C.held && Math.random() < 0.3 * (1 - C.q) + 0.08) let_go(C); }   // (the jolt at the top)
      } else if (C.st === 'ret') {
        if (C.held && Math.random() < dt * 0.2 * (1 - C.q)) let_go(C);
        if (C.z > KS.HZ + 0.01) C.z = Math.max(KS.HZ, C.z - 0.45 * dt);
        else if (C.x > KS.HX + 0.5) C.x = Math.max(KS.HX, C.x - sp);
        else { C.st = 'rel'; C.t = 0; }
      } else if (C.st === 'rel') {
        C.o = Math.min(3, Math.floor(C.t / 0.08));
        if (C.held && C.t > 0.15) { const p = C.held; C.held = null; p.st = 'fall'; p.x = C.x; p.z = C.z; p.lift = kfy(C.z) - (kcy(C.z) + C.L + 9 + p.h); p.vy = 0; }
        if (C.t > 0.9) {
          C.o = 0;
          if (!S.demo) {
            const got = S.won.length > (C.wonBefore || 0);
            if (!got) { S.pity = Math.min(0.3, S.pity + 0.05); if (!S.msgT) { S.msg = C.slip || C.dropped ? T().slip : T().miss; S.msgT = 1.3; } }
            S.tries--; C.slip = C.dropped = false; C.wonBefore = S.won.length;
            if (S.tries <= 0) { C.st = 'end'; C.t = 0; } else { C.st = 'mx'; S.timer = 15; }
          } else { C.st = 'idle'; S.demoT = rnd(1.5, 3); }
        }
      } else if (C.st === 'end') { if (C.t > 1.6 && !S.prizes.some((p) => p.st === 'fall')) S.over = true; }
      if (C.held) { C.held.x = C.x; C.held.z = C.z; }
    };
    function let_go(C) { const p = C.held; C.held = null; C.dropped = true; p.st = 'fall'; p.vy = 0; p.lift = kfy(C.z) - (kcy(C.z) + C.L + 9 + p.h); }
    G.draw = (g) => {
      const K = ksSprites();
      g.drawImage(K.box, 0, 0);
      if (!S) return;
      const C = S.claw, list = S.prizes.filter((p) => p.st === 'pile' || p.st === 'fall').sort((a, b) => b.z - a.z || a.lift - b.lift);
      const drawP = (p, x, y) => { const sp = K[p.k]; g.drawImage(sp, Math.round(x - sp.width / 2), Math.round(y - sp.height)); };
      // the claw at its depth among the prizes (those in front of it hide it): its bar across the box, its carriage, its
      // cable, what it holds, the claw
      const cx = Math.round(ksx(C.x, C.z)), ry = Math.round(kcy(C.z)), hy = Math.round(kcy(C.z) + C.L);
      let clawDone = false;
      const claw = () => {
        const a = Math.round(ksx(0, C.z)), b = Math.round(ksx(KS.W, C.z));
        R(g, a, ry - 2, b - a, 2, KC.bar); R(g, a, ry - 2, b - a, 1, KC.c); R(g, cx - 4, ry - 3, 9, 4, KC.k); R(g, cx - 3, ry - 2, 7, 2, KC.c);
        R(g, cx, ry, 1, Math.max(0, hy - ry), KC.k);
        if (C.held) drawP(C.held, cx, hy + 9 + C.held.h);
        g.drawImage(K.claw[C.o], cx - 8, hy);
        clawDone = true;
      };
      g.save(); g.beginPath(); g.rect(0, 0, KS.W, KS.FRONT + 1); g.clip();   // (what falls into the chute goes under the floor)
      for (const p of list) {
        if (!clawDone && p.z < C.z) claw();
        if (p.st === 'fall' && inChute(p.x, p.z)) { g.save(); g.beginPath(); g.rect(0, 0, KS.W, Math.round(kfy(p.z))); g.clip(); drawP(p, ksx(p.x, p.z), kfy(p.z) - p.lift); g.restore(); }
        else drawP(p, ksx(p.x, p.z), kfy(p.z) - p.lift);
      }
      if (!clawDone) claw();
      g.restore();
      // the chute's clear walls in front of all
      const ax = (x, z) => Math.round(ksx(x, z)), ay = (z, h) => Math.round(kfy(z) - h);
      R(g, ax(KS.CH0, 0), ay(0, 18), ax(KS.CH1, 0) - ax(KS.CH0, 0) + 1, 1, KC.acr);
      R(g, ax(KS.CH1, 0), ay(0, 18), 1, 18, KC.acr);
      R(g, ax(KS.CH1, KS.CZ), ay(KS.CZ, 18), 1, 18, '#ffdcec');
      for (let i = 0; i <= 8; i++) { const z = KS.CZ * i / 8; R(g, ax(KS.CH1, z), ay(z, 18), 1, 1, KC.acr); }
      // the light spot where the claw would land, while it can still be moved
      if (C.st === 'mx' || C.st === 'mz') { const [top] = topAt(C.x, C.z), sy = Math.round(kfy(C.z) - top); R(g, cx - 2, sy - 1, 5, 1, KC.acr); R(g, cx - 1, sy - 2, 3, 3, KC.acr); }
      // a glint on the glass
      for (let i = 0; i < 9; i++) R(g, 88 + i, 22 - i * 2, 1, 2, '#ffe8f4');
      if (S.msgT > 0) text(g, S.msg, 52, 44, KC.hi, 1, 'c', KC.plate);
      // under the glass: the prize door (what was won, in it) and the display (tries, time, score)
      R(g, 0, KS.GH, KS.W, KS.H - KS.GH, KC.panel);
      R(g, 2, 130, 36, 13, KC.pink); R(g, 3, 131, 34, 11, KC.led2);
      g.save(); g.beginPath(); g.rect(3, 131, 34, 11); g.clip();
      S.won.slice(-4).forEach((k, i) => { const sp = K[k]; g.drawImage(sp, 4 + i * 8, 142 - Math.min(sp.height, 9)); });
      g.restore();
      R(g, 41, 130, 61, 13, KC.k); R(g, 42, 131, 59, 11, KC.led2);
      if (!S.demo) {
        text(g, T().tries + ' ' + Math.max(0, S.tries), 44, 132, KC.ink);
        if (C.st === 'mx' || C.st === 'mz') text(g, pad(Math.ceil(Math.max(0, S.timer)), 2), 99, 132, KC.hi, 1, 'r');
        text(g, pad(S.score, 6), 44, 138, KC.hi);
        text(g, C.st === 'mx' ? '← →' : C.st === 'mz' ? '↑ ↓' : '', 99, 138, KC.dim, 1, 'r');
      } else text(g, 'HI ' + pad(G.hi || 0, 6), 44, 131, KC.ink);
    };
    G.drawTitle = (g, k) => {
      R(g, 10, 40, 84, 34, KC.plate); R(g, 10, 40, 84, 1, '#ff86d6'); R(g, 10, 73, 84, 1, '#ff86d6');
      text(g, 'KUMA SUKUI', 52, 43, KC.hi, 2, 'c'); kana(g, 'クマスクイ', 52, 55, '#ff9ad0', 'c');
      if (k) text(g, k, 52, 65, KC.hi, 1, 'c');
    };
    G.drawInfo = (g) => {
      const K = ksSprites();
      R(g, 4, 22, 96, 82, KC.plate); R(g, 4, 22, 96, 1, '#ff86d6'); R(g, 4, 103, 96, 1, '#ff86d6');
      [['o', 6000], ['p', 9000], ['v', 16000], ['a', 32000]].forEach(([k, v], i) => {   // (two by two: the prize standing on its line, its value)
        const sp = K[k], cx = 8 + (i % 2) * 46, by = 43 + Math.floor(i / 2) * 20;
        g.drawImage(sp, cx + ((16 - sp.width) >> 1), by - sp.height); text(g, String(v), cx + 18, by - 6, KC.hi);
      });
      T().kInfo.forEach((s, i) => text(g, s, 52, 68 + i * 7, i < 2 ? KC.hi : KC.ink, 1, 'c'));
    };
    G.reset(true);
    return G;
  }

  // ==== the machine around a game: the coin, the start, the attract's pages (the title over the game playing itself, the
  // high scores, how to play), the game over, the initials for a new high score (up and down for a letter, left and right
  // or A to go on; or typed), the pause. Each machine its own game and its own table, kept while the page lives ====
  const MACH = [{ game: hoshiGame, face: 'cab1', hs: 'mtsfj-arcade-hoshikuzu-1', cred: [126, 117, 'r'] },
    { game: yuhiGame, face: 'cab2', hs: 'mtsfj-arcade-yuhi', cred: [64, 3, 'c'] },
    { game: hoshiGame, face: 'cab1', hs: 'mtsfj-arcade-hoshikuzu-3', cred: [126, 117, 'r'] },
    { game: kumaGame, face: 'claw', hs: 'mtsfj-arcade-kuma', cred: [44, 138, ''] }];
  const PAGES = [9, 6, 6];
  const NOI = { held: {}, hit: {}, q: [] };
  const LET = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ.';
  function machine(i) {
    const M = MACH[i];
    if (M.sh) return M.sh;
    const G = M.game(), [cv, g] = canvas(G.W, G.H);
    const S = { i, M, G, cv, g, ph: 'attract', t: 0, page: 0, pageT: 0, credits: 0, tab: hsLoad(M.hs), ent: null, last: -1, overT: 0, paused: false, rep: 0 };
    G.hi = S.tab[0][1];
    return (M.sh = S);
  }
  function shStep(S, dt, I) {
    const G = S.G;
    if (I.hit.pause && S.ph === 'play') { S.paused = !S.paused; say(S.paused ? T().said.paused : ''); }
    if (S.paused) { if (I.hit.start || I.hit.enter) S.paused = false; return; }
    S.t += dt;
    if (S.ph !== 'enter') for (const e of I.q) {  // the coins and the start, in their order (a coin and a start in one frame: both)
      const startable = S.ph === 'attract' && S.credits > 0;
      if (e === 'coin' || (e === 'enter' && S.ph !== 'over' && !startable)) {
        S.credits = Math.min(9, S.credits + 1); FL.coin = 0.2;
        if (S.ph === 'attract') { S.page = 0; S.pageT = 0; }
        say(T().said.coin + S.credits);
      } else if (startable && (e === 'start' || e === 'enter' || e === 'a')) {
        S.credits--; G.reset(false); S.ph = 'play'; S.last = -1; say(T().said.start); return;
      } else if (S.ph === 'attract' && (e === 'start' || e === 'a')) { S.page = 0; S.pageT = 0; }   // (START with no coin: the title, its INSERT COIN)
    }
    if (S.ph === 'attract') {
      G.update(dt, NOI);
      if ((S.pageT += dt) > PAGES[S.page]) { S.pageT = 0; S.page = (S.page + 1) % PAGES.length; if (S.page === 0) S.last = -1; }
    } else if (S.ph === 'play') {
      G.update(dt, I);
      if (G.over()) {
        S.ph = 'over'; S.overT = 3;
        const sc = G.score(); S.rank = S.tab.findIndex((e) => sc > e[1]);
        say(T().said.over + sc + T().said.pts);
      }
    } else if (S.ph === 'over') {
      G.update(dt, NOI);
      if ((S.overT -= dt) <= 0) {
        if (S.rank >= 0) { S.ph = 'enter'; S.ent = { ini: iniLoad().split(''), pos: 0, t: 0, score: G.score() }; say(T().said.rec); }
        else { S.ph = 'attract'; S.page = 1; S.pageT = 0; G.reset(true); }
      }
    } else if (S.ph === 'enter') {
      const E = S.ent, step = (d) => { const k = (LET.indexOf(E.ini[E.pos]) + d + LET.length) % LET.length; E.ini[E.pos] = LET[k]; };
      E.t += dt;
      for (const e of I.q) {                    // (the presses in their order: typed fast, none lost)
        if (E.pos >= 3) break;
        if (e.length === 1 && e >= 'A' && e <= 'Z') { E.ini[E.pos] = e; E.pos++; }
        else if (e === 'u' || e === 'd') { step(e === 'u' ? 1 : -1); S.rep = 0.4; }
        else if (e === 'r' || e === 'a' || e === 'enter' || e === 'start') E.pos++;
        else if ((e === 'l' || e === 'b' || e === 'back') && E.pos > 0) E.pos--;
      }
      if (!I.q.some((e) => e === 'u' || e === 'd') && (I.held.u || I.held.d) && (S.rep -= dt) <= 0) { step(I.held.u ? 1 : -1); S.rep = 0.09; }
      if (E.pos >= 3 || E.t > 45) {
        const ini = E.ini.join('');
        S.tab.splice(S.rank, 0, [ini, E.score]); S.tab.length = 5; hsSave(S.M.hs, S.tab); iniSave(ini);
        G.hi = S.tab[0][1]; S.last = S.rank; S.ph = 'attract'; S.page = 1; S.pageT = 0; S.ent = null; G.reset(true);
      }
    }
  }
  function shDraw(S) {
    const G = S.G, g = S.g, t = T(), I = G.ink, W = G.W, H = G.H, on = reduced || Math.floor(S.t * 2.2) % 2 === 0;
    const plate = (x, y, w, h) => { R(g, x, y, w, h, I.plate); R(g, x, y, w, 1, I.hi); R(g, x, y + h - 1, w, 1, I.hi); };
    G.draw(g);
    if (S.ph === 'attract') {
      if (S.page === 0) G.drawTitle(g, on ? (S.credits ? t.start : t.coin) : '');
      else if (S.page === 1) {
        const w = Math.min(W - 8, 104), x = (W - w) >> 1, y = Math.round(H / 2 - 30);
        plate(x, y, w, 50); text(g, t.hs, W / 2, y + 4, I.hi, 1, 'c');
        S.tab.forEach(([n, v], k) => {
          const yy = y + 14 + k * 7, c = k === S.last ? I.hi : I.ink;
          text(g, t.ranks[k], x + 6, yy, k === S.last ? I.hi : I.dim); text(g, n, x + 30, yy, c); text(g, pad(v, 6), x + w - 6, yy, c, 1, 'r');
        });
      } else G.drawInfo(g);
      const [cx, cy, ca] = S.M.cred; text(g, t.credit + ' ' + S.credits, cx, cy, I.ink, 1, ca, I.sh);
    } else if (S.ph === 'over') {
      const w = textW(t.over, 1) + 16; plate((W - w) >> 1, Math.round(H / 2 - 8), w, 15); text(g, t.over, W / 2, Math.round(H / 2 - 3), I.ink, 1, 'c');
    } else if (S.ph === 'enter') {
      const E = S.ent, w = W - 10, x = 5, y = Math.round(H / 2 - 30);
      plate(x, y, w, 60);
      text(g, t.rec, W / 2, y + 4, I.hi, 1, 'c');
      text(g, t.ranks[S.rank] + '  ' + pad(E.score, 6), W / 2, y + 13, I.ink, 1, 'c');
      text(g, t.ini, W / 2, y + 22, I.dim, 1, 'c');
      for (let k = 0; k < 3; k++) {
        const lx = Math.round(W / 2 - 20 + k * 16);
        text(g, E.ini[k], lx, y + 31, k === E.pos ? I.hi : I.ink, 2);
        if (k === E.pos && on) R(g, lx - 2, y + 44, 10, 1, I.hi);   // (wider than the letter: not read as a cedilla)
      }
      text(g, t.keysIni, W / 2, y + 50, I.dim, 1, 'c');
    }
    if (S.paused) { const w = Math.min(W - 8, Math.max(textW(t.resume) + 12, 60)); plate((W - w) >> 1, Math.round(H / 2 - 12), w, 22); text(g, t.pause, W / 2, Math.round(H / 2 - 8), I.hi, 1, 'c'); text(g, t.resume, W / 2, Math.round(H / 2 + 1), I.ink, 1, 'c'); }
  }

  // ==== the faces: each machine's front as the drawing shows it, in pixels on one canvas with the game's screen in it.
  // The cabinets: the pink-edged navy body, the marquee (the first's pink, blue and teal stripes, the second's pink checks),
  // its name on a plate in it; the bezel; the deck with the red ball-top joystick and the buttons (red A, amber B, purple
  // START); the coin door with its lit red slot. The claw machine: its lit header, its pink posts and the cyan edge of its
  // glass, its deck (joystick, the big claw button, START), its coin slot, its pink and navy checks. Two layouts: tall, as
  // drawn; wide, for a phone held sideways (the deck split either side of the screen). Its controls: where they are, for the
  // touch (each a target of 44 CSS px at least, the nearest one when they would overlap) ----
  const CP = { n0: '#050a22', n1: '#0a1640', n2: '#0e1d52', n3: '#1e3270', b1: '#0b2050', b2: '#1a3a7a', p0: '#6a1a5e', p1: '#d03096', p2: '#ff74c8', lab: '#5a74b8',
    k0: '#4a0c3e', k1: '#e83898', k2: '#ff86d6', kd: '#3a1a6a', kdl: '#5a3a9a', kb: '#2a1458' };
  const BTN = { red: ['#e0284c', '#ff8aa4', '#7a1028', '#ff6a88'], amber: ['#e8a03c', '#ffd890', '#7a4410', '#ffd070'], purple: ['#8044d0', '#c0a0ff', '#3a1870', '#b088ff'],
    pink: ['#ff4aa0', '#ffb0d8', '#8a1050', '#ff9ad0'] };
  const BALL = ['..rrrr..', '.rhhrrr.', 'rhhrrrrr', 'rhrrrrrr', 'rrrrrrrd', 'rrrrrrdd', '.rrrrdd.', '..dddd..'];
  let BALLC = null;
  const FACES = {};
  function face(look, wide) {
    const key = look + (wide ? 'W' : 'T');
    if (FACES[key]) return FACES[key];
    const claw = look === 'claw', F = claw ? clawFace(wide) : cabFace(look, wide);
    return (FACES[key] = F);
  }
  function marquee(g, look, x, y, w, h, small) {
    for (let v = 0; v < h; v++) for (let u = 0; u < w; u++) {
      let c;
      if (look === 'cab1') c = ['#1838a8', '#0878b8', '#1838a8', '#c82890', '#e858b0', '#0a1a6a'][Math.floor((u + v + 600) / 6) % 6];
      else {
        const edge = Math.min(u, w - 1 - u) / (w / 2), chk = (Math.floor(u / 3) + Math.floor(v / 3)) % 2 === 0, band = (u + v) % 40 < 9 && Math.abs(u - w / 2) < w / 4;
        c = band ? '#181878' : chk && edge < 0.32 && ((u * 7 + v * 3) % 11) / 11 > edge * 2.2 ? '#181878' : '#b82888';
      }
      R(g, x + u, y + v, 1, 1, c);
    }
    const name = look === 'cab1' ? 'HOSHIKUZU' : 'YUHI DRIVE', kn = look === 'cab1' ? 'ホシクズ' : 'ユウヒ', ink = look === 'cab1' ? '#74f5d6' : '#ffd8e6';
    const pw = Math.max(kanaW(kn), small ? 0 : textW(name)) + 10, ph = small ? 9 : 16, px = x + ((w - pw) >> 1), py = y + ((h - ph) >> 1);
    R(g, px - 1, py - 1, pw + 2, ph + 2, CP.n0); R(g, px, py, pw, ph, '#0a0a2a');
    kana(g, kn, px + pw / 2, py + 1, ink, 'c');
    if (!small) text(g, name, px + pw / 2, py + 10, look === 'cab1' ? '#3dcbb8' : '#f8a8c8', 1, 'c');
  }
  function cabFace(look, wide) {
    const W = wide ? 256 : 152, H = wide ? 158 : 222, [c, g] = canvas(W, H), F = { W, H, chrome: c, ctl: [], labs: [] };
    const x0 = wide ? 56 : 0, bw = wide ? 144 : 152;
    R(g, 0, 0, W, H, CP.n1);
    if (wide) R(g, 0, 0, W, H, '#070f30');
    R(g, x0, 0, bw, H, CP.n1); R(g, x0, 0, 1, H, CP.p0); R(g, x0 + 1, 0, 1, H, CP.p1); R(g, x0 + bw - 2, 0, 1, H, CP.p1); R(g, x0 + bw - 1, 0, 1, H, CP.p0); R(g, x0, 0, bw, 1, CP.p1);
    if (!wide) {
      R(g, 4, 3, 144, 21, CP.n0); marquee(g, look, 5, 4, 142, 19); R(g, 2, 24, 148, 2, CP.n0);
      R(g, 6, 27, 140, 135, CP.n0); R(g, 7, 28, 138, 133, CP.b1); R(g, 7, 28, 138, 1, CP.b2); R(g, 11, 32, 130, 126, CP.b2); F.scr = [12, 33];
      R(g, 2, 162, 148, 1, CP.n0); R(g, 2, 163, 148, 28, CP.n2); R(g, 2, 163, 148, 1, CP.n3); R(g, 2, 191, 148, 2, CP.p1); R(g, 2, 193, 148, 1, CP.p0); R(g, 2, 194, 148, 3, CP.n0);
      R(g, 10, 200, 30, 16, CP.n0); R(g, 11, 201, 28, 14, '#0b1440'); for (let y = 203; y < 214; y += 3) R(g, 13, y, 24, 1, CP.n0);
      R(g, 112, 200, 30, 16, CP.n0); R(g, 113, 201, 28, 14, '#0b1440'); for (let y = 203; y < 214; y += 3) R(g, 115, y, 24, 1, CP.n0);
      R(g, 48, 199, 56, 20, CP.n0); R(g, 49, 200, 54, 18, CP.n2); R(g, 49, 200, 54, 1, CP.n3); R(g, 2, 219, 148, 3, CP.n0);
      F.ctl.push({ k: 'stick', x: 26, y: 187, zone: [4, 163, 50, 196] }, { k: 'a', x: 78, y: 176, big: 1, col: BTN.red }, { k: 'b', x: 100, y: 176, big: 1, col: BTN.amber },
        { k: 'start', x: 124, y: 178, col: BTN.purple }, { k: 'coin', x: 60, y: 209 });
      F.labs.push([78, 184, 'A'], [100, 184, 'B'], [124, 185, 'START'], [66, 206, 3, '']);
    } else {
      R(g, 60, 2, 136, 13, CP.n0); marquee(g, look, 61, 3, 134, 11, true);
      R(g, 58, 16, 140, 140, CP.n0); R(g, 59, 17, 138, 138, CP.b1); R(g, 59, 17, 138, 1, CP.b2); R(g, 63, 21, 130, 126, CP.b2); F.scr = [64, 22]; R(g, 56, 156, 144, 2, CP.n0);
      for (const wx of [0, 200]) {
        R(g, wx, 34, 56, 98, CP.n0); R(g, wx + 1, 35, 54, 92, CP.n2); R(g, wx + 1, 35, 54, 1, CP.n3); R(g, wx + 1, 127, 54, 2, CP.p1); R(g, wx + 1, 129, 54, 1, CP.p0);
      }
      F.ctl.push({ k: 'stick', x: 28, y: 92, zone: [2, 36, 54, 126] }, { k: 'a', x: 213, y: 58, big: 1, col: BTN.red }, { k: 'b', x: 243, y: 58, big: 1, col: BTN.amber },
        { k: 'start', x: 213, y: 100, col: BTN.purple }, { k: 'coin', x: 243, y: 102 });   // (30 pixels apart: 44 CSS px at 1.5 a pixel)
      F.labs.push([213, 66, 'A'], [243, 66, 'B'], [213, 108, 'START'], [243, 111, 3, 'c']);
    }
    return F;
  }
  function clawFace(wide) {
    const W = wide ? 240 : 128, H = wide ? 162 : 226, [c, g] = canvas(W, H), F = { W, H, chrome: c, ctl: [], labs: [] };   // (wide: short enough
    const x0 = wide ? 56 : 0, hh = wide ? 10 : 22;                                                                         // for 5 device px on a phone)
    R(g, 0, 0, W, H, wide ? '#1c0c38' : CP.kb);
    R(g, x0, 0, 128, hh, CP.k0); R(g, x0 + 1, 1, 126, hh - 2, '#ff9ad0'); R(g, x0 + 2, 2, 124, hh - 4, '#ffc0dc'); R(g, x0 + 2, 2, 124, wide ? 1 : 2, '#fff0f8');
    const mid = x0 + 64;
    kana(g, 'クマスクイ', mid, wide ? 2 : 5, '#a0187a', 'c'); if (!wide) text(g, 'KUMA SUKUI', mid, 14, '#c83898', 1, 'c');
    const top = hh, gx = x0 + 12, bot = top + 2 + KS.H;          // the posts, the glass's frame (the game: glass and the panel under it)
    R(g, x0, top, 10, bot - top + 2, CP.k1); R(g, x0 + 2, top, 1, bot - top + 2, CP.k2); R(g, x0 + 8, top, 2, bot - top + 2, '#8a1f6e');
    R(g, x0 + 118, top, 10, bot - top + 2, CP.k1); R(g, x0 + 118, top, 2, bot - top + 2, '#8a1f6e'); R(g, x0 + 125, top, 1, bot - top + 2, CP.k2);
    R(g, x0 + 10, top, 108, 2, CP.k0); R(g, x0 + 10, top, 2, bot - top + 2, CP.k0); R(g, x0 + 116, top, 2, bot - top + 2, CP.k0); R(g, x0 + 116, top + 2, 1, KS.GH, '#7fe0f0');
    R(g, x0, bot, 128, 2, CP.k0);
    F.scr = [gx, top + 2];
    if (!wide) {
      R(g, 0, 170, 128, 1, CP.k0); R(g, 0, 171, 128, 24, CP.kd); R(g, 0, 171, 128, 1, CP.kdl); R(g, 0, 195, 128, 2, CP.k1); R(g, 0, 197, 128, 1, '#8a1f6e');
      R(g, 0, 198, 128, 12, CP.kb);
      for (let j = 0; 210 + j * 4 < H; j++) for (let i = 0; i * 4 < W; i++) R(g, i * 4, 210 + j * 4, 4, 4, (i + j) % 2 ? '#e83898' : '#181858');
      F.ctl.push({ k: 'stick', x: 22, y: 191, zone: [2, 171, 44, 195] }, { k: 'a', x: 70, y: 181, big: 2, col: BTN.pink }, { k: 'start', x: 104, y: 182, col: BTN.purple }, { k: 'coin', x: 114, y: 204 });
      F.labs.push([70, 188, 4], [104, 189, 'START'], [107, 202, 3, 'r']);
    } else {
      R(g, x0, bot + 2, 128, H - bot - 2, CP.kb);
      for (let j = 0; bot + 2 + j * 4 < H; j++) for (let i = 0; i < 32; i++) R(g, x0 + i * 4, bot + 2 + j * 4, 4, 4, (i + j) % 2 ? '#e83898' : '#181858');
      for (const wx of [0, 188]) { R(g, wx, 20, 52, 126, CP.k0); R(g, wx + 1, 21, 50, 120, CP.kd); R(g, wx + 1, 21, 50, 1, CP.kdl); R(g, wx + 1, 141, 50, 2, CP.k1); R(g, wx + 1, 143, 50, 1, '#8a1f6e'); }
      F.ctl.push({ k: 'stick', x: 26, y: 92, zone: [2, 22, 50, 140] }, { k: 'a', x: 214, y: 40, big: 2, col: BTN.pink }, { k: 'start', x: 214, y: 80, col: BTN.purple }, { k: 'coin', x: 214, y: 116 });
      F.labs.push([214, 48, 4], [214, 87, 'START'], [214, 126, 3, 'c']);
    }
    return F;
  }
  function drawBtn(g, cx, cy, big, col, down) {   // a round button seen from above at a slant: its cap, its side under it; pressed: lit, a pixel lower
    const rx = big === 2 ? 7 : big ? 5 : 4, ry = big === 2 ? 4 : big ? 3 : 2, [cap, hi, side, lit] = col;
    ellipse(g, cx, cy + 2, rx + 1, ry + 1, CP.n0); ellipse(g, cx, cy + 1, rx, ry, side);
    const y = cy + (down ? 1 : 0);
    ellipse(g, cx, y, rx, ry, down ? lit : cap); R(g, cx - rx + 2, y - ry + 1, 2, 1, hi);
  }
  function drawStick(g, cx, cy, dx, dy) {        // the joystick: its washer on the deck, its shaft leaning, its red ball
    if (!BALLC) BALLC = sprite(BALL, { r: '#e0284c', h: '#ff8aa4', d: '#8a1030' });
    ellipse(g, cx, cy + 1, 6, 2, CP.n0); ellipse(g, cx, cy, 5, 2, CP.n3); ellipse(g, cx, cy, 3, 1, CP.n0);
    const bx = cx + dx * 3, by = cy - 11 + dy * 2;
    for (let i = 0; i <= 8; i++) { const u = i / 8, x = Math.round(cx - 1 + (bx - cx) * u), y = Math.round(cy - 1 + (by + 3 - (cy - 1)) * u); R(g, x, y, 2, 1, '#2a2a52'); R(g, x, y, 1, 1, '#5a5a8a'); }
    g.drawImage(BALLC, bx - 4, by - 4);
  }
  function drawCoin(g, cx, cy, lit) {           // the lit coin slot: its plate, its slit
    R(g, cx - 3, cy - 7, 7, 14, '#3a0818'); R(g, cx - 2, cy - 6, 5, 12, lit ? '#ffd0dc' : '#ff2850'); R(g, cx - 1, cy - 5, 3, 10, lit ? '#ffffff' : '#ff7090'); R(g, cx, cy - 4, 1, 8, '#3a0818');
  }

  // ==== the dialog: a .pc window as the street's others (role dialog, modal; Esc, x, a click outside and a phone's Back close it;
  // Tab stays inside, the street's own rule for an open .pc; the page does not scroll under it). Its bar: the previous and
  // the next machine, the machine's name, the close key; the face; under it the keys (not on a touch screen: the deck is
  // the controls). The face's canvas at a whole number of device pixels per pixel (re-fitted on a resize, a zoom, a turn) ====
  const D = { el: null, open: false, cur: 0, prev: null, hist: false, raf: 0, last: 0, acc: 0, opts: null, F: null, k: 1, dpr: 1, u: 1 };
  const IN = { kb: {}, tch: {}, stick: { l: 0, r: 0, u: 0, d: 0 }, hit: {}, q: [], ptr: new Map() };   // (q: the presses in order, for the initials)
  const FL = { a: 0, b: 0, start: 0, coin: 0 };   // (a key's light, a moment after a press)
  const q = (s) => D.el.querySelector(s);
  function say(s) { if (D.el && s) q('.arc-sr').textContent = s; }
  function build() {
    if (D.el) return;
    const el = document.createElement('div'); el.className = 'pc arc'; el.setAttribute('role', 'dialog'); el.setAttribute('aria-modal', 'true'); el.setAttribute('aria-labelledby', 'arc-name');
    el.innerHTML = '<div class="arc-win"><div class="arc-bar"><button type="button" class="arc-prev"></button><span class="arc-name" id="arc-name"></span>'
      + '<button type="button" class="arc-next"></button><button type="button" class="arc-x"></button></div>'
      + '<div class="arc-face" tabindex="0" role="application"><canvas></canvas></div><p class="arc-help"></p><p class="arc-sr" aria-live="polite"></p></div>';
    document.body.appendChild(el); D.el = el;
    D.cv = q('.arc-face canvas'); D.g = D.cv.getContext('2d');
    [D.art, D.ag] = canvas(8, 8);              // (the face at 1:1, then brought up k times into the shown canvas)
    q('.arc-x').addEventListener('click', () => close());
    q('.arc-prev').addEventListener('click', () => select((D.cur + 3) % 4));
    q('.arc-next').addEventListener('click', () => select((D.cur + 1) % 4));
    el.addEventListener('click', (ev) => { if (ev.target === el) close(); });
    el.addEventListener('touchmove', (ev) => { if (ev.cancelable) ev.preventDefault(); }, { passive: false });   // (the page under it stays put)
    el.addEventListener('wheel', (ev) => ev.preventDefault(), { passive: false });
    const fc = q('.arc-face');
    fc.addEventListener('pointerdown', ptrDown); fc.addEventListener('pointermove', ptrMove);
    fc.addEventListener('pointerup', ptrUp); fc.addEventListener('pointercancel', ptrUp); fc.addEventListener('lostpointercapture', ptrUp);
    fc.addEventListener('contextmenu', (ev) => ev.preventDefault());
    document.addEventListener('keydown', onKey, true); document.addEventListener('keyup', onKeyUp, true);
    window.addEventListener('blur', () => { IN.kb = {}; });
    window.addEventListener('resize', () => { if (D.open) fit(); });
    window.addEventListener('popstate', () => { if (D.open) { D.hist = false; close(true); } });
    document.addEventListener('visibilitychange', () => {
      if (!D.open) return;
      if (document.hidden) { const S = machine(D.cur); if (S.ph === 'play') S.paused = true; cancelAnimationFrame(D.raf); D.raf = 0; }
      else run();
    });
    new MutationObserver(() => { if (D.open) labels(); }).observe(document.documentElement, { attributes: true, attributeFilter: ['lang'] });
  }
  function labels() {
    const t = T(), S = machine(D.cur);
    q('.arc-name').textContent = (D.cur + 1) + '/4 · ' + S.G.title;   // (the machine's own name in the face's label)
    q('.arc-x').setAttribute('aria-label', t.close); q('.arc-prev').setAttribute('aria-label', t.prev); q('.arc-next').setAttribute('aria-label', t.next);
    q('.arc-face').setAttribute('aria-label', t.face(t.mach[D.cur], S.G.title));
    q('.arc-help').textContent = t.help; q('.arc-help').hidden = coarse;
  }
  function fit() {                              // the largest whole number of device pixels per pixel that fits (4 CSS px at most);
    const S = machine(D.cur), look = S.M.face, dpr = window.devicePixelRatio || 1;   // the tall face unless it would fall
    const vw = document.documentElement.clientWidth || window.innerWidth, vh = window.innerHeight;   // under 2 CSS px a pixel
    const avW = vw - 16, avH = vh - 50 - (coarse ? 0 : 34) - 20;                      // and the wide one does better
    const kOf = (F) => Math.max(1, Math.min(Math.floor(4 * dpr + 1e-6), Math.floor(Math.min(avW * dpr / F.W, avH * dpr / F.H) + 1e-6)));
    const ft = face(look, false), fw = face(look, true), kt = kOf(ft), kw = kOf(fw), wide = kt / dpr < 2 - 1e-6 && kw > kt;
    const F = wide ? fw : ft, k = wide ? kw : kt;
    D.F = F; D.k = k; D.dpr = dpr; D.u = k / dpr;
    // the shown canvas holds the face's device pixels themselves (k of them a pixel, scaled here, nearest), and a few clear
    // ones more on the right and at the bottom where needed: its CSS size must be exact in the browser's layout units
    // (1/64 px), or the browser resamples it, a column doubled or dropped (1064 device px at a DPR of 3: 354.67 CSS px);
    // padded to the next size that is (1065: 355 px), it is drawn as it is at any zoom and DPR
    if (D.art.width !== F.W || D.art.height !== F.H) { D.art.width = F.W; D.art.height = F.H; D.ag = D.art.getContext('2d'); }
    D.ag.imageSmoothingEnabled = false;
    const ok = (m) => { const v = m / dpr * 64; return Math.abs(v - Math.round(v)) < 1e-3; };   // (m device px: exact in 1/64 CSS px)
    const exact = (n) => { for (let m = n; m < n + 96; m++) if (ok(m)) return m; return n; };
    const w = exact(F.W * k), h = exact(F.H * k);
    if (D.cv.width !== w || D.cv.height !== h) { D.cv.width = w; D.cv.height = h; D.g = D.cv.getContext('2d'); }
    D.g.imageSmoothingEnabled = false;
    D.cv.style.width = (w / dpr) + 'px'; D.cv.style.height = (h / dpr) + 'px';
    // and its corner on a whole device pixel: the window placed here, not centred by the layout (a centred window lands on
    // half a pixel as often as not), the bar's height and the face's margin in the window whole numbers of device pixels;
    // each a length the layout's 1/64 px holds exactly too (at a DPR of 3: a whole CSS px)
    const dev = (v) => { const m0 = Math.round(v * dpr); for (let i = 0; i < 24; i++) for (const m of [m0 - i, m0 + i]) if ((m > 0 || m0 <= 0) && ok(m)) return m / dpr; return m0 / dpr; };
    const win = q('.arc-win'), fw0 = w / dpr, ww = Math.max(fw0, dev(Math.min(vw - 16, 280)));
    win.classList.toggle('wide', wide);
    win.style.width = ww + 'px'; q('.arc-bar').style.height = dev(46) + 'px';
    q('.arc-face').style.marginLeft = dev((ww - fw0) / 2) + 'px';
    win.style.left = dev((vw - ww) / 2) + 'px';
    win.style.top = Math.max(0, dev((vh - win.offsetHeight) / 2)) + 'px';
  }
  function faceDraw() {
    const S = machine(D.cur), F = D.F, g = D.ag, t = T();
    g.drawImage(F.chrome, 0, 0);
    g.drawImage(S.cv, F.scr[0], F.scr[1]);
    const H = held(), lab = (x, y, s, al) => text(g, s, x, y, S.M.face === 'claw' ? '#c088d8' : CP.lab, 1, al === undefined ? 'c' : al);
    for (const C of F.ctl) {
      if (C.k === 'stick') drawStick(g, C.x, C.y, (H.r ? 1 : 0) - (H.l ? 1 : 0), (H.d ? 1 : 0) - (H.u ? 1 : 0));
      else if (C.k === 'coin') drawCoin(g, C.x, C.y, FL.coin > 0);
      else drawBtn(g, C.x, C.y, C.big, C.col, !!(H[C.k] || FL[C.k] > 0));
    }
    for (const [x, y, s, al] of F.labs) lab(x, y, typeof s === 'number' ? t.helpK[s] : s, al);
    D.g.drawImage(D.art, 0, 0, F.W * D.k, F.H * D.k);
  }
  // ---- the inputs: the keyboard (arrows or WASD, by the keys' places: ZQSD on a French keyboard), space Z X, enter or 5, P;
  // the face's controls under a finger or a mouse (the joystick follows the finger from where it went down; a button held
  // while pressed). A press is kept until a game step has seen it ----
  const KEYC = { ArrowLeft: 'l', KeyA: 'l', ArrowRight: 'r', KeyD: 'r', ArrowUp: 'u', KeyW: 'u', ArrowDown: 'd', KeyS: 'd', Space: 'a', KeyZ: 'a', KeyX: 'b',
    Enter: 'enter', NumpadEnter: 'enter', Digit5: 'coin', Numpad5: 'coin', KeyP: 'pause', Backspace: 'back' };
  const KEYK = { ArrowLeft: 'l', ArrowRight: 'r', ArrowUp: 'u', ArrowDown: 'd', ' ': 'a', Enter: 'enter', 5: 'coin', p: 'pause', P: 'pause', Backspace: 'back' };
  function onKey(ev) {
    if (!D.open || ev.altKey || ev.ctrlKey || ev.metaKey) return;
    if (ev.key === 'Escape') { close(); ev.preventDefault(); ev.stopPropagation(); return; }
    if (ev.key === 'Tab') { D.el.classList.add('kbd'); return; }
    const ae = document.activeElement;
    if (ae && ae.tagName === 'BUTTON' && D.el.contains(ae) && (ev.key === 'Enter' || ev.key === ' ')) return;   // (a key of the bar: its own press)
    const S = machine(D.cur);
    if (S.ph === 'enter' && ev.key && ev.key.length === 1 && /[a-z]/i.test(ev.key)) { IN.q.push(ev.key.toUpperCase()); ev.preventDefault(); ev.stopPropagation(); return; }
    const k = KEYC[ev.code] || KEYK[ev.key];
    if (!k) return;
    ev.preventDefault(); ev.stopPropagation();
    if (!ev.repeat) { IN.hit[k] = 1; IN.q.push(k); if (k === 'enter') FL[S.ph === 'attract' && S.credits > 0 ? 'start' : 'coin'] = 0.2; if (k === 'coin') FL.coin = 0.2; }
    if ('lrudab'.includes(k)) IN.kb[k] = 1;
  }
  function onKeyUp(ev) { if (!D.open) return; const k = KEYC[ev.code] || KEYK[ev.key]; if (k && 'lrudab'.includes(k)) IN.kb[k] = 0; }
  function held() {
    const h = {};
    for (const k of ['l', 'r', 'u', 'd', 'a', 'b']) h[k] = !!(IN.kb[k] || IN.tch[k] > 0 || IN.stick[k]);
    return h;
  }
  function artAt(ev) { const r = D.cv.getBoundingClientRect(); return [(ev.clientX - r.left) / D.u, (ev.clientY - r.top) / D.u]; }
  function ctlAt(ev) {                          // the control under a pointer: its box grown to 44 CSS px; of two, the nearest
    const [x, y] = artAt(ev), m = 22 / D.u; let best = null, bd = 1e9;
    for (const C of D.F.ctl) {
      const [x0, y0, x1, y1] = C.zone || [C.x - 6, C.y - 5, C.x + 6, C.y + 5];
      const gx = Math.max(0, m - (x1 - x0) / 2), gy = Math.max(0, m - (y1 - y0) / 2);
      if (x < x0 - gx || x > x1 + gx || y < y0 - gy || y > y1 + gy) continue;
      const d = Math.hypot(x - (x0 + x1) / 2, y - (y0 + y1) / 2); if (d < bd) { bd = d; best = C; }
    }
    return best;
  }
  function ptrDown(ev) {
    const fc = q('.arc-face'); D.el.classList.remove('kbd');
    try { fc.focus({ preventScroll: true }); } catch (e) {}
    const C = ctlAt(ev); if (!C) return;
    ev.preventDefault();
    try { fc.setPointerCapture(ev.pointerId); } catch (e) {}
    IN.ptr.set(ev.pointerId, C.k === 'stick' ? { k: 'stick', x0: ev.clientX, y0: ev.clientY } : { k: C.k });
    if (C.k === 'stick') stickTo(ev, IN.ptr.get(ev.pointerId));
    else { IN.hit[C.k] = 1; IN.q.push(C.k); FL[C.k] = 0.2; if ('ab'.includes(C.k)) IN.tch[C.k] = (IN.tch[C.k] || 0) + 1; }
  }
  function ptrMove(ev) { const P = IN.ptr.get(ev.pointerId); if (P && P.k === 'stick') stickTo(ev, P); }
  function ptrUp(ev) {
    const P = IN.ptr.get(ev.pointerId); if (!P) return;
    IN.ptr.delete(ev.pointerId);
    if (P.k === 'stick') IN.stick = { l: 0, r: 0, u: 0, d: 0 }; else if ('ab'.includes(P.k)) IN.tch[P.k] = Math.max(0, (IN.tch[P.k] || 1) - 1);
  }
  function stickTo(ev, P) {                     // the joystick: the finger's way from where it went down (and from the ball, for a tap
    const C = D.F.ctl.find((c) => c.k === 'stick'), r = D.cv.getBoundingClientRect();   // on its side), eight ways, 9 CSS px of play
    const bx = r.left + C.x * D.u, by = r.top + (C.y - 11) * D.u;
    const dx = ev.clientX - (P.moved ? P.x0 : bx), dy = ev.clientY - (P.moved ? P.y0 : by);
    if (Math.hypot(ev.clientX - P.x0, ev.clientY - P.y0) > 12) P.moved = true;
    const dz = 9, ax = Math.abs(dx), ay = Math.abs(dy), old = IN.stick;
    const s = { l: dx < -dz && ax > ay * 0.4 ? 1 : 0, r: dx > dz && ax > ay * 0.4 ? 1 : 0, u: dy < -dz && ay > ax * 0.4 ? 1 : 0, d: dy > dz && ay > ax * 0.4 ? 1 : 0 };
    for (const k in s) if (s[k] && !old[k]) { IN.hit[k] = 1; IN.q.push(k); }
    IN.stick = s;
  }
  function input() { return { held: held(), hit: IN.hit, q: IN.q }; }
  // ---- the loop: fixed steps of 1/60 s, drawn once a frame; only while the dialog is open and the tab shown ----
  function run() { if (!D.raf && D.open && !document.hidden) { D.last = 0; D.raf = requestAnimationFrame(loop); } }
  function loop(ts) {
    D.raf = 0;
    if (!D.open || document.hidden) return;
    const dt = D.last ? Math.min(0.25, (ts - D.last) / 1000) : STEP; D.last = ts;
    const S = machine(D.cur);
    D.acc += dt; let n = 0;
    while (D.acc >= STEP && n < 12) { shStep(S, STEP, input()); IN.hit = {}; IN.q = []; D.acc -= STEP; n++; }
    if (n >= 12) D.acc = 0;
    for (const k in FL) FL[k] = Math.max(0, FL[k] - dt);
    shDraw(S); faceDraw();
    D.raf = requestAnimationFrame(loop);
  }
  function select(i) {
    const P = machine(D.cur); if (P.ph === 'play') P.paused = true;
    D.cur = i; IN.hit = {}; IN.q = []; IN.kb = {}; IN.tch = {}; IN.stick = { l: 0, r: 0, u: 0, d: 0 }; IN.ptr.clear();
    labels(); fit();
    const S = machine(i); shDraw(S); faceDraw();
    if (D.opts && D.opts.onPlay) try { D.opts.onPlay(i); } catch (e) {}
  }
  function open(i, opts) {
    build();
    D.opts = opts || {};
    D.el.classList.toggle('kbd', !!D.opts.kb);   // (the focus ring for the keyboard only: no ring on a key nobody chose)
    if (!D.open) {
      D.prev = document.activeElement; D.open = true; D.el.classList.add('on');
      if (!D.hist) try { history.pushState({ arcade: 1 }, ''); D.hist = true; } catch (e) {}   // (a phone's Back: closes it)
    }
    select(i);
    try { q('.arc-face').focus({ preventScroll: true }); } catch (e) {}
    run();
  }
  function close(back) {
    if (!D.open) return;
    const S = machine(D.cur); if (S.ph === 'play') S.paused = true;
    D.open = false; D.el.classList.remove('on'); cancelAnimationFrame(D.raf); D.raf = 0;
    IN.kb = {}; IN.tch = {}; IN.stick = { l: 0, r: 0, u: 0, d: 0 }; IN.ptr.clear(); IN.hit = {};
    if (D.hist) { D.hist = false; if (back !== true) try { history.back(); } catch (e) {} }
    if (D.opts && D.opts.onPlay) try { D.opts.onPlay(-1); } catch (e) {}
    const p = D.prev; if (p && p.focus && p !== document.body && document.contains(p)) try { p.focus({ preventScroll: true }); } catch (e) {}
  }
  // (for the street, and for a test: the dialog, its state)
  window.ARCADE = { open, close, isOpen: () => D.open, get cur() { return D.cur; }, machine,
    frame: () => D.art.toDataURL(),
    controls: () => { const r = D.cv.getBoundingClientRect(); return D.F.ctl.map((C) => ({ k: C.k, cx: r.left + C.x * D.u, cy: r.top + (C.k === 'stick' ? C.y - 11 : C.y) * D.u })); } };
  // the styles (street.js loads them with the script and opens the dialog once both are in; this script alone adds them itself)
  if (!document.querySelector('link[data-arcade]')) {
    const l = document.createElement('link'); l.rel = 'stylesheet'; l.href = 'assets/arcade.css?v=1'; l.dataset.arcade = '1'; document.head.appendChild(l);
  }
})();
