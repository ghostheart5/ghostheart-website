#!/usr/bin/env python3
"""Verify exact approved public text, honest release date, and no future release."""
from pathlib import Path
from datetime import datetime
import hashlib
import os
import re
import shutil
import subprocess
import sys
import tempfile
from bs4 import BeautifulSoup

ROOT = Path(__file__).resolve().parents[2]


def released(route: Path, reading: str) -> bool:
    """A ready Passage gets an early 'opens at' page before its time: that holds no reading text."""
    if not route.exists():
        return False
    html = route.read_text(encoding="utf-8")
    if 'class="r-body r-wait"' in html:
        assert reading not in html, f"{route.name} leaks its reading before release"
        return False
    return True
TITLE = "I’m Not — More Than One Chapter"
BODY_SHA = "9427fc3d8dad30dab6839a7ae6ccca00bc98d4d8669025cc50b6d677e8b8b6d1"


def main():
    source = (ROOT / ".github/content/passages/02-im-not.md").read_text(encoding="utf-8")
    header, body = source.split("---", 2)[1:]
    body = body.strip()
    assert hashlib.sha256(body.encode()).hexdigest() == BODY_SHA
    assert f"title: {TITLE}\n" in header
    assert "date: 2026-10-19T02:25:44-05:00\n" in header
    expected = [" ".join(line.removeprefix("> ").strip() for line in p.splitlines()) for p in re.split(r"\n\s*\n", body)]
    future = (ROOT / ".github/content/passages/03-its-not-the-1950s.md").read_text(encoding="utf-8").split("---", 2)[1]
    future_meta = dict(line.split(":", 1) for line in future.splitlines() if ":" in line)
    with tempfile.TemporaryDirectory(prefix="ghostheart-im-not-test-") as directory:
        fixture = Path(directory)
        for name in [".github/scripts/build_passages.py", "passages/index.html", "sitemap.xml"]:
            target = fixture / name
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(ROOT / name, target)
        shutil.copytree(ROOT / ".github/content/passages", fixture / ".github/content/passages")
        for instant, opened in [("2026-10-19T07:25:43Z", False), ("2026-10-19T07:25:44Z", True),
                                ("2026-10-24T23:59:59Z", True), ("2026-10-25T00:00:00Z", True),
                                ("2026-10-19T07:25:43Z", False)]:
            subprocess.run([sys.executable, "-X", "utf8", str(fixture / ".github/scripts/build_passages.py")],
                           env=dict(os.environ, PASSAGES_BUILD_NOW=instant), check=True, capture_output=True)
            route = fixture / "passages/im-not.html"
            assert released(route, expected[0]) == opened
            index = BeautifulSoup((fixture / "passages/index.html").read_text(encoding="utf-8"), "html.parser")
            assert (index.select_one("#p02 a[href='/passages/im-not.html']") is not None) == opened
            assert ("/passages/im-not.html" in (fixture / "sitemap.xml").read_text()) == opened
            future_open = (future_meta["status"].strip() == "ready" and
                           datetime.fromisoformat(instant.replace("Z", "+00:00")) >= datetime.fromisoformat(future_meta["date"].strip()))
            assert (index.select_one("#p03 a[href='/passages/its-not-the-1950s.html']") is not None) == future_open
            future_body = (ROOT / ".github/content/passages/03-its-not-the-1950s.md").read_text(encoding="utf-8").split("---", 2)[2].strip()
            assert released(fixture / "passages/its-not-the-1950s.html", future_body.split("\n\n")[0].strip()) == future_open
            if opened:
                page = BeautifulSoup(route.read_text(encoding="utf-8"), "html.parser")
                assert page.select_one("h1").get_text() == TITLE
                assert [p.get_text() for p in page.select(".r-body p")] == expected
                assert "Source and review handoff" not in page.get_text()
                assert "Released Oct 19, 2026" in page.select_one(".kicker").get_text()
                assert "7 PM" not in page.select_one(".kicker").get_text()
            print(f"PASS {instant}: approved I'm Not {'open' if opened else 'locked'}; 1950s {'open at gate' if future_open else 'unpublished'}")


if __name__ == "__main__":
    main()
