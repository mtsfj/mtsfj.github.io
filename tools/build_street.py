#!/usr/bin/env python3
"""assets/street.min.js from assets/street.js: what the home loads (index.html), the same program in fewer bytes.

    python3 tools/build_street.py           writes assets/street.min.js (then: its ?v= in index.html, in the script that loads it)
    python3 tools/build_street.py --check   only says whether assets/street.min.js is street.js's build (exit 1 if not)

street.js stays the source: edit it, never the .min.js, and rebuild after each change. esbuild, at a fixed version (ESBUILD), through
npx (Node and npm needed; the first run fetches it): the comments and the spaces out, the local names shortened, nothing else; the
same input gives the same bytes. The build is checked by Node (node --check) and its sizes printed (raw, gzip as GitHub Pages sends
it); a debug page loads street.js itself. Both forms also check that index.html asks for the
street's biggest layer (with the scripts) at the very address street.js loads it from (ASSETS.city: a ?v= changed in one and not the
other would download it twice).
"""
import argparse, gzip, os, re, subprocess, sys, tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, 'assets', 'street.js')
OUT = os.path.join(ROOT, 'assets', 'street.min.js')
INDEX = os.path.join(ROOT, 'index.html')
ESBUILD = 'esbuild@0.21.5'


def build(out):
    subprocess.run(['npx', '--yes', ESBUILD, SRC, '--minify', '--charset=utf8', '--legal-comments=none', '--log-level=warning', '--outfile=' + out], check=True, cwd=ROOT)
    subprocess.run(['node', '--check', out], check=True)
    return open(out, 'rb').read()


def city_ok():
    city = re.search(r'"city": "([^"]+)"', open(SRC, encoding='utf-8').read())
    asked = re.search(r"var c = '([^']+)'", open(INDEX, encoding='utf-8').read())
    if city and asked and city.group(1) == asked.group(1):
        return True
    print('index.html asks for', asked and asked.group(1), 'but street.js loads', city and city.group(1), '(the same address in both)')
    return False


def main():
    ap = argparse.ArgumentParser(description='street.min.js depuis street.js (voir la docstring)')
    ap.add_argument('--check', action='store_true', help="compare seulement, n'écrit rien")
    a = ap.parse_args()
    if a.check:
        with tempfile.TemporaryDirectory() as tmp:
            b = build(os.path.join(tmp, 'street.min.js'))
        same = os.path.exists(OUT) and open(OUT, 'rb').read() == b
        print('street.min.js is street.js\'s build' if same else 'street.min.js is NOT street.js\'s build: python3 tools/build_street.py')
        sys.exit(0 if same and city_ok() else 1)
    b = build(OUT)
    src = open(SRC, 'rb').read()
    kb = lambda n: f'{n / 1024:.0f} KB'
    print(f'street.js {kb(len(src))} (gzip {kb(len(gzip.compress(src, 9)))}) -> street.min.js {kb(len(b))} (gzip {kb(len(gzip.compress(b, 9)))})')
    if not city_ok():
        sys.exit(1)


if __name__ == '__main__':
    main()
