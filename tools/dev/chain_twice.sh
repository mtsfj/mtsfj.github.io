#!/bin/bash
# The street's whole build chain, run twice, its outputs' md5 compared: prints SAME when the second run writes the same
# bytes as the first (the chain is at its fixpoint and deterministic). Run from the repository root:
#     bash tools/dev/chain_twice.sh            (after a merge, run it again until it prints SAME: the first run may still
#                                               be converging, a zone's before copies feeding the next)
# Each run keeps its md5 lists in its own temporary directory (several agents may run this at once).
set -u
T=$(mktemp -d)
chain() {
  python3 tools/kirua_bay_window.py >/dev/null &&
  (cd tools && python3 redraw_zones.py >/dev/null) &&
  python3 tools/bake_retouches.py >/dev/null &&
  python3 tools/ichiraku_figures.py >/dev/null &&
  python3 tools/ichiraku_luffy.py >/dev/null &&
  python3 tools/naruto_col.py >/dev/null &&
  python3 tools/killua_seat.py >/dev/null &&
  python3 tools/center_red.py >/dev/null &&
  python3 tools/build_street.py >/dev/null
}
sums() { md5sum assets/*.webp assets/street.min.js tools/src/retouches/*.webp > "$1"; }
chain && sums "$T/m1" && chain && sums "$T/m2" || { echo "FAILED (a step of the chain stopped)"; exit 2; }
if cmp -s "$T/m1" "$T/m2"; then echo SAME; rm -rf "$T"; else echo "DIFFERENT (run again; if it never settles, a tool is not deterministic):"; diff "$T/m1" "$T/m2" | head; exit 1; fi
git status --short | grep -v '^[ADMR] ' | head -20
