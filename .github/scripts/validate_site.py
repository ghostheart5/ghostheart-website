#!/usr/bin/env python3
"""Validate the exact static tree proposed for GitHub Pages."""

from __future__ import annotations

import json
import re
import sys
from collections import Counter
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote, urlsplit


ROOT = Path(__file__).resolve().parents[2]
TEXT_SUFFIXES = {".css", ".html", ".js", ".json", ".md", ".txt", ".xml", ".yml", ".yaml"}
SKIPPED_SCHEMES = {"data", "http", "https", "javascript", "mailto", "sms", "tel"}
MAILCHIMP_ACTION = (
    "https://myghostheart.us22.list-manage.com/subscribe/post"
    "?u=a7ab330423f3b936c48b8d8ba&id=880e8056a6&f_id=00bec2e1f0"
)
LEGACY_REDIRECTS = {
    "ghostheart-website/index.html": "../index.html",
    "ghostheart-website/human-too.html": "../GhostHeart_Songs.html#human-too",
    "ghostheart-website/join.html": "../index.html#join-the-signal",
    "ghostheart-website/music.html": "../GhostHeart_Songs.html",
    "ghostheart-website/projects.html": "../GhostHeart_Projects.html",
    "ghostheart-website/quotes.html": "../GhostHeart_Quotes.html",
    "ghostheart-website/resources.html": "../GhostHeart_Resources.html",
    "ghostheart-website/story.html": "../GhostHeart_Story.html",
    "ghostheart-website/videos.html": "../GhostHeart_Videos.html",
}


class PageParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.ids: list[str] = []
        self.refs: list[str] = []
        self.h1_count = 0
        self.title_count = 0
        self.meta_description = False
        self.viewport = False
        self.charset = False
        self.images_missing_alt = 0
        self.unsafe_blank_links = 0
        self.autoplay_media = 0

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        values = {name.lower(): (value or "") for name, value in attrs}
        tag = tag.lower()
        if values.get("id"):
            self.ids.append(values["id"])
        for name in ("href", "src", "poster"):
            if values.get(name):
                self.refs.append(values[name])
        if tag == "h1":
            self.h1_count += 1
        elif tag == "title":
            self.title_count += 1
        elif tag == "meta":
            self.charset = self.charset or bool(values.get("charset"))
            meta_name = values.get("name", "").lower()
            if meta_name == "description" and values.get("content", "").strip():
                self.meta_description = True
            if meta_name == "viewport":
                self.viewport = True
        elif tag == "img" and "alt" not in values:
            self.images_missing_alt += 1
        elif tag == "a" and values.get("target", "").lower() == "_blank":
            rel = set(values.get("rel", "").lower().split())
            if not ({"noopener", "noreferrer"} & rel):
                self.unsafe_blank_links += 1
        elif tag in {"audio", "video"} and "autoplay" in values:
            self.autoplay_media += 1


def local_target(source: Path, reference: str) -> tuple[Path | None, str]:
    parts = urlsplit(reference.strip())
    if parts.scheme.lower() in SKIPPED_SCHEMES or parts.netloc:
        return None, unquote(parts.fragment)
    path_text = unquote(parts.path)
    if not path_text:
        return source, unquote(parts.fragment)
    candidate = ROOT / path_text.lstrip("/") if path_text.startswith("/") else source.parent / path_text
    candidate = candidate.resolve()
    try:
        candidate.relative_to(ROOT)
    except ValueError:
        return Path("__ESCAPES_ROOT__"), unquote(parts.fragment)
    if candidate.is_dir():
        candidate /= "index.html"
    return candidate, unquote(parts.fragment)


def main() -> int:
    errors: list[str] = []
    warnings: list[str] = []
    required = {
        ".nojekyll",
        "404.html",
        "CNAME",
        "favicon.ico",
        "index.html",
        "robots.txt",
        "site.webmanifest",
        "sitemap.xml",
        "GhostHeart_Songs.html",
        "GhostHeart_Story.html",
        "GhostHeart_Videos.html",
        *LEGACY_REDIRECTS,
    }
    for relative in sorted(required):
        if not (ROOT / relative).is_file():
            errors.append(f"Missing required file: {relative}")

    files = [path for path in ROOT.rglob("*") if path.is_file() and ".git" not in path.parts]
    public_files = [path for path in files if ".github" not in path.parts]
    total_bytes = sum(path.stat().st_size for path in public_files)
    if total_bytes > 1024**3:
        errors.append(f"Published tree exceeds 1 GiB: {total_bytes / 1024**2:.1f} MiB")
    for path in public_files:
        size = path.stat().st_size
        relative = path.relative_to(ROOT).as_posix()
        if size > 100 * 1024**2:
            errors.append(f"File exceeds GitHub's 100 MiB hard limit: {relative} ({size / 1024**2:.1f} MiB)")
        elif size > 50 * 1024**2:
            warnings.append(f"Large-file warning: {relative} ({size / 1024**2:.1f} MiB)")

    for path in files:
        if path.suffix.lower() not in TEXT_SUFFIXES:
            continue
        text = path.read_text(encoding="utf-8")
        if re.search(r"^(<<<<<<<|=======|>>>>>>>)", text, re.MULTILINE):
            errors.append(f"Unresolved merge marker: {path.relative_to(ROOT).as_posix()}")

    html_files = sorted(path for path in ROOT.rglob("*.html") if ".git" not in path.parts)
    page_ids: dict[Path, set[str]] = {}
    page_refs: list[tuple[Path, str]] = []
    for page in html_files:
        parser = PageParser()
        parser.feed(page.read_text(encoding="utf-8"))
        relative = page.relative_to(ROOT).as_posix()
        page_ids[page.resolve()] = set(parser.ids)
        page_refs.extend((page, reference) for reference in parser.refs)
        duplicates = [item for item, count in Counter(parser.ids).items() if count > 1]
        if parser.title_count != 1:
            errors.append(f"Expected one title element in {relative}; found {parser.title_count}")
        if parser.h1_count != 1:
            errors.append(f"Expected one h1 in {relative}; found {parser.h1_count}")
        if not parser.meta_description:
            errors.append(f"Missing meta description: {relative}")
        if not parser.viewport:
            errors.append(f"Missing viewport metadata: {relative}")
        if not parser.charset:
            errors.append(f"Missing charset metadata: {relative}")
        if duplicates:
            errors.append(f"Duplicate IDs in {relative}: {', '.join(duplicates)}")
        if parser.images_missing_alt:
            errors.append(f"Images missing alt text in {relative}: {parser.images_missing_alt}")
        if parser.unsafe_blank_links:
            errors.append(f"Unsafe target=_blank links in {relative}: {parser.unsafe_blank_links}")
        if parser.autoplay_media:
            errors.append(f"Autoplay media found in {relative}: {parser.autoplay_media}")

    for source, reference in page_refs:
        target, fragment = local_target(source, reference)
        relative = source.relative_to(ROOT).as_posix()
        if target is None:
            continue
        if target == Path("__ESCAPES_ROOT__"):
            errors.append(f"Reference escapes the site root in {relative}: {reference}")
            continue
        if not target.is_file():
            errors.append(f"Missing local target in {relative}: {reference}")
            continue
        if fragment and target.suffix.lower() == ".html":
            target_ids = page_ids.get(target.resolve())
            if target_ids is None:
                target_parser = PageParser()
                target_parser.feed(target.read_text(encoding="utf-8"))
                target_ids = set(target_parser.ids)
                page_ids[target.resolve()] = target_ids
            if fragment not in target_ids:
                errors.append(f"Missing fragment #{fragment} referenced by {relative}")

    for stylesheet in ROOT.rglob("*.css"):
        text = stylesheet.read_text(encoding="utf-8")
        for match in re.finditer(r"url\(\s*['\"]?([^)'\"]+)", text, re.IGNORECASE):
            target, _ = local_target(stylesheet, match.group(1))
            if target is not None and not target.is_file():
                errors.append(
                    f"Missing CSS asset in {stylesheet.relative_to(ROOT).as_posix()}: {match.group(1)}"
                )

    if (ROOT / "CNAME").read_text(encoding="utf-8").strip() != "www.myghostheart.com":
        errors.append("CNAME must contain exactly www.myghostheart.com")
    try:
        json.loads((ROOT / "site.webmanifest").read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        errors.append(f"Invalid site.webmanifest: {exc}")
    robots = (ROOT / "robots.txt").read_text(encoding="utf-8")
    if "https://www.myghostheart.com/sitemap.xml" not in robots:
        errors.append("robots.txt does not identify the production sitemap")

    homepage = (ROOT / "index.html").read_text(encoding="utf-8")
    decoded_homepage = homepage.replace("&amp;", "&")
    if MAILCHIMP_ACTION not in decoded_homepage:
        errors.append("Homepage is missing the approved Mailchimp form action")
    if not re.search(r'<input\b[^>]*\bname=["\']EMAIL["\'][^>]*\brequired\b', homepage, re.IGNORECASE):
        errors.append("Mailchimp email input must be required")
    if 'name="b_a7ab330423f3b936c48b8d8ba_880e8056a6"' not in homepage:
        errors.append("Mailchimp honeypot field is missing")

    for relative, destination in LEGACY_REDIRECTS.items():
        text = (ROOT / relative).read_text(encoding="utf-8")
        expected = f'content="0; url={destination}"'
        if expected not in text:
            errors.append(f"Legacy redirect mismatch in {relative}; expected {destination}")

    songs = (ROOT / "GhostHeart_Songs.html").read_text(encoding="utf-8")
    if 'id="human-too"' not in songs:
        errors.append("Human Too deep-link target is missing")
    if "hasArchiveTarget" not in songs:
        errors.append("Music archive does not reveal deep-linked releases")

    for warning in warnings:
        print(f"WARNING: {warning}")
    if errors:
        for error in errors:
            print(f"ERROR: {error}", file=sys.stderr)
        print(f"FAIL: {len(errors)} validation error(s)", file=sys.stderr)
        return 1

    print(
        "PASS: "
        f"{len(html_files)} HTML pages, {len(public_files)} published files, "
        f"{total_bytes / 1024**2:.1f} MiB, 0 validation errors"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
