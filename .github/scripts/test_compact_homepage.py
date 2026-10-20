#!/usr/bin/env python3
"""Regression: the actual LOUD build must retain the published compact homepage CSS.

Run with python3 .github/scripts/test_compact_homepage.py. Builds a minimal
temporary site twice; never writes to the checkout or releases Passages.
"""
from pathlib import Path
import hashlib
import shutil
import subprocess
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[2]
MARKER = "/* COMPACT PASS 2026-10-18"


def compact_css(text):
    assert text.count(MARKER) == 1, "Compact homepage rules must occur exactly once"
    return text[text.index(MARKER):text.index("</style>", text.index(MARKER))]


def main():
    published = (ROOT / "index.html").read_text(encoding="utf-8")
    expected = compact_css(published)
    with tempfile.TemporaryDirectory(prefix="ghostheart-compact-test-") as directory:
        fixture = Path(directory)
        for name in (
            ".github/scripts/apply_loud_design.py",
            ".github/scripts/build_passages.py",
            ".github/loud-pages/index.html.loud",
            ".github/loud-sources/index.html.src",
            "index.html",
            "passages/index.html",
            "sitemap.xml",
        ):
            target = fixture / name
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(ROOT / name, target)
        # No Passage content is copied: this fixture only exercises homepage rendering.
        previous = None
        for run in (1, 2):
            subprocess.run(
                [sys.executable, "-X", "utf8", str(fixture / ".github/scripts/apply_loud_design.py")],
                check=True, capture_output=True, text=True, encoding="utf-8",
            )
            rebuilt = (fixture / "index.html").read_text(encoding="utf-8")
            assert compact_css(rebuilt) == expected, f"Rebuild {run} lost or changed compact CSS"
            assert 'https://www.youtube.com/watch?v=RtFTIssLd0s' in rebuilt
            assert "FEATURED NOW" in rebuilt
            if previous is not None:
                assert rebuilt == previous, "Second LOUD build changed homepage output"
            previous = rebuilt
    print("PASS: two actual LOUD rebuilds preserve compact homepage CSS and featured preview")
    print("Compact CSS SHA256:", hashlib.sha256(expected.encode()).hexdigest())


if __name__ == "__main__":
    main()
