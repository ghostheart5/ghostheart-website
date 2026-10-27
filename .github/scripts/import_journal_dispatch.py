#!/usr/bin/env python3
"""Validate one approved Power Automate journal payload and add it idempotently."""
import argparse
from datetime import datetime, timezone
import json
import os
from pathlib import Path
import re
from urllib.parse import urlparse

ROOT = Path(__file__).resolve().parents[2]
SOURCE_PATH = ROOT / '.github/content/journal.json'
SLUG = re.compile(r'^[a-z0-9]+(?:-[a-z0-9]+)*$')
REQUIRED = {
    'slug', 'title', 'category', 'published', 'summary', 'image', 'paragraphs', 'links'
}
ALLOWED = REQUIRED | {'sources', 'status'}


def arguments():
    parser = argparse.ArgumentParser()
    parser.add_argument('--input', help='JSON file. Defaults to GHOSTHEART_JOURNAL_POST_JSON.')
    parser.add_argument('--now', help='ISO 8601 validation time. Defaults to current UTC time.')
    return parser.parse_args()


def parse_time(value, field):
    parsed = datetime.fromisoformat(value.replace('Z', '+00:00'))
    if parsed.tzinfo is None:
        raise ValueError(f'{field} must include a timezone')
    return parsed


def nonempty_text(value, field):
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f'{field} must be a non-empty string')
    if '\x00' in value:
        raise ValueError(f'{field} contains a null character')


def validate(post, now):
    if not isinstance(post, dict):
        raise ValueError('Journal payload must be one JSON object')
    missing = REQUIRED - post.keys()
    extra = post.keys() - ALLOWED
    if missing:
        raise ValueError(f'Missing fields: {", ".join(sorted(missing))}')
    if extra:
        raise ValueError(f'Unsupported fields: {", ".join(sorted(extra))}')

    for field in ('slug', 'title', 'category', 'published', 'summary', 'image'):
        nonempty_text(post[field], field)
    if not SLUG.fullmatch(post['slug']):
        raise ValueError('slug must contain lowercase letters, numbers, and single hyphens only')

    status = post.get('status', 'approved')
    if status not in {'approved', 'published'}:
        raise ValueError('A dispatch may publish only an approved post')
    publish_at = parse_time(post['published'], 'published')
    if publish_at > now:
        raise ValueError('The approved publication time has not arrived yet')

    if not post['image'].startswith('/') or post['image'].startswith('//'):
        raise ValueError('image must be a root-relative path to an existing public site asset')
    image = (ROOT / post['image'].lstrip('/')).resolve()
    if ROOT not in image.parents or not image.is_file():
        raise ValueError(f'Journal image does not exist in the website: {post["image"]}')

    if not isinstance(post['paragraphs'], list) or not post['paragraphs']:
        raise ValueError('paragraphs must be a non-empty list')
    for index, paragraph in enumerate(post['paragraphs']):
        nonempty_text(paragraph, f'paragraphs[{index}]')

    if not isinstance(post['links'], list) or not post['links']:
        raise ValueError('links must be a non-empty list')
    for index, link in enumerate(post['links']):
        if not isinstance(link, dict) or set(link) != {'label', 'url'}:
            raise ValueError(f'links[{index}] must contain exactly label and url')
        nonempty_text(link['label'], f'links[{index}].label')
        nonempty_text(link['url'], f'links[{index}].url')
        parsed = urlparse(link['url'])
        if not (link['url'].startswith('/') or parsed.scheme == 'https'):
            raise ValueError(f'links[{index}].url must be root-relative or HTTPS')

    sources = post.get('sources', [])
    if not isinstance(sources, list):
        raise ValueError('sources must be a list when provided')
    for index, source in enumerate(sources):
        nonempty_text(source, f'sources[{index}]')

    normalized = dict(post)
    normalized['status'] = 'published'
    return normalized


def github_output(name, value):
    output_path = os.environ.get('GITHUB_OUTPUT')
    if output_path:
        with open(output_path, 'a', encoding='utf-8') as output:
            output.write(f'{name}={value}\n')


args = arguments()
if args.input:
    incoming = json.loads(Path(args.input).read_text(encoding='utf-8'))
else:
    raw = os.environ.get('GHOSTHEART_JOURNAL_POST_JSON')
    if not raw:
        raise ValueError('No journal payload was provided')
    incoming = json.loads(raw)

now = parse_time(args.now, '--now') if args.now else datetime.now(timezone.utc)
post = validate(incoming, now)
posts = json.loads(SOURCE_PATH.read_text(encoding='utf-8'))
existing = next((item for item in posts if item.get('slug') == post['slug']), None)

if existing:
    comparable = dict(existing)
    comparable['status'] = comparable.get('status', 'published')
    if comparable != post:
        raise ValueError(f'Journal slug already exists with different content: {post["slug"]}')
    github_output('changed', 'false')
    github_output('slug', post['slug'])
    print(f'No change: {post["slug"]} is already published with identical content.')
else:
    posts.append(post)
    SOURCE_PATH.write_text(
        json.dumps(posts, ensure_ascii=False, indent=2) + '\n',
        encoding='utf-8',
        newline='\n',
    )
    github_output('changed', 'true')
    github_output('slug', post['slug'])
    print(f'Added approved journal entry: {post["slug"]}')
