#!/usr/bin/env python3
"""Checks for apply_google_analytics.py (runs in website-checks)."""
import importlib.util
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
spec = importlib.util.spec_from_file_location('ga', ROOT / '.github/scripts/apply_google_analytics.py')
ga = importlib.util.module_from_spec(spec)
spec.loader.exec_module(ga)

PAGE = ('<html><head><meta charset="utf-8"><meta http-equiv="Content-Security-Policy" content="default-src \'self\'; '
        'script-src \'self\' https://tracker.metricool.com; connect-src \'self\' https://tracker.metricool.com"></head>'
        '<body><h2>Website visit analytics</h2>\n<p>Metricool.</p>\n<h2>Next</h2></body></html>')

out = ga.apply(PAGE, 'G-TEST1234', privacy=True)
assert out.count('id="ghostheart-ga-loader"') == 1
assert 'src="/assets/shared/ghostheart-ga.js" data-ga-id="G-TEST1234"' in out
js = (ROOT / 'assets/shared/ghostheart-ga.js').read_text(encoding='utf-8')
assert "['www.myghostheart.com', 'myghostheart.com'].includes(location.hostname)" in js, 'public domain only'
assert 'script-src \'self\' https://tracker.metricool.com https://www.googletagmanager.com' in out
assert 'https://*.google-analytics.com' in out and 'https://*.analytics.google.com' in out
assert out.index('<h2>Google Analytics</h2>') > out.index('<p>Metricool.</p>')
assert ga.apply(out, 'G-TEST1234', privacy=True) == out, 'running twice changes nothing'
assert ga.apply(PAGE, 'G-TEST1234') .count('<h2>Google Analytics</h2>') == 0, 'privacy text only on the privacy page'

mid = ga.measurement_id()
built = [p for p in ROOT.rglob('*.html') if 'ghostheart-ga-loader' in p.read_text(encoding='utf-8', errors='ignore')
         and not p.relative_to(ROOT).as_posix().startswith(('.github/', 'node_modules/'))]
if mid:
    assert built, 'measurement ID set but no page has the loader: run build_site.py'
    assert '<h2>Google Analytics</h2>' in (ROOT / 'GhostHeart_Privacy.html').read_text(encoding='utf-8')
else:
    assert not built, 'no measurement ID, so no page may carry Google Analytics'
print('Google Analytics checks passed' + (f' ({mid})' if mid else ' (no ID yet, nothing added)'))
