# Passages content

One file per Passage. The site build (`.github/scripts/build_passages.py`) reads these files.

- `status: draft` (default): the Passage shows as locked with its date. Its text is never published.
- `status: ready`: published as `/passages/<slug>.html` once its `date` has passed at build time.
  Before the date it stays locked.
- `link:` instead of text sends readers to an existing page (Passage 01 links to the Cruel Blog entry).

Format: YAML-style header between `---` lines (`number`, `title`, `date`, `status`, `audio`, `teaser`),
then the reading. Blank line between paragraphs; `> ` starts a pull-quote paragraph. Plain text only:
`<`, `>` and `&` are escaped, no HTML.

The scheduled workflow `.github/workflows/passages-release.yml` rebuilds the site every Saturday at
7 PM Central (it runs at both possible UTC times so daylight saving changes don't matter) and commits
any Passage that just went live.

Owner rule: a reading goes out only when it is complete. Mark it `ready` only then.
