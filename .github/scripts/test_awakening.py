"""Offline checks for source preservation and public/draft boundaries."""
import copy
import importlib.util
import json
from pathlib import Path
import tempfile
import unittest

spec = importlib.util.spec_from_file_location('awakening', Path(__file__).with_name('build_awakening.py'))
app = importlib.util.module_from_spec(spec)
spec.loader.exec_module(app)


class CampaignTests(unittest.TestCase):
    def setUp(self):
        self.data = json.loads(app.MANIFEST.read_text(encoding='utf-8'))

    def test_exact_sequence_and_source_association(self):
        sections = app.validate(self.data)
        self.assertEqual(sections[0]['source_key'], 'cruel')
        self.assertEqual(sections[3]['source_key'], 'wife')
        self.assertTrue(all(section['source_name'] is None and section['source_sha256'] is None for section in sections))
        self.data['sections'][2]['title'] = "Papa Didn't Raise No Fool"
        with self.assertRaises(ValueError):
            app.validate(self.data)

    def test_public_build_does_not_read_drafts_or_emit_empty_articles(self):
        with tempfile.TemporaryDirectory() as temp:
            pages = app.build(Path(temp), self.data)
            self.assertEqual(set(pages), {'awakening/index.html', 'story/how-we-got-here.html'})
            html = (Path(temp) / 'awakening/index.html').read_text(encoding='utf-8')
            for section in self.data['sections']:
                self.assertNotIn('href="' + section['route'] + '"', html)
            self.assertNotIn('Private local review', html)
            self.assertNotIn('No manuscript yet', html)
            self.assertIn('url=/GhostHeart_Story.html', html)
            self.assertNotIn(app.SUNDAY, html)
            self.assertNotIn('<iframe', html)
            self.assertNotIn('<audio', html)

    def test_wife_cannot_skip_unapproved_opening(self):
        sections = self.data['sections']
        sections[3].update(status='approved', ready=True, approval='synthetic test approval', source_sha256='synthetic-test-source-hash')
        self.assertEqual(app.public_sections(app.validate(self.data)), [])
        sections[0].update(status='approved', ready=True, approval='synthetic test approval', source_sha256='synthetic-test-source-hash')
        self.assertEqual([s['number'] for s in app.public_sections(sections)], [1])

    def test_ready_does_not_grant_approval(self):
        self.data['sections'][0]['ready'] = True
        with self.assertRaises(ValueError):
            app.validate(self.data)

    def test_source_change_blocks_rendering(self):
        with tempfile.TemporaryDirectory() as temp:
            source = Path(temp) / 'changed.md'
            source.write_text('Changed prose', encoding='utf-8')
            with self.assertRaises(ValueError):
                app.manuscript(self.data['sections'][0], {'cruel': {'path': str(source), 'sha256': 'bad'}})

    def test_preview_cannot_write_into_public_tree(self):
        for output in [app.ROOT, app.ROOT / 'drafts', app.ROOT.parent]:
            with self.assertRaises(ValueError):
                app.build(output, self.data, preview=True)

    def test_stale_article_blocks_public_build(self):
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / 'awakening/cruel.html'
            path.parent.mkdir()
            path.write_text('preserve this draft', encoding='utf-8')
            with self.assertRaises(ValueError):
                app.build(Path(temp), self.data)
            self.assertEqual(path.read_text(), 'preserve this draft')

    def test_preview_navigation_is_exact(self):
        sections = self.data['sections']
        # Use unwritten sections to verify navigation without touching personal sources.
        for index in [1, 2, 4, 5, 6, 7]:
            body = app.section_body(sections[index], sections, {}, True)
            self.assertIn('rel="prev" href="' + sections[index-1]['route'] + '"', body)
            if index < 7:
                self.assertIn('rel="next" href="' + sections[index+1]['route'] + '"', body)
            else:
                self.assertNotIn('rel="next"', body)


if __name__ == '__main__':
    unittest.main()
