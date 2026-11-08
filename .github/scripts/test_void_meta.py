#!/usr/bin/env python3
"""Checks for apply_void_meta.py (stray </meta> fix, Nov 8, 2026)."""
from pathlib import Path
import importlib.util, sys

spec = importlib.util.spec_from_file_location('void_meta', Path(__file__).with_name('apply_void_meta.py'))
mod = importlib.util.module_from_spec(spec)
mod.main = lambda: 0  # load the helpers only, don't touch the site
src = Path(spec.origin).read_text(encoding='utf-8').replace('\nmain()\n', '\n')
exec(compile(src, spec.origin, 'exec'), mod.__dict__)

broken = ('<html><head><meta charset="utf-8"/><meta name="referrer" content="x"><meta content="a>b" name="d">'
          '<title>T</title><script>var s="<meta name=q>";</script></meta></meta></head><body><p>hi</p></body></html>')
fixed = mod.fix(broken)
assert '</meta>' not in fixed, fixed
assert '<meta name="referrer" content="x"/>' in fixed, fixed
assert '<meta content="a>b" name="d"/>' in fixed, fixed
assert '<meta charset="utf-8"/>' in fixed and '<meta charset="utf-8"//>' not in fixed, fixed
assert 'var s="<meta name=q>";' in fixed, 'head script must be left alone'
assert mod.fix(fixed) == fixed, 'not safe to run twice'
body = '<html><head><title>T</title></head><body><script>x="<meta a>";</script></body></html>'
assert mod.fix(body) == body, 'body must be left alone'

from bs4 import BeautifulSoup
reparsed = str(BeautifulSoup(fixed, 'html.parser'))
assert '</meta>' not in reparsed, reparsed
print('PASS void meta: head <meta> self-closing, stray </meta> removed, body untouched, re-parse clean')
