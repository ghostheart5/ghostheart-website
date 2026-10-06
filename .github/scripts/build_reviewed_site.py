#!/usr/bin/env python3
"""Apply the owner-reviewed Story, Music, Readings, Projects and support pages.

Runs after the existing gateway build so its library and legacy routes remain.
The reviewed inputs live in this repository and are safe for repeat builds.
"""

from pathlib import Path
import runpy
import shutil

ROOT = Path(__file__).resolve().parents[2]
TEMPLATES = ROOT / ".github/reviewed-pages"
INPUTS = ROOT / ".github/reviewed-inputs"

# The gateway builder updates its journal source and script. Restore the reviewed
# four-entry archive before building the approved pages.
for relative in ("content/journal.json", "scripts/build_journal.py"):
    shutil.copyfile(INPUTS / relative, ROOT / ".github" / relative)

for template in sorted(TEMPLATES.rglob("*.html.template")):
    relative = Path(str(template.relative_to(TEMPLATES)).removesuffix(".template"))
    if relative.as_posix() == "journal/how-we-got-here-archive.html":
        continue  # The Journal builder prunes unpublished pages; restore below.
    output = ROOT / relative
    output.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(template, output)

for name in (
    "build_awakening.py",
    "build_music.py",
    "build_readings.py",
    "build_projects.py",
    "build_journal.py",
    "build_navigation.py",
):
    runpy.run_path(str(ROOT / ".github/scripts" / name), run_name="__main__")

archive = ROOT / "journal/how-we-got-here-archive.html"
shutil.copyfile(TEMPLATES / "journal/how-we-got-here-archive.html.template", archive)
print("Applied owner-reviewed pages after preserving the existing gateway archive.")
