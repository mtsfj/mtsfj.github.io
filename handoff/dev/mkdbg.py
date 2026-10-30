# builds _dbg_street.js / _dbg.html from the live sources: internals exposed (window.__S), a time warp (window.__warp, __dtMax)
import re
s = open('assets/street.js', encoding='utf-8').read()
s = s.replace("const dt = Math.min(clock.getDelta(), 0.05); t += dt;", "const dt = window.__dtHook ? window.__dtHook(clock.getDelta()) : Math.min(clock.getDelta(), 0.05); t += dt; window.__t = t;")
names = ['ws', 'HRS', 'TREE', 'powerCut', 'IRNR', 'IRL', 'SHOP', 'shopOff', 'IR', 'PW_ZONES', 'comps', 'skyDim', 'fogs', 'farQuad', 'farMat', 'city', 'fujiNight', 'fujiTree', 'fujiFront', 'towerMesh', 'pwShade', 'sky', 'NRU', 'FIN', 'FINS', 'PW', 'CLOCK', 'SKYF', 'REDN', 'finStart', 'finDawn', 'finClear', 'setTimeOverride', 'frame', 'scene', 'camera', 'renderer', 'view', 'WET', 'NIGHT', 'HRS', 'OPEN', 'PAN']
expose = "  try { window.__S = {" + ", ".join(f"get {n}() {{ try {{ return {n}; }} catch (e) {{ return undefined; }} }}" for n in names) + "}; } catch (e) {}\n"
tail = "  frame();\n  if (reduced) setTimeout(frame, 800);"
assert s.count(tail) == 1
s = s.replace(tail, expose + tail)
open('_dbg_street.js', 'w', encoding='utf-8').write(s)
h = re.sub(r'assets/street\.js\?v=\d+', '_dbg_street.js', open('index.html', encoding='utf-8').read())
open('_dbg.html', 'w', encoding='utf-8').write(h)
print('ok')
