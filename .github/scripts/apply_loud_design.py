#!/usr/bin/env python3
"""Apply the LOUD redesign (October 14, 2026) as the final build step.

Page sources live in .github/loud-pages as *.html.loud (so the validator does
not treat them as published pages). They are copied over the generated
routes. Where a source contains an inject marker, the approved content block
(films, Vault items, resources) is taken from the page this build just
generated, so the redesign restyles that content instead of rewriting it:

  <!--@inject CSS-SELECTOR-->      first match, outer HTML
  <!--@inject-all CSS-SELECTOR-->  every match, outer HTML
"""
from pathlib import Path
import re
import shutil

from bs4 import BeautifulSoup

ROOT = Path(__file__).resolve().parents[2]
PAGES = ROOT / ".github/loud-pages"
SOURCES = ROOT / ".github/loud-sources"
STAMP = '<meta name="generator" content="GhostHeart LOUD redesign">'
MARKER = re.compile(r"<!--@(inject|inject-all|inject-from) (.+?)-->")


VOID = {"area","base","br","col","embed","hr","img","input","link","meta","source","track","wbr"}


def raw_outer(text: str, node) -> str:
    """Return the element exactly as written in the generated file (attribute order kept)."""
    lines = text.split("\n")
    start = sum(len(line) + 1 for line in lines[: node.sourceline - 1]) + node.sourcepos
    if node.name in VOID:
        return text[start : text.index(">", start) + 1]
    tag = re.compile(r"<(/?)%s\b[^>]*>" % re.escape(node.name), re.I)
    depth = 0
    for match in tag.finditer(text, start):
        if match.group(0).endswith("/>"):
            continue
        depth += -1 if match.group(1) else 1
        if depth == 0:
            return text[start : match.end()]
    raise SystemExit(f"LOUD inject: unbalanced <{node.name}>")


def approved_source(relative: Path, target: Path) -> str:
    """The page as the approved pipeline generated it, before the redesign.

    Routes the pipeline regenerates are read fresh (and the snapshot refreshed);
    routes it leaves alone still hold the redesign, so the stored snapshot is used.
    """
    snapshot = SOURCES / (str(relative) + ".src")
    current = target.read_text(encoding="utf-8") if target.exists() else ""
    if current and "GhostHeart LOUD redesign" not in current:
        snapshot.parent.mkdir(parents=True, exist_ok=True)
        snapshot.write_text(current, encoding="utf-8")
        return current
    if snapshot.exists():
        return snapshot.read_text(encoding="utf-8")
    raise SystemExit(f"LOUD inject: no approved source for {relative}")


def render(source: Path, target: Path, relative: Path) -> str:
    text = source.read_text(encoding="utf-8").replace("<head>", "<head>\n" + STAMP, 1)
    assert STAMP in text, relative
    if not MARKER.search(text):
        return text
    needs_own = any(m.group(1) != "inject-from" for m in MARKER.finditer(text))
    raw = approved_source(relative, target) if needs_own else ""
    generated = BeautifulSoup(raw, "html.parser")

    def replace(match: re.Match) -> str:
        kind, selector = match.group(1), match.group(2).strip()
        if kind == "inject-from":
            other, selector = selector.split(" ", 1)
            other_raw = approved_source(Path(other), ROOT / other)
            node = BeautifulSoup(other_raw, "html.parser").select_one(selector)
            if node is None:
                raise SystemExit(f"LOUD inject: {selector!r} not found in {other}")
            return raw_outer(other_raw, node)
        found = generated.select(selector)
        if not found:
            raise SystemExit(f"LOUD inject: {selector!r} not found for {relative}")
        nodes = found if kind == "inject-all" else found[:1]
        return "\n".join(raw_outer(raw, node) for node in nodes)

    return MARKER.sub(replace, text)


count = 0
for source in sorted(PAGES.rglob("*.html.loud")):
    relative = Path(str(source.relative_to(PAGES)).removesuffix(".loud"))
    target = ROOT / relative
    target.parent.mkdir(parents=True, exist_ok=True)
    output = render(source, target, relative)
    target.write_text(output, encoding="utf-8")
    count += 1

print("Applied LOUD redesign pages:", count)

# Passages list and reading pages come from .github/content/passages (see build_passages.py).
import runpy
runpy.run_path(str(ROOT / ".github/scripts/build_passages.py"), run_name="__main__")

# LOUD skin (owner request October 14, 2026): restyle these approved pages in place,
# keeping their content and layout exactly as generated.
# Every other published page (owner: "finish everything"), except redirect stubs
# and pages that already carry the full LOUD redesign.
SKIN_ROUTES = sorted(
    str(path.relative_to(ROOT)).replace("\\", "/")
    for path in ROOT.rglob("*.html")
    if ".github" not in path.parts and "node_modules" not in path.parts
    and 'http-equiv="refresh"' not in (text := path.read_text(encoding="utf-8"))
    and "GhostHeart LOUD redesign" not in text
)
SKIN_HEAD = (
    '<link rel="preconnect" href="https://fonts.googleapis.com">'
    '<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>'
    '<link href="https://fonts.googleapis.com/css2?family=Anton&family=Space+Grotesk:wght@400;500;700&display=swap" rel="stylesheet">'
    '<link rel="stylesheet" href="/assets/loud/loud-skin.css">'
)
skinned = 0
for route in SKIN_ROUTES:
    page = ROOT / route
    value = page.read_text(encoding="utf-8")
    if "/assets/loud/loud-skin.css" not in value:
        value = value.replace("</head>", SKIN_HEAD + "</head>", 1)
        if re.search(r"<body\b[^>]*\bclass=\"", value):
            value = re.sub(r'(<body\b[^>]*\bclass=")([^"]*)"', lambda m: '%s%s loud-skin"' % (m.group(1), m.group(2)), value, count=1)
        else:
            value = re.sub(r"<body\b", '<body class="loud-skin"', value, count=1)
        assert re.search(r'<body\b[^>]*loud-skin', value), route
        page.write_text(value, encoding="utf-8")
    skinned += 1
print("Applied LOUD skin pages:", skinned)
