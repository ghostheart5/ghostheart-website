# GhostHeart Journal

The live journal is `/journal/`; its RSS 2.0 feed is `/journal/feed.xml`.

To add an approved entry, edit `.github/content/journal.json`, using a unique permanent slug, an ISO 8601 publication timestamp with timezone, an existing local image, and approved text. `published` is the journal entry's publication date, not a song's release date. Preserve existing slugs and timestamps so feed readers do not treat older entries as new.

Run `python .github/scripts/build_journal.py`, then `python .github/scripts/validate_site.py`. Commit the source and generated pages/feed together. Add new article URLs to `sitemap.xml`. Website checks regenerate the journal and fail if committed output differs from the source.

The generator reuses the homepage header/footer with root-relative links and emits RSS, canonical links, social metadata, and BlogPosting structured data. The initial entries reuse text and assets already published on the site. Their `sources` fields record where that material came from; they are not rendered to visitors.

Metricool is connected to the RSS URL. Adding entries does not itself authorize social posting or create a publishing schedule.
